package com.alwansan.raftlab;

import android.content.ContentResolver;
import android.database.Cursor;
import android.net.Uri;
import android.provider.DocumentsContract;
import org.json.JSONObject;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.List;

/** Bounded read-only SAF tree inventory. Never opens an OBB during scanning. */
public final class LocalOwnerBundleScanner {
    private static final int MAX_ENTRIES=500;
    private static final int MAX_DEPTH=8;
    private static final int MAX_JSON=128*1024;
    private static final String DIR=DocumentsContract.Document.MIME_TYPE_DIR;
    private static final String[] PROJECTION={
        DocumentsContract.Document.COLUMN_DOCUMENT_ID,
        DocumentsContract.Document.COLUMN_DISPLAY_NAME,
        DocumentsContract.Document.COLUMN_MIME_TYPE,
        DocumentsContract.Document.COLUMN_SIZE
    };
    private LocalOwnerBundleScanner() {}

    public static final class Entry {
        public final Uri uri;
        public final String name,kind;
        public final long bytes;
        Entry(Uri uri,String name,String kind,long bytes) {
            this.uri=uri;this.name=name;this.kind=kind;this.bytes=bytes;
        }
    }
    public static final class Snapshot {
        public final List<Entry> files;
        public final String report;
        Snapshot(List<Entry> files,String report){this.files=files;this.report=report;}
    }
    private static final class Folder {
        final String id,relative;
        final int depth;
        Folder(String id,String relative,int depth){this.id=id;this.relative=relative;this.depth=depth;}
    }

    public static Snapshot inspect(ContentResolver resolver,Uri tree)throws IOException {
        if(resolver==null||tree==null)throw new IOException("No selected SAF folder");
        final String root;
        try{root=DocumentsContract.getTreeDocumentId(tree);}
        catch(RuntimeException e){throw new IOException("Not a SAF document tree",e);}
        ArrayDeque<Folder> queue=new ArrayDeque<>();
        queue.add(new Folder(root,"",0));
        List<Entry> files=new ArrayList<>();
        StringBuilder report=new StringBuilder("فحص مجلدك بإذن SAF للقراءة فقط؛ النتائج أدلة ملفات لا تثبت تشغيل Raft.\n");
        int seen=0,folders=0;
        boolean truncated=false;
        while(!queue.isEmpty()) {
            Folder folder=queue.removeFirst();
            if(folder.depth>MAX_DEPTH){truncated=true;continue;}
            folders++;
            Uri children=DocumentsContract.buildChildDocumentsUriUsingTree(tree,folder.id);
            try(Cursor cursor=resolver.query(children,PROJECTION,null,null,null)){
                if(cursor==null)throw new IOException("SAF provider did not list selected folder");
                int idIndex=cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_DOCUMENT_ID);
                int nameIndex=cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_DISPLAY_NAME);
                int mimeIndex=cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_MIME_TYPE);
                int sizeIndex=cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_SIZE);
                while(cursor.moveToNext()){
                    if(++seen>MAX_ENTRIES){truncated=true;queue.clear();break;}
                    String id=cursor.getString(idIndex);
                    if(id==null)continue;
                    String name=LocalOwnerBundlePolicy.safeLabel(cursor.getString(nameIndex));
                    String mime=cursor.getString(mimeIndex);
                    if(DIR.equals(mime)){
                        if(folder.depth<MAX_DEPTH)queue.addLast(
                            new Folder(id,folder.relative+name+"/",folder.depth+1));
                        else truncated=true;
                        continue;
                    }
                    String kind=LocalOwnerBundlePolicy.kind(name,folder.relative);
                    if("UNKNOWN".equals(kind))continue;
                    long size=cursor.isNull(sizeIndex)?-1L:cursor.getLong(sizeIndex);
                    Uri document=DocumentsContract.buildDocumentUriUsingTree(tree,id);
                    files.add(new Entry(document,name,kind,size));
                }
            }catch(SecurityException e){
                throw new IOException("Cannot list this SAF folder; select files individually",e);
            }catch(IllegalArgumentException e){
                throw new IOException("SAF provider refused folder children",e);
            }
        }
        if(files.isEmpty())report.append("لم أجد الملفات المتوقعة داخل المجلد المحدد. اختر Download/logs نفسه، وليس Raft-Android-Test فقط إذا أردت جميع الحزم.\n");
        for(Entry e:files){
            report.append("• ").append(LocalOwnerBundlePolicy.arabicRole(e.kind)).append(": ")
              .append(e.name).append(" / ")
              .append(e.bytes<0?"حجم غير معروف":e.bytes+" بايت").append("\n");
            if("MANIFEST".equals(e.kind))
                report.append(manifestSummary(resolver,e.uri)).append("\n");
        }
        report.append("المجلدات ").append(folders).append("؛ الإدخالات المفحوصة ")
              .append(Math.min(seen,MAX_ENTRIES)).append(".\n");
        if(truncated)report.append("تحذير: توقّف الفحص عند حد العمق أو 500 إدخال؛ القائمة قد تكون ناقصة.\n");
        report.append("حزم T2/T3/T4 القديمة وملف BlackBox لا تُنفّذ أو تُرفع تلقائيًا. لا تُستبدل حزمة المختبر المضمنة بمجرد وجود JSON.\n");
        report.append("لحساب SHA256 اضغط زر الملف المطلوب فقط؛ قراءة OBB قد تكون بطيئة. دون قراءة رقمية لا توجد نتيجة PASS.\n");
        return new Snapshot(files,report.toString());
    }

    private static String manifestSummary(ContentResolver resolver,Uri uri) {
        try(InputStream in=resolver.openInputStream(uri)){
            if(in==null)throw new IOException("manifest unreadable");
            ByteArrayOutputStream out=new ByteArrayOutputStream();
            byte[] buf=new byte[4096];int n;int read=0;
            while((n=in.read(buf))!=-1){
                if(n==0)continue;
                read+=n;
                if(read>MAX_JSON)throw new IOException("manifest exceeds 128 KiB");
                out.write(buf,0,n);
            }
            JSONObject json=new JSONObject(new String(out.toByteArray(),StandardCharsets.UTF_8));
            String pkg=json.optString("package_name",json.optString("packageName",json.optString("package","")));
            String ver=json.optString("versionCode",json.optString("version_code",""));
            String p=pkg.isEmpty()?"غير مذكورة":("com.alwansan.raft.androidtest".equals(pkg)?"متطابقة نصيًا":"مختلفة/غير معروفة");
            String v=ver.matches("[0-9]{1,9}")?ver:"غير محدد";
            return "  manifest (غير موثّق): خانة الحزمة "+p+"؛ versionCode "+v+"؛ لا يثبت مطابقة APK/OBB.";
        }catch(Exception e){
            return "  لم تُقرأ بيانات manifest بأمان ("+
                LocalOwnerBundlePolicy.safeLabel(e.getClass().getSimpleName())+").";
        }
    }
}
