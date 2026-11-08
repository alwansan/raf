package com.alwansan.raftlab;

import android.app.Activity;
import android.content.ContentValues;
import android.net.Uri;
import android.opengl.GLES30;
import android.opengl.GLSurfaceView;
import android.os.*;
import android.provider.MediaStore;
import android.view.*;
import android.widget.*;
import org.json.JSONObject;
import java.io.*;
import java.nio.*;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.*;

/** T2 real GLES3 controls only; no proprietary Raft shader, Unity, or assets. */
public final class T2GpuActivity extends Activity {
  static final String[] TITLES = {
    "CASE01 - GLES driver and capabilities",
    "CASE02 - two-pass RGBA8 FBO pixel roundtrip",
    "CASE03 - incomplete FBO negative control",
    "CASE04 - invalid shader compile negative control"
  };
  static final String[] EXPECTED = {
    "Real GLES3 renderer/version and maximum texture size",
    "Two complete RGBA8 FBOs, final pixel (32,96,159,255) +/-2",
    "GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT detected",
    "GL_COMPILE_STATUS=0 for deliberately invalid GLSL"
  };
  GLSurfaceView surface;
  Probe probe;
  TextView status;
  EditText notes;
  File logFile;
  Uri exported;
  String session;
  volatile int selected = -1;
  synchronized void log(String kind, String info) { logForCase(kind,info,selected); }
  synchronized void logForCase(String kind, String info, int caseId) {
    try {
      JSONObject j = new JSONObject();
      j.put("unix_ms",System.currentTimeMillis());
      j.put("elapsed_ms",SystemClock.elapsedRealtime());
      j.put("worker","T2");
      j.put("package",getPackageName());
      j.put("version","0.1.0");
      j.put("session",session);
      j.put("case",caseId<0?JSONObject.NULL:"CASE0"+(caseId+1));
      j.put("event",kind);
      j.put("detail",info);
      try(FileOutputStream out = new FileOutputStream(logFile,true)) {
        out.write((j.toString()+"\n").getBytes(StandardCharsets.UTF_8));
      }
    } catch(Exception e) { android.util.Log.e("T2GpuLab","append JSONL failed",e); }
  }
  @Override public void onCreate(Bundle b) {
    super.onCreate(b);
    session = new SimpleDateFormat("yyyyMMdd-HHmmss",Locale.US).format(new Date())
        + "-" + SystemClock.elapsedRealtime();
    File d = new File(getFilesDir(),"sessions");
    if(!d.exists() && !d.mkdirs()) throw new IllegalStateException("private log directory failed");
    logFile = new File(d,"t2-gles-"+session+".jsonl");
    ScrollView scroll = new ScrollView(this);
    LinearLayout root = new LinearLayout(this);
    root.setPadding(10,10,10,20);
    root.setOrientation(LinearLayout.VERTICAL);
    scroll.addView(root);
    TextView header = new TextView(this);
    header.setText("T2 GLES3 WATER PASS PROBE 0.1.0\nActual driver, synthetic shaders only.\nNOT proof of original Foam/Spectrum/Blur, ShaderLab or Raft.");
    header.setTextSize(17);root.addView(header);
    status = new TextView(this);status.setText("Select a numbered case");
    status.setTextSize(16);status.setPadding(8,12,8,12);root.addView(status);
    notes = new EditText(this);notes.setHint("Observed notes; no private data");root.addView(notes);
    for(int i=0;i<TITLES.length;i++){
      final int id=i;Button button=new Button(this);button.setText(TITLES[i]);
      button.setOnClickListener(v->runCase(id));root.addView(button);
    }
    LinearLayout results = new LinearLayout(this);root.addView(results);
    for(String outcome:new String[]{"PASS","FAIL","UNEXPECTED"}){
      Button bResult=new Button(this);bResult.setText(outcome);
      bResult.setOnClickListener(v->record(outcome));
      results.addView(bResult,new LinearLayout.LayoutParams(0,-2,1));
    }
    Button export=new Button(this);export.setText("EXPORT LOGS to Download/Games/cl/test");
    export.setOnClickListener(v->export());root.addView(export);
    probe = new Probe();
    surface = new GLSurfaceView(this);
    surface.setEGLContextClientVersion(3);
    surface.setEGLConfigChooser(8,8,8,8,16,0);
    surface.setRenderer(probe);
    surface.setRenderMode(GLSurfaceView.RENDERMODE_WHEN_DIRTY);
    root.addView(surface,new LinearLayout.LayoutParams(-1,160));
    setContentView(scroll);
    log("startup","api="+Build.VERSION.SDK_INT+" model="+Build.MODEL+" abi="+Build.SUPPORTED_ABIS[0]);
    surface.requestRender();
  }
  void runCase(int id) {
    selected=id;notes.setText("");
    status.setText(TITLES[id]+"\nExpected: "+EXPECTED[id]+"\nRunning on GL thread...");
    log("case_start",TITLES[id]);
    surface.queueEvent(()->{
      String result;
      try { result=probe.check(id); }
      catch(Throwable e){ result="FAIL: "+e.getClass().getSimpleName()+": "+e.getMessage(); }
      final String observed=result.length()>1200?result.substring(0,1200):result;
      logForCase("gl_observed",observed,id);
      runOnUiThread(()->{
        if(selected==id)status.setText(TITLES[id]+"\nExpected: "+EXPECTED[id]+
            "\nObserved: "+observed+"\nMark PASS/FAIL/UNEXPECTED, then export JSONL.");
      });
    });
    surface.requestRender();
  }
  void record(String outcome) {
    if(selected<0){status.setText("Select a case first");return;}
    String n=notes.getText().toString().replace('\n',' ');
    if(n.length()>800)n=n.substring(0,800);
    log("user_result","CASE0"+(selected+1)+"="+outcome+" observed_notes="+n);
    export();
  }
  void export() {
    if(Build.VERSION.SDK_INT<29){status.append("\nExport requires MediaStore (Android10+)");return;}
    try {
      if(exported==null){
        ContentValues v=new ContentValues();
        v.put(MediaStore.Downloads.DISPLAY_NAME,logFile.getName());
        v.put(MediaStore.Downloads.MIME_TYPE,"application/x-ndjson");
        v.put(MediaStore.Downloads.RELATIVE_PATH,
            Environment.DIRECTORY_DOWNLOADS+"/Games/cl/test/t2-gles-pass-"+session+"/");
        exported=getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,v);
        if(exported==null)throw new IOException("MediaStore insert returned null");
      }
      log("export","MediaStore.Downloads");
      try(InputStream in=new FileInputStream(logFile);
          OutputStream out=getContentResolver().openOutputStream(exported,"wt")){
        if(out==null)throw new IOException("MediaStore output stream null");
        byte[] buf=new byte[8192];int n;
        while((n=in.read(buf))!=-1)out.write(buf,0,n);
        out.flush();
      }
      status.append("\nExported: Download/Games/cl/test/t2-gles-pass-"+session);
    }catch(Exception e){log("export_error",e.toString());status.append("\nExport failed, private JSONL preserved");}
  }
  @Override protected void onResume(){super.onResume();if(surface!=null)surface.onResume();}
  @Override protected void onPause(){if(surface!=null)surface.onPause();log("activity","pause");super.onPause();}
  @Override protected void onStop(){log("activity","stop");export();super.onStop();}

  final class Probe implements GLSurfaceView.Renderer {
    volatile boolean ready=false;
    int surfaceWidth=1, surfaceHeight=1;
    static final String V="#version 300 es\n"
        +"void main(){float x=gl_VertexID==1?3.0:-1.0;"
        +"float y=gl_VertexID==2?3.0:-1.0;gl_Position=vec4(x,y,0.,1.);}";
    static final String F0="#version 300 es\nprecision highp float;"
        +"out vec4 col;void main(){col=vec4(0.125,0.375,0.625,1.0);}";
    static final String F1="#version 300 es\nprecision highp float;"
        +"uniform sampler2D image0;out vec4 col;"
        +"void main(){col=texture(image0,gl_FragCoord.xy/vec2(8.0));}";
    @Override public void onSurfaceCreated(javax.microedition.khronos.opengles.GL10 gl,
                              javax.microedition.khronos.egl.EGLConfig config){
      ready=true;
      log("gl_context","vendor="+GLES30.glGetString(GLES30.GL_VENDOR)+
          " renderer="+GLES30.glGetString(GLES30.GL_RENDERER)+
          " version="+GLES30.glGetString(GLES30.GL_VERSION));
    }
    @Override public void onSurfaceChanged(javax.microedition.khronos.opengles.GL10 gl,int w,int h){
      surfaceWidth=w;surfaceHeight=h;
      log("surface","w="+w+" h="+h);
    }
    @Override public void onDrawFrame(javax.microedition.khronos.opengles.GL10 gl){
      GLES30.glBindFramebuffer(GLES30.GL_FRAMEBUFFER,0);
      GLES30.glViewport(0,0,surfaceWidth,surfaceHeight);
      GLES30.glClearColor(.04f,.08f,.12f,1f);
      GLES30.glClear(GLES30.GL_COLOR_BUFFER_BIT);
    }
    String check(int id) {
      if(!ready)throw new IllegalStateException("GL context not ready");
      if(id==0){
        int[] max={0};GLES30.glGetIntegerv(GLES30.GL_MAX_TEXTURE_SIZE,max,0);
        String version=GLES30.glGetString(GLES30.GL_VERSION);
        if(version==null||!version.contains("OpenGL ES 3"))
          throw new IllegalStateException("GLES3 context missing: "+version);
        return "OK renderer="+GLES30.glGetString(GLES30.GL_RENDERER)+
            " version="+version+" maxTexture="+max[0];
      }
      if(id==1)return twoPass();
      if(id==2)return invalidFbo();
      if(id==3)return invalidShader();
      throw new IllegalArgumentException("Unknown case");
    }
    int compile(int type,String src){
      int sh=GLES30.glCreateShader(type);
      if(sh==0)throw new IllegalStateException("glCreateShader failed");
      GLES30.glShaderSource(sh,src);GLES30.glCompileShader(sh);
      int[] success={0};GLES30.glGetShaderiv(sh,GLES30.GL_COMPILE_STATUS,success,0);
      if(success[0]!=GLES30.GL_TRUE){
        String err=GLES30.glGetShaderInfoLog(sh);GLES30.glDeleteShader(sh);
        throw new IllegalStateException("compile: "+err);
      }
      return sh;
    }
    int program(String frag){
      int vs=compile(GLES30.GL_VERTEX_SHADER,V);
      int fs=compile(GLES30.GL_FRAGMENT_SHADER,frag);
      int p=GLES30.glCreateProgram();GLES30.glAttachShader(p,vs);GLES30.glAttachShader(p,fs);
      GLES30.glLinkProgram(p);int[] ok={0};GLES30.glGetProgramiv(p,GLES30.GL_LINK_STATUS,ok,0);
      GLES30.glDeleteShader(vs);GLES30.glDeleteShader(fs);
      if(ok[0]!=GLES30.GL_TRUE){
        String err=GLES30.glGetProgramInfoLog(p);GLES30.glDeleteProgram(p);
        throw new IllegalStateException("link: "+err);
      }
      return p;
    }
    String twoPass(){
      int[] tex=new int[2],fb=new int[2],vao={0};int p0=0,p1=0;
      try{
        GLES30.glGenTextures(2,tex,0);GLES30.glGenFramebuffers(2,fb,0);
        GLES30.glGenVertexArrays(1,vao,0);GLES30.glBindVertexArray(vao[0]);
        for(int i=0;i<2;i++){
          GLES30.glBindTexture(GLES30.GL_TEXTURE_2D,tex[i]);
          GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D,GLES30.GL_TEXTURE_MIN_FILTER,GLES30.GL_NEAREST);
          GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D,GLES30.GL_TEXTURE_MAG_FILTER,GLES30.GL_NEAREST);
          GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D,GLES30.GL_TEXTURE_WRAP_S,GLES30.GL_CLAMP_TO_EDGE);
          GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D,GLES30.GL_TEXTURE_WRAP_T,GLES30.GL_CLAMP_TO_EDGE);
          GLES30.glTexImage2D(GLES30.GL_TEXTURE_2D,0,GLES30.GL_RGBA8,8,8,0,
              GLES30.GL_RGBA,GLES30.GL_UNSIGNED_BYTE,null);
          GLES30.glBindFramebuffer(GLES30.GL_FRAMEBUFFER,fb[i]);
          GLES30.glFramebufferTexture2D(GLES30.GL_FRAMEBUFFER,GLES30.GL_COLOR_ATTACHMENT0,
              GLES30.GL_TEXTURE_2D,tex[i],0);
          int state=GLES30.glCheckFramebufferStatus(GLES30.GL_FRAMEBUFFER);
          if(state!=GLES30.GL_FRAMEBUFFER_COMPLETE)
            throw new IllegalStateException("FBO"+i+" incomplete: 0x"+Integer.toHexString(state));
        }
        p0=program(F0);p1=program(F1);
        GLES30.glDisable(GLES30.GL_BLEND);GLES30.glDisable(GLES30.GL_DEPTH_TEST);
        GLES30.glDisable(GLES30.GL_SCISSOR_TEST);GLES30.glViewport(0,0,8,8);
        GLES30.glBindFramebuffer(GLES30.GL_FRAMEBUFFER,fb[0]);
        GLES30.glUseProgram(p0);GLES30.glDrawArrays(GLES30.GL_TRIANGLES,0,3);
        GLES30.glBindFramebuffer(GLES30.GL_FRAMEBUFFER,fb[1]);
        GLES30.glActiveTexture(GLES30.GL_TEXTURE0);GLES30.glBindTexture(GLES30.GL_TEXTURE_2D,tex[0]);
        GLES30.glUseProgram(p1);
        int loc=GLES30.glGetUniformLocation(p1,"image0");
        if(loc<0)throw new IllegalStateException("sampler uniform optimized out");
        GLES30.glUniform1i(loc,0);GLES30.glDrawArrays(GLES30.GL_TRIANGLES,0,3);
        ByteBuffer pixel=ByteBuffer.allocateDirect(4).order(ByteOrder.nativeOrder());
        GLES30.glReadPixels(4,4,1,1,GLES30.GL_RGBA,GLES30.GL_UNSIGNED_BYTE,pixel);
        int error=GLES30.glGetError();
        if(error!=GLES30.GL_NO_ERROR)throw new IllegalStateException("GL error 0x"+Integer.toHexString(error));
        int[] actual=new int[4],expected={32,96,159,255};
        for(int i=0;i<4;i++){
          actual[i]=pixel.get(i)&255;
          if(Math.abs(actual[i]-expected[i])>2)
            throw new IllegalStateException("pixel mismatch actual="+Arrays.toString(actual));
        }
        return "OK 2-pass RGBA8 FBO sample; pixel="+Arrays.toString(actual)+" tolerance=2";
      }finally{
        GLES30.glBindFramebuffer(GLES30.GL_FRAMEBUFFER,0);
        GLES30.glViewport(0,0,surfaceWidth,surfaceHeight);
        GLES30.glUseProgram(0);
        GLES30.glBindVertexArray(0);
        if(p0!=0)GLES30.glDeleteProgram(p0);if(p1!=0)GLES30.glDeleteProgram(p1);
        GLES30.glDeleteVertexArrays(1,vao,0);
        GLES30.glDeleteFramebuffers(2,fb,0);GLES30.glDeleteTextures(2,tex,0);
      }
    }
    String invalidFbo(){
      int[] f={0};GLES30.glGenFramebuffers(1,f,0);
      try{
        GLES30.glBindFramebuffer(GLES30.GL_FRAMEBUFFER,f[0]);
        int s=GLES30.glCheckFramebufferStatus(GLES30.GL_FRAMEBUFFER);
        if(s!=GLES30.GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT)
          throw new IllegalStateException("unexpected FBO status=0x"+Integer.toHexString(s));
        return "OK driver rejects unattached FBO: 0x"+Integer.toHexString(s);
      }finally{GLES30.glBindFramebuffer(GLES30.GL_FRAMEBUFFER,0);
        GLES30.glDeleteFramebuffers(1,f,0);}
    }
    String invalidShader(){
      int sh=GLES30.glCreateShader(GLES30.GL_FRAGMENT_SHADER);
      if(sh==0)throw new IllegalStateException("createShader failed");
      try{
        GLES30.glShaderSource(sh,"#version 300 es\nvoid main(){ invalid_token!; }");
        GLES30.glCompileShader(sh);int[] ok={1};
        GLES30.glGetShaderiv(sh,GLES30.GL_COMPILE_STATUS,ok,0);
        if(ok[0]!=GLES30.GL_FALSE)throw new IllegalStateException("invalid GLSL accepted");
        return "OK compile rejected invalid fragment shader";
      }finally{GLES30.glDeleteShader(sh);}
    }
  }
}
