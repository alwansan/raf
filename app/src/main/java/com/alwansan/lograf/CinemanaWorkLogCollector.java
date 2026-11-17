package com.alwansan.lograf;

import android.content.ContentResolver;
import android.database.Cursor;
import android.net.Uri;
import android.os.ParcelFileDescriptor;
import android.provider.DocumentsContract;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Opt-in, READ-ONLY SAF mirror for Cinemana/work/log.
 * Uses a bounded per-poll IO budget and seeks to incremental offsets, avoiding
 * periodic multi-gigabyte rescans. Never edits or deletes source documents.
 */
public final class CinemanaWorkLogCollector implements Runnable {
    public interface Listener {
        void onNewFile(Uri file);
        void onIssue(String message);
        default void onAudit(org.json.JSONObject summary) {}
    }
    private static final long SEGMENT_LIMIT=16L*1024L*1024L;
    private static final int CHUNK_LIMIT=256*1024;
    private static final int MAX_FILES_PER_POLL=20;
    private final ContentResolver resolver;
    private final Uri selectedTree, sessionDir;
    private final AtomicBoolean active;
    private final Listener listener;
    private final HashMap<String,Long> offsets=new HashMap<>();
    private int part=0,scanStart=0;
    private long segmentBytes=0,bytesCopied=0,lastAuditTime=0;
    private OutputStream stream;
    private boolean warningAlreadySent=false;
    private final byte[] buffer=new byte[32768];

    CinemanaWorkLogCollector(ContentResolver resolver, Uri selectedTree,
            Uri sessionDir,AtomicBoolean active,Listener listener) {
        this.resolver=resolver;
        this.selectedTree=selectedTree;
        this.sessionDir=sessionDir;
        this.active=active;
        this.listener=listener;
    }

    @Override public void run(){
        try {
            while(active.get() && !Thread.currentThread().isInterrupted()) {
                try{scanOnce();}
                catch(Exception e){warnOnce("Cinemana work/log read unavailable: "+e.getClass().getSimpleName());}
                try{Thread.sleep(8000);}
                catch(InterruptedException e){Thread.currentThread().interrupt();break;}
            }
        } finally {
            if(stream!=null)try{stream.flush();stream.close();}catch(Exception ignored){}
        }
    }

    private static final class Item {
        String id,name,mime;
        long size,modified;
        Item(String id,String name,String mime,long size,long modified){
            this.id=id;this.name=name;this.mime=mime;this.size=size;this.modified=modified;
        }
    }

    private Uri documentUri(String id){
        return DocumentsContract.buildDocumentUriUsingTree(selectedTree,id);
    }
    private List<Item> children(Uri folder) throws IOException {
        ArrayList<Item> files=new ArrayList<>();
        Uri children=DocumentsContract.buildChildDocumentsUriUsingTree(
                selectedTree,DocumentsContract.getDocumentId(folder));
        String[] cols={DocumentsContract.Document.COLUMN_DOCUMENT_ID,
                DocumentsContract.Document.COLUMN_DISPLAY_NAME,
                DocumentsContract.Document.COLUMN_MIME_TYPE,
                DocumentsContract.Document.COLUMN_SIZE,
                DocumentsContract.Document.COLUMN_LAST_MODIFIED};
        try(Cursor cursor=resolver.query(children,cols,null,null,null)){
            if(cursor==null)throw new IOException("SAF query returned null");
            int id=0,name=1,mime=2,size=3;
            while(cursor.moveToNext()){
                if(files.size()>=4000){warnOnce("Folder has >4000 entries; narrow selection to Cinemana/work/log");break;}
                files.add(new Item(cursor.getString(id),cursor.getString(name),
                        cursor.getString(mime),cursor.isNull(size)?-1:cursor.getLong(size),
                        cursor.isNull(4)?-1:cursor.getLong(4)));
            }
        }
        return files;
    }

    private boolean isReadableLog(Item i){
        if(i.name==null || i.id==null || i.mime==null ||
                DocumentsContract.Document.MIME_TYPE_DIR.equals(i.mime))return false;
        String n=i.name.toLowerCase(Locale.ROOT);
        // The user selects the log directory, not the entire work/media tree.
        return (n.endsWith(".log") || n.endsWith(".jsonl") || n.equals("tree.txt")) &&
                !n.endsWith(".zip");
    }

    private void scanOnce() throws IOException {
        if(StorageAccess.file(selectedTree)){scanDirect();return;}
        Uri root=DocumentsContract.buildDocumentUriUsingTree(selectedTree,
                DocumentsContract.getTreeDocumentId(selectedTree));
        List<Item> entries=children(root);
        if(System.currentTimeMillis()-lastAuditTime>=30000){
            lastAuditTime=System.currentTimeMillis();
            auditRootMetadata(entries);
        }
        for(Item i:entries){
            if(i.name!=null && i.name.equals("log") &&
                    DocumentsContract.Document.MIME_TYPE_DIR.equals(i.mime)){
                root=documentUri(i.id);
                entries=children(root);
                break;
            }
        }
        ArrayList<Item> files=new ArrayList<>();
        for(Item item:entries)if(isReadableLog(item))files.add(item);
        if(files.isEmpty())return;
        files.sort(Comparator.comparing(i->i.name.toLowerCase(Locale.ROOT)));
        int start=scanStart%files.size(),count=Math.min(MAX_FILES_PER_POLL,files.size());
        for(int j=0;j<count && active.get();j++){
            Item item=files.get((start+j)%files.size());
            copyTail(item);
        }
        scanStart=(start+count)%files.size();
    }

    private final Map<String,String> directIdentity=new HashMap<>();
    private final Map<String,Uri> directOutputs=new HashMap<>();
    private final Map<String,Integer> directParts=new HashMap<>();
    private long directLastCensus=0;
    private void scanDirect() throws IOException {
        File root=StorageAccess.WORK.getCanonicalFile(), log=new File(root,"log").getCanonicalFile();
        if(!log.getPath().startsWith(root.getPath()+File.separator))throw new IOException("Unexpected log path");
        if(!root.isDirectory()){warnOnce("Cinemana/work not yet created; recording continues");return;}
        long now=android.os.SystemClock.elapsedRealtime();
        if(now-directLastCensus>=30000 || directLastCensus==0){
            directLastCensus=now;
            censusDirect(root);
        }
        File[] entries=log.listFiles();
        if(entries==null)return;
        Arrays.sort(entries,Comparator.comparing(File::getName));
        ArrayList<File> allowed=new ArrayList<>();
        for(File f:entries){
            String n=f.getName().toLowerCase(Locale.ROOT);
            if(f.isFile() && (n.endsWith(".log")||n.endsWith(".jsonl")||n.equals("tree.txt")) && f.getCanonicalFile().getParentFile().equals(log))allowed.add(f);
            if(allowed.size()>=4000)break;
        }
        if(allowed.isEmpty())return;
        int start=scanStart%allowed.size(),count=Math.min(MAX_FILES_PER_POLL,allowed.size());
        int budget=1024*1024;
        for(int i=0;i<count&&budget>0&&active.get();i++){
            File f=allowed.get((start+i)%allowed.size());
            try{budget-=directTail(f,Math.min(budget,CHUNK_LIMIT));}catch(Exception e){warnOnce("Direct log tail unavailable: "+e.getClass().getSimpleName());}
        }
        scanStart=(start+count)%allowed.size();
    }
    private int directTail(File f,int budget)throws Exception{
        String key=f.getName(), identity;
        try{android.system.StructStat stat=android.system.Os.stat(f.getPath());identity=stat.st_dev+":"+stat.st_ino;}catch(Exception e){identity=key;}
        long offset=offsets.getOrDefault(key,0L);
        if(!identity.equals(directIdentity.get(key))||f.length()<offset){offset=0;directOutputs.remove(key);directIdentity.put(key,identity);offsets.put(key,0L);}
        if(f.length()==offset)return 0;
        int copied=0;
        try(RandomAccessFile in=new RandomAccessFile(f,"r")){
            in.seek(offset);
            while(budget>0&&active.get()){
                int n=in.read(buffer,0,Math.min(buffer.length,budget));if(n<=0)break;
                Uri dest=directOutputs.get(key);
                if(dest==null || StorageAccess.outputFile(dest).length()+n>SEGMENT_LIMIT){
                    int part=directParts.getOrDefault(key,0)+1;directParts.put(key,part);
                    String safe=key.replaceAll("[^a-zA-Z0-9._-]","_");
                    dest=StorageAccess.create(resolver,sessionDir,"application/octet-stream",String.format(Locale.US,"internal-%s-%08x-%04d.raw",safe,key.hashCode(),part));
                    directOutputs.put(key,dest);listener.onNewFile(dest);
                }
                try(OutputStream out=new FileOutputStream(StorageAccess.outputFile(dest),true)){out.write(buffer,0,n);}
                offset+=n;offsets.put(key,offset);copied+=n;budget-=n;
            }
        }
        return copied;
    }
    private void censusDirect(File root){
        try{
            long begin=android.os.SystemClock.elapsedRealtime(),files=0,dirs=0,empty=0,mp4=0,mkv=0,part=0,temp=0,subs=0,mp4Bytes=0,mkvBytes=0,partBytes=0,tempBytes=0,oldest=Long.MAX_VALUE;
            long limit=begin+600;boolean capped=false;
            ArrayDeque<File> q=new ArrayDeque<>();q.add(root);
            while(!q.isEmpty()&&active.get()){
                if(files+dirs>=20000||android.os.SystemClock.elapsedRealtime()>limit){capped=true;break;}
                File dir=q.removeFirst();File[] entries=dir.listFiles();dirs++;
                if(entries==null){capped=true;continue;}if(entries.length==0)empty++;
                for(File f:entries){
                    if(files+dirs>=20000||android.os.SystemClock.elapsedRealtime()>limit){capped=true;break;}
                    if(!f.getCanonicalPath().startsWith(root.getPath()+File.separator)||!f.getCanonicalFile().equals(f.getAbsoluteFile()))continue;
                    if(f.isDirectory()){if(!f.getName().equals("log")&&q.size()<2000)q.add(f);else if(!f.getName().equals("log"))capped=true;continue;}
                    if(!f.isFile())continue;files++;
                    String n=f.getName().toLowerCase(Locale.ROOT);long len=f.length();
                    if(n.endsWith(".mp4")){mp4++;mp4Bytes+=len;if(f.lastModified()>0)oldest=Math.min(oldest,f.lastModified());}
                    else if(n.endsWith(".mkv")){mkv++;mkvBytes+=len;}
                    else if(n.endsWith(".part")){part++;partBytes+=len;}
                    else if(n.endsWith(".temp")){temp++;tempBytes+=len;}
                    else if(n.endsWith(".srt")||n.endsWith(".vtt")||n.endsWith(".ass"))subs++;
                }
            }
            org.json.JSONObject x=new org.json.JSONObject().put("timestamp_unix_ms",System.currentTimeMillis()).put("elapsed_ms",begin)
                .put("scope","Cinemana/work recursive metadata, excludes log").put("scan_capped",capped||!q.isEmpty())
                .put("scan_duration_ms",android.os.SystemClock.elapsedRealtime()-begin).put("entries_scanned",files+dirs)
                .put("directories",dirs).put("empty_directories",empty).put("mp4_files",mp4).put("mp4_bytes",mp4Bytes)
                .put("mkv_files",mkv).put("mkv_bytes",mkvBytes).put("part_files",part).put("part_bytes",partBytes)
                .put("temp_files",temp).put("temp_bytes",tempBytes).put("subtitle_files",subs)
                .put("oldest_mp4_age_ms",oldest==Long.MAX_VALUE?org.json.JSONObject.NULL:Math.max(0,System.currentTimeMillis()-oldest))
                .put("source","metadata only; extension is not completion proof");
            listener.onAudit(x);
        }catch(Exception e){warnOnce("Direct metadata audit unavailable: "+e.getClass().getSimpleName());}
    }
    private void auditRootMetadata(List<Item> files){
        // SAF *metadata only*: no reads of MP4, subtitles, .part or Room files.
        try{
            long mp4=0,mkv=0,part=0,temporary=0,subtitle=0,partBytes=0,oldParts=0,unknownDates=0;
            long now=System.currentTimeMillis();
            boolean workRoot=false;
            for(Item f:files){
                if(f.name==null || f.mime==null)continue;
                if(DocumentsContract.Document.MIME_TYPE_DIR.equals(f.mime)){
                    if(f.name.equals("log"))workRoot=true;
                    continue;
                }
                String name=f.name.toLowerCase(Locale.ROOT);
                if(name.endsWith(".mp4"))mp4++;
                else if(name.endsWith(".mkv"))mkv++;
                else if(name.endsWith(".part")){
                    part++;
                    if(f.size>0)partBytes+=f.size;
                    if(f.modified<=0)unknownDates++;
                    else if(now-f.modified>30*60*1000L)oldParts++;
                }
                else if(name.endsWith(".temp"))temporary++;
                else if(name.endsWith(".srt") || name.endsWith(".vtt"))subtitle++;
            }
            org.json.JSONObject row=new org.json.JSONObject();
            row.put("timestamp_unix_ms",now);
            row.put("scope",workRoot?"Cinemana/work root":"selected folder only");
            row.put("source","SAF metadata only; no file contents scanned for media audit");
            row.put("entries_scanned",files.size());
            row.put("mp4_files",mp4).put("mkv_files",mkv);
            row.put("part_files",part).put("part_bytes",partBytes);
            row.put("part_age_over_30min_candidates",oldParts);
            row.put("part_modification_time_unavailable",unknownDates);
            row.put("temp_files",temporary).put("subtitle_files",subtitle);
            row.put("part_age_note","Old .part timestamp does NOT prove it is abandoned; never auto-delete");
            listener.onAudit(row);
        }catch(Exception err){warnOnce("SAF metadata audit: "+err.getClass().getSimpleName());}
    }

    private void copyTail(Item item) {
        long offset=offsets.getOrDefault(item.id,0L);
        if(item.size>=0 && item.size<offset) offset=0; // original log rotated/truncated
        if(item.size==offset)return;
        Uri source=documentUri(item.id);
        try(ParcelFileDescriptor fd=resolver.openFileDescriptor(source,"r")){
            if(fd==null)throw new IOException("source fd null");
            try(FileInputStream input=new FileInputStream(fd.getFileDescriptor())){
                // On a non-seekable provider we can capture the first small
                // block but must not repeatedly read gigabytes just to skip.
                if(offset>0)input.getChannel().position(offset);
                int remaining=CHUNK_LIMIT;
                while(remaining>0 && active.get()){
                    int n=input.read(buffer,0,Math.min(buffer.length,remaining));
                    if(n<=0)break;
                    writeChunk(item.name,offset,buffer,n);
                    offset+=n;remaining-=n;
                }
                offsets.put(item.id,offset);
            }
        }catch(Exception err) {
            warnOnce("Selected work/log file cannot be tailed: "+
                    err.getClass().getSimpleName()+"; raw Logcat capture continues");
        }
    }

    private void openSegment() throws IOException {
        if(stream!=null){stream.flush();stream.close();}
        String name=String.format(Locale.US,"cinemana-internal-%05d.log",++part);
        Uri uri=StorageAccess.create(resolver,sessionDir,"text/plain",name);
        if(uri==null)throw new IOException("Cannot create work-log mirror");
        stream=StorageAccess.write(resolver,uri);
        if(stream==null)throw new IOException("Cannot open work-log mirror");
        segmentBytes=0;
        listener.onNewFile(uri);
    }

    private void writeChunk(String name,long offset,byte[] bytes,int len) throws IOException {
        // File name only, never internal SAF identifiers or credentials.
        String safeName=name.replace('\n','_').replace('\r','_');
        String marker="\n[CLOG INTERNAL FILE "+safeName+" offset="+offset+
                " bytes="+len+" captured_unix_ms="+System.currentTimeMillis()+"]\n";
        byte[] header=marker.getBytes(StandardCharsets.UTF_8);
        if(stream==null || segmentBytes+header.length+len>SEGMENT_LIMIT)openSegment();
        stream.write(header);
        stream.write(bytes,0,len);
        stream.flush(); // keep records available in case Cinemana or CLog terminates
        segmentBytes+=header.length+len;
        bytesCopied+=len;
    }

    private void warnOnce(String message){
        if(warningAlreadySent)return;
        warningAlreadySent=true;
        listener.onIssue(message);
    }
}
