package com.alwansan.raftlab;

import android.app.Activity;
import android.content.*;
import android.database.Cursor;
import android.net.Uri;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.*;
import android.provider.*;
import android.view.*;
import android.widget.*;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.text.SimpleDateFormat;
import java.util.*;

/** Isolated Android mouse/input and data-only testpack logger; never loads code from packs. */
public final class MainActivity extends Activity {
    final int PICK_PACK=101,PICK_TREE=102,PICK_ASSET=103,SAVE_AS=104;
    final ArrayList<JSONObject> cases=new ArrayList<>();
    JSONObject selected;
    T1ComputeProbe t1Probe;
    LinearLayout entries; TextView caption,events,exportStatus,pad; EditText note; ImageView preview;
    File privateLog; Uri output; String packId="builtin-mouse",session;
    long lastMove=0;
    volatile boolean assetDigestBusy=false;
    Thread assetDigestThread;
    final ArrayList<String> recent=new ArrayList<>();
    TextView txt(String s){TextView v=new TextView(this);v.setText(s);v.setTextSize(15);v.setPadding(8,6,8,6);return v;}
    void addButton(LinearLayout p,String name,View.OnClickListener click){Button b=new Button(this);b.setText(name);b.setOnClickListener(click);p.addView(b);}
    String activeWorker(){
        String fromIntent=getIntent()==null?null:getIntent().getStringExtra("mini_worker");
        return fromIntent!=null&&fromIntent.matches("T[1-5]")?fromIntent:BuildConfig.LAB_WORKER;
    }
    int physicalMouseButtons=0,physicalMouseScrolls=0;
    void finishSharedManualMouse(){
        String id=getIntent().getStringExtra("manual_case_id");
        if(id==null||!id.matches("T4-0[1-9]"))return;
        Intent reply=new Intent();
        reply.putExtra("case_id",id);
        reply.putExtra("status",(physicalMouseButtons>0||physicalMouseScrolls>0)?"EVIDENCE_READY":"NEEDS_INPUT");
        reply.putExtra("observed","physical_button_events="+physicalMouseButtons+" scroll_events="+physicalMouseScrolls+"; see raw JSONL callbacks");
        log("manual_mouse_summary",id+" buttons="+physicalMouseButtons+" scroll="+physicalMouseScrolls);
        export();setResult(RESULT_OK,reply);finish();
    }
    void runSharedAutoCase(){
        String caseId=getIntent()==null?null:getIntent().getStringExtra("auto_case_id");
        if(caseId==null||!caseId.matches("T1-0[1-4]")||t1Probe==null)return;
        for(JSONObject x:cases)if(caseId.equals(x.optString("id"))){selected=x;break;}
        final String id=caseId;
        new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(()->{
            t1Probe.runAutomated(id,value->{
                Intent data=new Intent();
                data.putExtra("case_id",id);
                data.putExtra("observed",value);
                data.putExtra("status",value.startsWith("PASS")?"PASS":"FAIL");
                log("shared_auto_result",id+" "+value);
                setResult(RESULT_OK,data);
                finish();
            });
        },1000);
    }
    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        session=new SimpleDateFormat("yyyyMMdd-HHmmss",Locale.US).format(new Date())+"-"+SystemClock.elapsedRealtime();
        File folder=new File(getFilesDir(),"sessions");if(!folder.exists())folder.mkdirs();
        privateLog=new File(folder,"events-"+session+".jsonl");
        ScrollView sc=new ScrollView(this);LinearLayout root=new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);root.setPadding(8,8,8,20);sc.addView(root);
        root.addView(txt("RAFT MINI LAB — "+activeWorker()+" — data-only testpacks, not full Raft"));
        if("T2".equals(activeWorker())) addButton(root,"OPEN T2 REAL GLES3 WATER PASS LAB",v->startActivity(new Intent(this,T2GpuActivity.class)));
        LinearLayout tools=new LinearLayout(this);root.addView(tools);
        addButton(tools,"Pick testpack",v->filePicker(PICK_PACK,"application/json"));
        addButton(tools,"Pick folder",v->{Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
            i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);startActivityForResult(i,PICK_TREE);});
        addButton(tools,"Export logs",v->export());
        addButton(tools,"Save As",v->{Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);
            i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/x-ndjson");
            i.putExtra(Intent.EXTRA_TITLE,privateLog.getName());startActivityForResult(i,SAVE_AS);});
        exportStatus=txt("Logs saved privately; export to "+logDisplayRoot()+"...");root.addView(exportStatus);
        entries=new LinearLayout(this);entries.setOrientation(LinearLayout.VERTICAL);root.addView(entries);
        caption=txt("Select numbered test");root.addView(caption);
        LinearLayout result=new LinearLayout(this);root.addView(result);
        addButton(result,"PASS",v->finish("PASS"));addButton(result,"FAIL",v->finish("FAIL"));
        addButton(result,"UNEXPECTED",v->finish("UNEXPECTED"));
        note=new EditText(this);note.setHint("Observed result / problem; avoid private data");root.addView(note);
        LinearLayout capture=new LinearLayout(this);root.addView(capture);
        addButton(capture,"Capture ON",v->{pad.requestFocus();pad.requestPointerCapture();log("capture_request","ON");});
        addButton(capture,"Capture OFF",v->{pad.releasePointerCapture();log("capture_request","OFF");});
        pad=txt("INPUT PAD — click LEFT/RIGHT/MIDDLE, move and scroll here");
        pad.setBackgroundColor(0xffdce6fa);pad.setMinimumHeight(100);
        pad.setFocusable(true);pad.setFocusableInTouchMode(true);pad.setClickable(true);
        root.addView(pad);
        pad.setOnTouchListener((v,e)->{mouse("view_touch",e);return true;});
        pad.setOnGenericMotionListener((v,e)->{mouse("view_generic",e);return true;});
        pad.setOnCapturedPointerListener((v,e)->{mouse("captured",e);return true;});
        events=txt("INPUT EVENTS:");root.addView(events);
        addButton(root,"Pick image or file / SHA256",v->filePicker(PICK_ASSET,"*/*"));
        addButton(root,"Recover older session logs",v->recoverPreviousLog());
        String manual=getIntent()==null?null:getIntent().getStringExtra("manual_case_id");
        if(manual!=null&&manual.matches("T4-0[1-9]"))
            addButton(root,"RETURN TO TEAM LAB — save observed mouse evidence",v->finishSharedManualMouse());
        preview=new ImageView(this);preview.setAdjustViewBounds(true);root.addView(preview,new LinearLayout.LayoutParams(-1,260));
        if("T1".equals(activeWorker())) t1Probe=T1ComputeProbe.install(this,root);
        setContentView(sc);
        if(!"T1".equals(activeWorker())) try{
            for(int k=1;k<=3;k++)cases.add(new JSONObject().put("id","T4-0"+k).put("type","mouse")
                .put("title",new String[]{"uncaptured clicks and wheel","captured clicks and wheel","compare with Raft game"}[k-1])
                .put("instructions","Press LEFT/RIGHT/MIDDLE and wheel, observe captured and uncaptured callbacks")
                .put("expected","Real input event visible in JSONL; compare game bridge"));
        }catch(Exception ignored){}
        render();
        runSharedAutoCase();
        log("startup","AndroidAPI="+Build.VERSION.SDK_INT+" device="+Build.MANUFACTURER+"/"+Build.MODEL+" ABI="+Build.SUPPORTED_ABIS[0]);
    }
    void filePicker(int code,String type){Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);
        i.addCategory(Intent.CATEGORY_OPENABLE);i.setType(type);
        i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);startActivityForResult(i,code);}
    void render(){entries.removeAllViews();for(JSONObject t:cases){String id=t.optString("id"),name=t.optString("title");
        addButton(entries,id+": "+name,v->{if(assetDigestBusy){Toast.makeText(this,"Wait for SHA-256",Toast.LENGTH_SHORT).show();return;}selected=t;note.setText("");
            caption.setText("TEST "+id+"\n"+t.optString("instructions")+"\nEXPECTED: "+t.optString("expected"));
            log("test_begin",id);});}}
    void finish(String result){if(assetDigestBusy){Toast.makeText(this,"Finish after SHA-256 completes",Toast.LENGTH_SHORT).show();return;}if(selected==null){Toast.makeText(this,"Select test first",Toast.LENGTH_SHORT).show();return;}
        String n=note.getText().toString().replace('\n',' ');if(n.length()>800)n=n.substring(0,800);
        log("result",selected.optString("id")+"="+result+" observed="+n);export();}
    @Override public boolean dispatchTouchEvent(MotionEvent e){
        if((e.getSource()&InputDevice.SOURCE_MOUSE)==InputDevice.SOURCE_MOUSE)mouse("activity_touch",e);
        return super.dispatchTouchEvent(e);}
    @Override public boolean dispatchGenericMotionEvent(MotionEvent e){mouse("activity_generic",e);return super.dispatchGenericMotionEvent(e);}
    void mouse(String route,MotionEvent e){int a=e.getActionMasked();
        if((e.getSource()&InputDevice.SOURCE_MOUSE)==InputDevice.SOURCE_MOUSE){
            if(a==MotionEvent.ACTION_DOWN||a==MotionEvent.ACTION_UP||
               a==MotionEvent.ACTION_BUTTON_PRESS||a==MotionEvent.ACTION_BUTTON_RELEASE)physicalMouseButtons++;
            if(a==MotionEvent.ACTION_SCROLL)physicalMouseScrolls++;
        }
        if(a==MotionEvent.ACTION_MOVE||a==MotionEvent.ACTION_HOVER_MOVE){long t=SystemClock.elapsedRealtime();
            if(t-lastMove<120)return;lastMove=t;}
        String s="route="+route+" action="+MotionEvent.actionToString(a)+" source=0x"+Integer.toHexString(e.getSource())
           +" buttonState=0x"+Integer.toHexString(e.getButtonState())+" actionButton=0x"+Integer.toHexString(e.getActionButton())
           +" vscroll="+e.getAxisValue(MotionEvent.AXIS_VSCROLL)+" hscroll="+e.getAxisValue(MotionEvent.AXIS_HSCROLL)
           +" eventTime="+e.getEventTime()+" x="+e.getX()+" y="+e.getY()
           +" captured="+pad.hasPointerCapture();
        log("input",s);recent.add(s);if(recent.size()>10)recent.remove(0);
        if(events!=null)events.setText("INPUT EVENTS:\n"+android.text.TextUtils.join("\n",recent));}
    @Override protected void onActivityResult(int req,int status,Intent data){super.onActivityResult(req,status,data);
        if(status!=RESULT_OK||data==null||data.getData()==null)return;
        Uri uri=data.getData();
        try{
            if(req==PICK_PACK)loadPack(uri);
            if(req==PICK_TREE){int flags=data.getFlags()&Intent.FLAG_GRANT_READ_URI_PERMISSION;
                if(flags!=0)getContentResolver().takePersistableUriPermission(uri,flags);
                Uri children=DocumentsContract.buildChildDocumentsUriUsingTree(uri,DocumentsContract.getTreeDocumentId(uri));
                Uri file=null;try(Cursor c=getContentResolver().query(children,new String[]{DocumentsContract.Document.COLUMN_DISPLAY_NAME,DocumentsContract.Document.COLUMN_DOCUMENT_ID},null,null,null)){
                    if(c!=null)for(int i=0;i<200&&c.moveToNext();i++)if("testpack.json".equals(c.getString(0))){
                        file=DocumentsContract.buildDocumentUriUsingTree(uri,c.getString(1));break;}}
                if(file==null)throw new IOException("Folder has no testpack.json; pick JSON file directly");
                loadPack(file);}
            if(req==PICK_ASSET)startAssetDigest(uri);
            if(req==SAVE_AS){try(InputStream in=new FileInputStream(privateLog);OutputStream out=getContentResolver().openOutputStream(uri,"wt")){
                    if(out==null)throw new IOException("Save stream unavailable");copy(in,out);}exportStatus.setText("Log saved via picker");}
        }catch(Exception ex){log("picker_error",ex.toString());Toast.makeText(this,ex.getMessage(),Toast.LENGTH_LONG).show();}
    }
    /**
     * Multi-GiB SAF APK/OBB reads must not run in onActivityResult/UI thread.
     * A 64 MiB ceiling is retained only for image decoding, not hashing.
     */
    void startAssetDigest(Uri uri) {
        if(assetDigestBusy){Toast.makeText(this,"SHA-256 already running",Toast.LENGTH_SHORT).show();return;}
        assetDigestBusy=true;
        final String caseId=selected==null?"none":selected.optString("id");
        final boolean imageCase=selected!=null&&"image_preview".equals(selected.optString("type"));
        String displayName="selected file";
        try(Cursor c=getContentResolver().query(uri,new String[]{OpenableColumns.DISPLAY_NAME},null,null,null)){
            if(c!=null&&c.moveToFirst()&&!c.isNull(0))displayName=c.getString(0);
        }catch(Exception ignored){}
        final String fileName=displayName.replace('\n',' ').replace('\r',' ').substring(0,Math.min(128,displayName.length()));
        caption.setText("Calculating SHA-256 off the UI thread for "+fileName+"...");
        log("asset_sha256_started","case="+caseId+" file="+fileName);
        assetDigestThread=new Thread(()->{
            try(InputStream in=getContentResolver().openInputStream(uri)){
                final long started=SystemClock.elapsedRealtime();
                StreamSha256.Result r=StreamSha256.digest(in,bytes->{
                    long mb=bytes/(1024L*1024L);
                    runOnUiThread(()->caption.setText("SHA-256 reading "+fileName+": "+mb+" MiB; keep app open"));
                });
                Bitmap bitmap=null;
                if(imageCase&&r.bytes<=64L*1024*1024){
                    BitmapFactory.Options opts=new BitmapFactory.Options();opts.inJustDecodeBounds=true;
                    try(InputStream pic=getContentResolver().openInputStream(uri)){
                        if(pic!=null)BitmapFactory.decodeStream(pic,null,opts);
                    }
                    if(opts.outWidth>0&&opts.outHeight>0&&opts.outWidth<=32768&&opts.outHeight<=32768){
                        int sample=1;
                        while(opts.outWidth/sample>1600||opts.outHeight/sample>1600)sample*=2;
                        BitmapFactory.Options small=new BitmapFactory.Options();small.inSampleSize=sample;
                        small.inPreferredConfig=Bitmap.Config.RGB_565;
                        try(InputStream pic=getContentResolver().openInputStream(uri)){
                            if(pic!=null)bitmap=BitmapFactory.decodeStream(pic,null,small);
                        }
                    }
                }
                final Bitmap image=bitmap;
                final long elapsed=SystemClock.elapsedRealtime()-started;
                log("asset_sha256","case="+caseId+" file="+fileName+" bytes="+r.bytes+" sha256="+r.hex+" elapsed_ms="+elapsed);
                runOnUiThread(()->{
                    if(image!=null)preview.setImageBitmap(image);else preview.setImageDrawable(null);
                    caption.setText("File: "+fileName+"\nBytes: "+r.bytes+"\nSHA-256: "+r.hex
                        +(imageCase&&r.bytes>64L*1024*1024?"\nImage preview skipped (>64MiB)":""));
                });
            }catch(Exception ex){
                log("asset_sha256_error","case="+caseId+" error="+ex.getClass().getSimpleName()+": "+ex.getMessage());
                runOnUiThread(()->{
                    caption.setText("SHA-256 failed: "+ex.getClass().getSimpleName()+": "+ex.getMessage());
                    Toast.makeText(this,"SHA-256 failed; no digest claimed",Toast.LENGTH_LONG).show();
                });
            }finally{assetDigestBusy=false;}
        },"raft-lab-stream-sha256");
        assetDigestThread.start();
    }

    void loadPack(Uri uri)throws Exception{byte[] b=new byte[65537];int length=0;
        try(InputStream in=getContentResolver().openInputStream(uri)){if(in==null)throw new IOException("Unreadable pack");
            while(length<b.length){int n=in.read(b,length,b.length-length);if(n<0)break;length+=n;}}
        if(length>65536)throw new IOException("Pack over 64KiB");
        JSONObject p=new JSONObject(new String(b,0,length,StandardCharsets.UTF_8));
        if(p.length()!=7||p.getInt("schema_version")!=1||!p.getString("worker").matches("T[1-5]"))throw new IOException("Invalid pack schema");
        String id=p.getString("pack_id");if(!id.matches("[a-z0-9][a-z0-9._-]{0,79}"))throw new IOException("Unsafe pack id");
        if(!p.isNull("source_sha")&&!p.getString("source_sha").matches("[a-f0-9]{40}"))throw new IOException("Bad source SHA");
        JSONArray ts=p.getJSONArray("tests");if(ts.length()<1||ts.length()>20)throw new IOException("Invalid case count");
        ArrayList<JSONObject> newCases=new ArrayList<>();HashSet<String> names=new HashSet<>();
        for(int i=0;i<ts.length();i++){JSONObject t=ts.getJSONObject(i);
            String tid=t.getString("id"),type=t.getString("type");
            if(t.length()<5||t.length()>7||!tid.matches("[A-Za-z0-9][A-Za-z0-9._-]{0,63}")||!names.add(tid))throw new IOException("Invalid case");
            if(!Arrays.asList("note","mouse","file_sha256","image_preview").contains(type))throw new IOException("Executable type forbidden");
            if(t.has("asset")){String name=t.getString("asset");if(name.startsWith("/")||name.contains("\\")||name.contains("://")||name.length()>180)throw new IOException("Unsafe asset");
                for(String part:name.split("/",-1))if(part.isEmpty()||part.equals(".")||part.equals(".."))throw new IOException("Traversal");}
            if(t.has("sha256")&&!t.getString("sha256").matches("[a-f0-9]{64}"))throw new IOException("Bad asset SHA");
            for(String key:new String[]{"title","instructions","expected"})if(t.getString(key).isEmpty()||t.getString(key).length()>1500)throw new IOException("Invalid case text");
            newCases.add(t);}
        packId=id;selected=null;cases.clear();cases.addAll(newCases);render();
        caption.setText("Pack "+p.getString("title")+"; tests="+cases.size());log("pack_loaded",id+" tests="+cases.size());
    }
    void log(String kind,String info){try{JSONObject j=new JSONObject();
        j.put("unix_ms",System.currentTimeMillis());j.put("elapsed_ms",SystemClock.elapsedRealtime());
        j.put("worker",activeWorker());j.put("package",getPackageName());
        j.put("app_version",BuildConfig.VERSION_NAME);j.put("app_version_code",BuildConfig.VERSION_CODE);
        j.put("session",session);
        j.put("pack_id",packId);j.put("test_id",selected==null?JSONObject.NULL:selected.optString("id"));
        j.put("event",kind);j.put("detail",info);
        try(FileOutputStream out=new FileOutputStream(privateLog,true)){out.write((j.toString()+"\n").getBytes(StandardCharsets.UTF_8));}
        }catch(Exception ex){android.util.Log.e("RaftMiniLab","Private log failed",ex);}}
    void copy(InputStream in,OutputStream out)throws IOException{byte[] buf=new byte[16384];int n;
        while((n=in.read(buf))>=0)out.write(buf,0,n);out.flush();}
    String folder(){return (activeWorker()+"-"+packId+"-"+session).toLowerCase(Locale.US).replaceAll("[^a-z0-9._-]","-");}
    String logRelativeRoot(){return Environment.DIRECTORY_DOWNLOADS+("T1".equals(activeWorker())?"/Games/cl/raft log/test/":"/Games/cl/test/");}
    String logDisplayRoot(){return "T1".equals(activeWorker())?"Download/Games/cl/raft log/test/":"Download/Games/cl/test/";}
    void export(){log("log_export","MediaStore.Downloads");
        if(Build.VERSION.SDK_INT<29){exportStatus.setText("Use Save As for Android 9");return;}
        try{
            if(output==null){ContentValues v=new ContentValues();
                v.put(MediaStore.Downloads.DISPLAY_NAME,privateLog.getName());v.put(MediaStore.Downloads.MIME_TYPE,"application/x-ndjson");
                v.put(MediaStore.Downloads.RELATIVE_PATH,logRelativeRoot()+folder()+"/");
                output=getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,v);
                if(output==null)throw new IOException("MediaStore refused file");}
            try(InputStream in=new FileInputStream(privateLog);OutputStream out=getContentResolver().openOutputStream(output,"wt")){
                if(out==null)throw new IOException("Export stream unavailable");copy(in,out);}
            exportStatus.setText("Exported: "+logDisplayRoot()+folder()+"/"+privateLog.getName());
        }catch(Exception ex){log("export_error",ex.toString());exportStatus.setText("Export failed; private logs preserved. Use Save As.");}}

    /** Export the newest previous append-only log after an unexpected app exit. */
    void recoverPreviousLog(){
        File dir=new File(getFilesDir(),"sessions");
        File[] old=dir.listFiles((d,name)->name.startsWith("events-")&&name.endsWith(".jsonl")&&!name.equals(privateLog.getName()));
        if(old==null||old.length==0){Toast.makeText(this,"No older logs",Toast.LENGTH_SHORT).show();return;}
        File latestFile=old[0];for(File x:old)if(x.lastModified()>latestFile.lastModified())latestFile=x;
        if(Build.VERSION.SDK_INT<29){exportStatus.setText("Use Android file picker to save older log");return;}
        try{
            ContentValues values=new ContentValues();
            values.put(MediaStore.Downloads.DISPLAY_NAME,latestFile.getName());
            values.put(MediaStore.Downloads.MIME_TYPE,"application/x-ndjson");
            values.put(MediaStore.Downloads.RELATIVE_PATH,logRelativeRoot()+folder()+"-recovered/");
            Uri dest=getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,values);
            if(dest==null)throw new IOException("Download entry unavailable");
            try(InputStream in=new FileInputStream(latestFile);OutputStream out=getContentResolver().openOutputStream(dest,"wt")){
                if(out==null)throw new IOException("Log export unavailable");copy(in,out);
            }
            log("recovered_log","file="+latestFile.getName());
            exportStatus.setText("Recovered old session: "+latestFile.getName()+" in "+logDisplayRoot()+folder()+"-recovered/");
        }catch(Exception ex){log("recover_error",ex.getClass().getSimpleName());exportStatus.setText("Could not recover; private files kept");}
    }

    @Override protected void onResume(){super.onResume();if(t1Probe!=null)t1Probe.onResume();}
    @Override protected void onPause(){if(t1Probe!=null)t1Probe.onPause();super.onPause();if(pad!=null&&pad.hasPointerCapture())pad.releasePointerCapture();log("activity","pause");}
    @Override protected void onStop(){super.onStop();export();}
    @Override protected void onDestroy(){if(assetDigestThread!=null)assetDigestThread.interrupt();super.onDestroy();}
}
