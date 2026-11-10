package com.alwansan.gfx094;
import android.app.*;
import android.os.*;
import android.content.*;
import android.net.Uri;
import android.provider.MediaStore;
import android.opengl.*;
import android.widget.*;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.zip.*;
import javax.microedition.khronos.egl.EGLConfig;
import javax.microedition.khronos.opengles.GL10;

/** Compiles authentic translated source stages. Does not claim rendering/parity. */
public final class MainActivity extends Activity {
  TextView status; GLSurfaceView surface; JSONArray events=new JSONArray(); JSONObject summary=new JSONObject();
  volatile boolean complete=false; volatile boolean running=false; String lastExport="";
  int count=0,compiled=0,linked=0,failed=0; JSONObject manifest;
  String text(String asset)throws Exception {
    try(InputStream in=getAssets().open(asset);ByteArrayOutputStream out=new ByteArrayOutputStream()){
      byte[] b=new byte[32768];int n;while((n=in.read(b))!=-1)out.write(b,0,n);
      return out.toString("UTF-8");
    }
  }
  synchronized void add(JSONObject e){events.put(e);}
  void show(final String msg){runOnUiThread(new Runnable(){public void run(){status.setText(msg);}});}
  JSONObject obj(Object... pairs){JSONObject o=new JSONObject();try{for(int i=0;i<pairs.length;i+=2)o.put((String)pairs[i],pairs[i+1]);}catch(Exception e){throw new RuntimeException(e);}return o;}
  @Override public void onCreate(Bundle state){super.onCreate(state);
    getWindow().addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    LinearLayout layout=new LinearLayout(this);layout.setOrientation(LinearLayout.VERTICAL);
    status=new TextView(this);status.setTextSize(17);status.setPadding(20,12,20,12);
    status.setText("GFX094: original Shader48 stages → GLES. Compile/link only. No model/pixel parity claim.");layout.addView(status);
    Button export=new Button(this);export.setText("EXPORT ALL LOGS ZIP → Download/Games/cl/test/g/");
    export.setOnClickListener(new android.view.View.OnClickListener(){public void onClick(android.view.View v){new Thread(new Runnable(){public void run(){exportZip();}}).start();}});layout.addView(export);
    surface=new GLSurfaceView(this);surface.setEGLContextClientVersion(3);
    surface.setRenderer(new GLSurfaceView.Renderer(){
      public void onSurfaceCreated(GL10 unused,EGLConfig config){
        if(running||complete){show("EGL context recreated. Keep this app open; completed logs are retained.");return;}
        running=true;
        try{
          manifest=new JSONObject(text("probe/manifest.json"));
          summary=obj("experiment","GFX-MULTI-094","source_sha",manifest.getString("source_sha"),
             "build_source_sha",manifest.optString("build_source_sha"),"device",Build.MANUFACTURER+" "+Build.MODEL,
             "android_sdk",Build.VERSION.SDK_INT,"renderer",GLES31.glGetString(GLES31.GL_RENDERER),
             "vendor",GLES31.glGetString(GLES31.GL_VENDOR),"GL_version",GLES31.glGetString(GLES31.GL_VERSION),
             "GLSL_version",GLES31.glGetString(GLES31.GL_SHADING_LANGUAGE_VERSION),
             "originalShaderRestored",false,"phase_closed",false,"model_rendered",false,"PC_pixel_parity",false,
             "offline_counts",manifest.getJSONObject("offline_counts"),"controlled_stage_block_and_sampler_names",true,"started_ms",System.currentTimeMillis());
          int[] val=new int[1];GLES31.glGetIntegerv(GLES31.GL_MAX_UNIFORM_BUFFER_BINDINGS,val,0);summary.put("max_ubo_bindings",val[0]);
          GLES31.glGetIntegerv(GLES31.GL_MAX_VERTEX_UNIFORM_BLOCKS,val,0);summary.put("max_VS_ubo_blocks",val[0]);
          GLES31.glGetIntegerv(GLES31.GL_MAX_FRAGMENT_UNIFORM_BLOCKS,val,0);summary.put("max_FS_ubo_blocks",val[0]);
          add(obj("event","environment","data",summary));surface.requestRender();
        }catch(Exception e){add(obj("event","fatal","message",e.toString()));complete=true;new Thread(new Runnable(){public void run(){exportZip();}}).start();show("Probe initialization failed; export logs.");}
      }
      public void onSurfaceChanged(GL10 gl,int w,int h){GLES31.glViewport(0,0,w,h);}
      public void onDrawFrame(GL10 gl){
        GLES31.glClearColor(.03f,.07f,.11f,1);GLES31.glClear(GLES31.GL_COLOR_BUFFER_BIT);
        if(complete||manifest==null)return;
        try{
          JSONArray pairs=manifest.getJSONArray("pairs");
          if(count>=pairs.length()){finishProbe();return;}
          JSONObject pair=pairs.getJSONObject(count);String id=pair.getString("id");
          int vs=pair.optBoolean("vertex_available",false)?compile(id,"vert",GLES31.GL_VERTEX_SHADER):0;
          int fs=pair.optBoolean("fragment_available",false)?compile(id,"frag",GLES31.GL_FRAGMENT_SHADER):0;
          if(!pair.optBoolean("vertex_available",false)||!pair.optBoolean("fragment_available",false))
            add(obj("event","CPU_translation_unavailable","pair",id,"reason",pair.optJSONObject("CPU_translation_errors")));
          boolean ok=false;int program=0;
          if(vs!=0&&fs!=0){
            program=GLES31.glCreateProgram();GLES31.glAttachShader(program,vs);GLES31.glAttachShader(program,fs);GLES31.glLinkProgram(program);
            int[] state=new int[1];GLES31.glGetProgramiv(program,GLES31.GL_LINK_STATUS,state,0);ok=state[0]!=0;
            int[] ubos=new int[1];GLES31.glGetProgramiv(program,GLES31.GL_ACTIVE_UNIFORM_BLOCKS,ubos,0);
            add(obj("event","link","pair",id,"success",ok,"active_ubo_blocks",ubos[0],"driver_log",GLES31.glGetProgramInfoLog(program),"gl_error",GLES31.glGetError()));
          }else add(obj("event","link","pair",id,"success",false,"skipped_compile_failure",true));
          if(ok)linked++;else failed++;
          if(program!=0)GLES31.glDeleteProgram(program);if(vs!=0)GLES31.glDeleteShader(vs);if(fs!=0)GLES31.glDeleteShader(fs);
          count++;show("Original Shader48 GPU compile/link: "+count+"/"+pairs.length()+" pairs\nStages compiled: "+compiled+" | pairs linked: "+linked+" | failed: "+failed+"\nThis is a driver test; original model and pixel parity remain unverified.");
          if(count>=pairs.length())finishProbe();else surface.requestRender();
        }catch(Exception e){add(obj("event","fatal","message",e.toString()));finishProbe();}
      }
    });surface.setRenderMode(GLSurfaceView.RENDERMODE_WHEN_DIRTY);layout.addView(surface,new LinearLayout.LayoutParams(-1,0,1));setContentView(layout);
  }
  int compile(String id,String stage,int type)throws Exception{
    String source=text("probe/"+id+"."+stage);int shader=GLES31.glCreateShader(type);GLES31.glShaderSource(shader,source);GLES31.glCompileShader(shader);
    int[] val=new int[1];GLES31.glGetShaderiv(shader,GLES31.GL_COMPILE_STATUS,val,0);boolean ok=val[0]!=0;
    add(obj("event","compile","pair",id,"stage",stage,"success",ok,"driver_log",GLES31.glGetShaderInfoLog(shader),"gl_error",GLES31.glGetError(),"time_ms",System.currentTimeMillis()));
    if(ok){compiled++;return shader;}GLES31.glDeleteShader(shader);return 0;
  }
  void finishProbe(){
    if(complete)return;complete=true;running=false;
    try{summary.put("completed_pairs",count);summary.put("compiled_stages",compiled);summary.put("linked_pairs",linked);summary.put("failed_pairs",failed);summary.put("expected_pairs",manifest.getJSONArray("pairs").length());summary.put("all_pairs_tested",count==manifest.getJSONArray("pairs").length());summary.put("finished_ms",System.currentTimeMillis());}catch(Exception ignored){}
    new Thread(new Runnable(){public void run(){exportZip();}}).start();
  }
  void zipEntry(ZipOutputStream z,String name,String value)throws Exception{z.putNextEntry(new ZipEntry(name));z.write(value.getBytes(StandardCharsets.UTF_8));z.closeEntry();}
  synchronized void exportZip(){
    Uri uri=null;File file=new File(getFilesDir(),"GFX094-last-test.zip");
    try{
      try(ZipOutputStream z=new ZipOutputStream(new FileOutputStream(file))){
        zipEntry(z,"summary.json",summary.toString(2));StringBuilder log=new StringBuilder();
        for(int i=0;i<events.length();i++)log.append(events.getJSONObject(i).toString()).append('\n');zipEntry(z,"events.jsonl",log.toString());
        zipEntry(z,"LIMITS.txt","Actual original translated stages compiled/linked on device. No model draw, bound original material payload, original render state, animation or PC pixel parity is established. originalShaderRestored=false; phase_closed=false.\n");
      }
      String name="GFX094-ALL-TEST-LOGS-"+System.currentTimeMillis()+".zip";ContentValues values=new ContentValues();
      values.put(MediaStore.Downloads.DISPLAY_NAME,name);values.put(MediaStore.Downloads.MIME_TYPE,"application/zip");values.put(MediaStore.Downloads.RELATIVE_PATH,"Download/Games/cl/test/g/");values.put(MediaStore.Downloads.IS_PENDING,1);
      uri=getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,values);if(uri==null)throw new IOException("MediaStore insert failed");
      try(InputStream in=new FileInputStream(file);OutputStream out=getContentResolver().openOutputStream(uri)){if(out==null)throw new IOException("Output stream missing");byte[] buf=new byte[32768];int n;while((n=in.read(buf))!=-1)out.write(buf,0,n);}
      ContentValues done=new ContentValues();done.put(MediaStore.Downloads.IS_PENDING,0);if(getContentResolver().update(uri,done,null,null)!=1)throw new IOException("Publish failed");
      try(android.database.Cursor c=getContentResolver().query(uri,new String[]{MediaStore.Downloads.SIZE,MediaStore.Downloads.RELATIVE_PATH},null,null,null)){
        if(c==null||!c.moveToFirst()||c.getLong(0)!=file.length()||!"Download/Games/cl/test/g/".equals(c.getString(1)))throw new IOException("Published size/path verification failed");
      }
      lastExport=name;show("Test "+(complete?"finished":"snapshot")+": "+count+" pairs; "+compiled+" stages compiled; "+linked+" pairs linked; "+failed+" failed.\nLogs saved: Download/Games/cl/test/g/"+name+"\nSend this ZIP back. Shader48 restoration remains OPEN.");
    }catch(Exception e){if(uri!=null)getContentResolver().delete(uri,null,null);show("Export failed: "+e+"\nPrivate ZIP retained. Press EXPORT to retry.");}
  }
  @Override protected void onPause(){super.onPause();surface.onPause();}
  @Override protected void onResume(){super.onResume();surface.onResume();}
}
