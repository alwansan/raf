package com.alwansan.raft.t3lab;

import android.app.Activity;
import android.graphics.Bitmap;
import android.view.PixelCopy;
import com.alwansan.raftlab.BuildConfig;
import android.content.ContentValues;
import android.content.Intent;
import android.graphics.PixelFormat;
import android.net.Uri;
import android.opengl.GLES30;
import android.opengl.GLSurfaceView;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.os.Bundle;
import android.os.Environment;
import android.os.SystemClock;
import android.provider.MediaStore;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.FloatBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Date;
import java.util.Locale;
import java.text.SimpleDateFormat;
import javax.microedition.khronos.egl.EGLConfig;
import javax.microedition.khronos.opengles.GL10;

/** No Raft assets or executable testpacks. Synthetic GLES3 diagnostics, not Unity proof. */
public final class T3LabActivity extends Activity {
    static final String[] TITLES = {"GLES3 / driver baseline","vertex colors and interpolation",
        "straight alpha smoke overlay","straight versus premultiplied alpha",
        "UNORM versus sRGB texture decode","bad shader must fail compilation"};
    static final String[] EXPECTED = {"Red, green, blue fields; GPU info in log",
        "Interpolated four-corner colors, not white","Blue background visible through red smoke overlay",
        "Two halves appear approximately equal when blend contracts match",
        "sRGB-decoded half is darker than UNORM half for encoded 128",
        "Deliberately invalid shader is rejected, valid fallback remains visible"};
    static final String[] STEPS = {"Select CASE01 and take a screenshot.",
        "Select CASE02; inspect corners and center.",
        "Select CASE03; check transparency and absence of opaque squares.",
        "Select CASE04; compare two panels visually.",
        "Select CASE05; compare left and right brightness.",
        "Select CASE06; check log for expected shader compile failure."};
    static final int PICK_TESTPACK=61;
    final Object lock=new Object();
    File logfile;
    String session, testId="CASE01", packId="builtin", packHash="none";
    JSONObject packOverrides=new JSONObject();
    GLSurfaceView surface;
    Painter painter;
    TextView instructions, status;
    EditText note;
    int caseIndex=0;

    TextView text(String value) { TextView t=new TextView(this); t.setText(value);
        t.setTextSize(15);t.setPadding(6,4,6,4);return t; }
    void button(LinearLayout parent,String name,View.OnClickListener action) {
        Button b=new Button(this);b.setText(name);parent.addView(b);b.setOnClickListener(action);
    }
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        session=new SimpleDateFormat("yyyyMMdd-HHmmss",Locale.US).format(new Date())
            +"-"+SystemClock.elapsedRealtime();
        File dir=new File(getFilesDir(),"sessions");if(!dir.exists()&&!dir.mkdirs())
            throw new IllegalStateException("Cannot create app-private log directory");
        logfile=new File(dir,"events-"+session+".jsonl");
        LinearLayout page=new LinearLayout(this);page.setOrientation(LinearLayout.VERTICAL);
        setContentView(page);
        page.addView(text("T3 GLES MATERIAL LAB 0.1.0 | "+BuildConfig.SOURCE_SHA.substring(0,Math.min(10,BuildConfig.SOURCE_SHA.length()))
            +" | synthetic GLES3 ≠ Unity/Raft"));
        HorizontalScrollView scroll=new HorizontalScrollView(this);
        LinearLayout choices=new LinearLayout(this);
        for(int i=0;i<6;i++){final int index=i;button(choices,"CASE0"+(i+1),v->select(index));}
        scroll.addView(choices);page.addView(scroll);
        instructions=text("");page.addView(instructions);
        surface=new GLSurfaceView(this);surface.setEGLContextClientVersion(3);
        surface.getHolder().setFormat(PixelFormat.RGBA_8888);
        painter=new Painter();surface.setRenderer(painter);
        surface.setRenderMode(GLSurfaceView.RENDERMODE_WHEN_DIRTY);
        page.addView(surface,new LinearLayout.LayoutParams(-1,0,1));
        note=new EditText(this);note.setSingleLine(true);
        note.setHint("Observed result / notes (max 800 chars)");page.addView(note);
        LinearLayout actions=new LinearLayout(this);page.addView(actions);
        button(actions,"PASS",v->result("PASS"));
        button(actions,"FAIL",v->result("FAIL"));
        button(actions,"UNEXPECTED",v->result("UNEXPECTED"));
        button(actions,"Import JSON",v->{
            Intent intent=new Intent(Intent.ACTION_OPEN_DOCUMENT);intent.addCategory(Intent.CATEGORY_OPENABLE);
            intent.setType("application/json");
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);startActivityForResult(intent,PICK_TESTPACK);
        });
        button(actions,"Export logs",v->exportLogs());
        status=text("App-private logging active; export to Download/Games/cl/test/");
        page.addView(status);
        log("startup","package="+getPackageName()+" version=0.1.0 source="+BuildConfig.SOURCE_SHA
            +" device="+Build.MANUFACTURER+"/"+Build.MODEL+" api="+Build.VERSION.SDK_INT
            +" abi="+Build.SUPPORTED_ABIS[0]);
        select(0);
        runSharedAutoT3();
    }
    void runSharedAutoT3(){
        String id=getIntent()==null?null:getIntent().getStringExtra("auto_case_id");
        if(id==null||!id.matches("T3-0[1-6]"))return;
        int idx=Integer.parseInt(id.substring(4))-1;
        new Handler(Looper.getMainLooper()).postDelayed(()->{
            select(idx);
            new Handler(Looper.getMainLooper()).postDelayed(()->captureSharedEvidence(id),1000);
        },850);
    }
    void captureSharedEvidence(String id){
        android.view.View decor=getWindow().getDecorView();
        if(decor==null||decor.getWidth()<=0||decor.getHeight()<=0){
            finishSharedEvidence(id,"NEEDS_SCREENSHOT",null,"No window pixels yet");return;
        }
        int width=Math.min(decor.getWidth(),1600),height=Math.min(decor.getHeight(),900);
        final Bitmap bmp=Bitmap.createBitmap(width,height,Bitmap.Config.ARGB_8888);
        try{
            PixelCopy.request(getWindow(),bmp,result->{
                if(result!=PixelCopy.SUCCESS){
                    bmp.recycle();finishSharedEvidence(id,"NEEDS_SCREENSHOT",null,"PixelCopy code "+result);return;
                }
                String uri=null;
                try{
                    ContentValues v=new ContentValues();
                    v.put(MediaStore.Downloads.DISPLAY_NAME,id+"-"+System.currentTimeMillis()+".png");
                    v.put(MediaStore.Downloads.MIME_TYPE,"image/png");
                    String parent=getIntent()==null?null:getIntent().getStringExtra("shared_session");
                    if(parent==null||!parent.matches("[A-Za-z0-9._-]{6,90}"))parent=session;
                    v.put(MediaStore.Downloads.RELATIVE_PATH,Environment.DIRECTORY_DOWNLOADS+"/Games/cl/test/shared-"+parent+"/");
                    Uri dest=getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,v);
                    if(dest==null)throw new IOException("Could not write PNG");
                    try(OutputStream out=getContentResolver().openOutputStream(dest,"wt")){
                        if(out==null||!bmp.compress(Bitmap.CompressFormat.PNG,100,out))throw new IOException("Bitmap compress failed");
                        out.flush();
                    }
                    uri=dest.toString();log("pixelcopy_png","id="+id+" uri="+uri);
                    finishSharedEvidence(id,"EVIDENCE_READY",uri,"GLES synthetic frame, visual review still required");
                }catch(Exception e){log("screenshot_error",e.toString());
                    finishSharedEvidence(id,"NEEDS_SCREENSHOT",null,e.getClass().getSimpleName());}
                finally{bmp.recycle();}
            },new Handler(Looper.getMainLooper()));
        }catch(Exception e){
            bmp.recycle();finishSharedEvidence(id,"NEEDS_SCREENSHOT",null,e.getClass().getSimpleName());
        }
    }
    void finishSharedEvidence(String id,String verdict,String uri,String observed){
        Intent reply=new Intent();reply.putExtra("case_id",id);reply.putExtra("status",verdict);
        reply.putExtra("observed",observed);if(uri!=null)reply.putExtra("screenshot_uri",uri);
        log("shared_auto_result",id+" "+verdict+" "+observed);
        setResult(RESULT_OK,reply);finish();
    }
    void select(int index){
        caseIndex=index;testId="CASE0"+(index+1);
        JSONObject override=packOverrides.optJSONObject(testId);
        String step=override==null?STEPS[index]:override.optString("instructions",STEPS[index]);
        String expected=override==null?EXPECTED[index]:override.optString("expected",EXPECTED[index]);
        instructions.setText(testId+" — "+TITLES[index]+"\nDO: "+step+"\nEXPECTED: "+expected);
        note.setText("");
        log("case_start","index="+index+" pack="+packId);
        if(surface!=null)surface.requestRender();
    }
    void result(String verdict) {
        String observed=note.getText().toString().replace('\n',' ');
        if(observed.length()>800)observed=observed.substring(0,800);
        log("case_result",testId+"="+verdict+" observed="+observed);
        status.setText(testId+" "+verdict+" — saved privately. Tap Export logs.");
    }
    synchronized void log(String event,String value) {
        try {
            JSONObject json=new JSONObject();json.put("utc_ms",System.currentTimeMillis());
            json.put("elapsed_ms",SystemClock.elapsedRealtime());json.put("event",event);
            json.put("test",testId);json.put("session",session);json.put("pack",packId);
            json.put("detail",value);
            try(FileOutputStream out=new FileOutputStream(logfile,true)){
                out.write((json.toString()+"\n").getBytes(StandardCharsets.UTF_8));
                out.getFD().sync();
            }
        }catch(Exception e){android.util.Log.e("T3Lab","Log write failed",e);}
    }
    void exportLogs() {
        if(Build.VERSION.SDK_INT<29){status.setText("Use Android 10+ MediaStore for export");return;}
        try {
            String folder="Games/cl/test/t3-gles-material-"+session+"/";
            ContentValues cv=new ContentValues();
            cv.put(MediaStore.Downloads.DISPLAY_NAME,logfile.getName());
            cv.put(MediaStore.Downloads.MIME_TYPE,"application/x-ndjson");
            cv.put(MediaStore.Downloads.RELATIVE_PATH,Environment.DIRECTORY_DOWNLOADS+"/"+folder);
            Uri uri=getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,cv);
            if(uri==null)throw new IllegalStateException("MediaStore insertion failed");
            try(InputStream input=new java.io.FileInputStream(logfile);
                OutputStream out=getContentResolver().openOutputStream(uri,"w")){
                if(out==null)throw new IllegalStateException("MediaStore stream failed");
                byte[] bytes=new byte[16384];int n;while((n=input.read(bytes))!=-1)out.write(bytes,0,n);
            }
            status.setText("Exported: Download/"+folder+logfile.getName());
        }catch(Exception e){log("export_error",e.getClass().getSimpleName()+": "+e.getMessage());
            status.setText("Export failed; private logs remain: "+e.getMessage());}
    }
    @Override protected void onActivityResult(int request,int result,Intent data) {
        super.onActivityResult(request,result,data);
        if(request!=PICK_TESTPACK||result!=RESULT_OK||data==null||data.getData()==null)return;
        try {
            byte[] bytes=new byte[65537];int n=0;
            try(InputStream in=getContentResolver().openInputStream(data.getData())){
                if(in==null)throw new IllegalStateException("Unreadable file");
                while(n<bytes.length){int k=in.read(bytes,n,bytes.length-n);if(k<0)break;n+=k;}
            }
            if(n>65536)throw new IllegalArgumentException("Pack exceeds 64 KiB");
            JSONObject obj=new JSONObject(new String(bytes,0,n,StandardCharsets.UTF_8));
            if(obj.length()!=7||obj.getInt("schema_version")!=1||
                !"T3".equals(obj.getString("worker")))throw new IllegalArgumentException("Not T3 data-only v1 pack");
            String id=obj.getString("pack_id");
            if(!id.matches("[a-z0-9][a-z0-9._-]{0,79}"))throw new IllegalArgumentException("Invalid pack id");
            if(!obj.isNull("source_sha")&&!obj.getString("source_sha").matches("[a-f0-9]{40}"))
                throw new IllegalArgumentException("Invalid source SHA");
            JSONArray tests=obj.getJSONArray("tests");
            if(tests.length()<1||tests.length()>6)throw new IllegalArgumentException("1..6 cases required");
            JSONObject parsed=new JSONObject();
            for(int i=0;i<tests.length();i++){
                JSONObject t=tests.getJSONObject(i);
                String key=t.getString("id");
                if(!key.matches("CASE0[1-6]")||parsed.has(key)||
                    !"note".equals(t.getString("type")) ||
                    t.getString("title").length()>1500 ||
                    t.getString("instructions").length()>1500 ||
                    t.getString("expected").length()>1500)
                    throw new IllegalArgumentException("Unsupported/duplicate test; text-only CASE01..06 required");
                parsed.put(key,t);
            }
            MessageDigest digest=MessageDigest.getInstance("SHA-256");
            byte[] hash=digest.digest(java.util.Arrays.copyOf(bytes,n));
            StringBuilder hex=new StringBuilder();for(byte b:hash)hex.append(String.format(Locale.US,"%02x",b&255));
            packOverrides=parsed;packId=id;packHash=hex.toString();
            log("pack_import","pack_id="+packId+" sha256="+packHash+" tests="+tests.length());
            select(caseIndex);
            Toast.makeText(this,"T3 data-only instructions loaded",Toast.LENGTH_LONG).show();
        }catch(Exception e){log("pack_reject",e.getClass().getSimpleName()+": "+e.getMessage());
            Toast.makeText(this,"Pack rejected: "+e.getMessage(),Toast.LENGTH_LONG).show();}
    }
    @Override protected void onPause(){super.onPause();if(surface!=null)surface.onPause();log("lifecycle","pause");}
    @Override protected void onResume(){super.onResume();if(surface!=null)surface.onResume();}
    @Override protected void onStop(){super.onStop();log("lifecycle","stop");}

    final class Painter implements GLSurfaceView.Renderer {
        final String vertex="#version 300 es\nlayout(location=0) in vec2 pos;\n"
           +"layout(location=1) in vec4 col;\nlayout(location=2) in vec2 uv;\n"
           +"out vec4 color;out vec2 texCoord;\nvoid main(){gl_Position=vec4(pos,0.0,1.0);color=col;texCoord=uv;}";
        final String fragment="#version 300 es\nprecision highp float;\nin vec4 color;in vec2 texCoord;\n"
           +"uniform sampler2D imageTex;uniform int useTex;out vec4 frag;\n"
           +"void main(){frag=color*(useTex==1?texture(imageTex,texCoord):vec4(1.0));}";
        int program=0,vbo=0,plain=0,srgb=0,smoke=0,width=1,height=1;
        int useTexLocation=-1;
        boolean negativeChecked=false;
        int compile(int type,String source,String label){
            int shader=GLES30.glCreateShader(type);
            GLES30.glShaderSource(shader,source);GLES30.glCompileShader(shader);
            int[] status=new int[1];GLES30.glGetShaderiv(shader,GLES30.GL_COMPILE_STATUS,status,0);
            if(status[0]==0){String err=GLES30.glGetShaderInfoLog(shader);
                log("shader_compile_failure",label+" "+(err.length()>600?err.substring(0,600):err));
                GLES30.glDeleteShader(shader);return 0;}
            log("shader_compile_success",label);return shader;
        }
        int texture(int internal,int r,int g,int b,int a) {
            int[] out=new int[1];GLES30.glGenTextures(1,out,0);
            GLES30.glBindTexture(GLES30.GL_TEXTURE_2D,out[0]);
            GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D,GLES30.GL_TEXTURE_MIN_FILTER,GLES30.GL_NEAREST);
            GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D,GLES30.GL_TEXTURE_MAG_FILTER,GLES30.GL_NEAREST);
            GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D,GLES30.GL_TEXTURE_WRAP_S,GLES30.GL_CLAMP_TO_EDGE);
            GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D,GLES30.GL_TEXTURE_WRAP_T,GLES30.GL_CLAMP_TO_EDGE);
            ByteBuffer pixels=ByteBuffer.allocateDirect(16);
            for(int i=0;i<4;i++)pixels.put((byte)r).put((byte)g).put((byte)b).put((byte)a);
            pixels.flip();GLES30.glTexImage2D(GLES30.GL_TEXTURE_2D,0,internal,2,2,0,
                GLES30.GL_RGBA,GLES30.GL_UNSIGNED_BYTE,pixels);
            return out[0];
        }
        @Override public void onSurfaceCreated(GL10 gl,EGLConfig config) {
            log("gles_context","vendor="+GLES30.glGetString(GLES30.GL_VENDOR)
                +" renderer="+GLES30.glGetString(GLES30.GL_RENDERER)
                +" version="+GLES30.glGetString(GLES30.GL_VERSION)
                +" GLSL="+GLES30.glGetString(GLES30.GL_SHADING_LANGUAGE_VERSION));
            int vs=compile(GLES30.GL_VERTEX_SHADER,vertex,"valid_vertex");
            int fs=compile(GLES30.GL_FRAGMENT_SHADER,fragment,"valid_fragment");
            if(vs!=0&&fs!=0){
                program=GLES30.glCreateProgram();GLES30.glAttachShader(program,vs);GLES30.glAttachShader(program,fs);
                GLES30.glLinkProgram(program);int[] ok=new int[1];
                GLES30.glGetProgramiv(program,GLES30.GL_LINK_STATUS,ok,0);
                if(ok[0]==0){log("shader_link_failure",GLES30.glGetProgramInfoLog(program));program=0;}
            }
            if(vs!=0)GLES30.glDeleteShader(vs);if(fs!=0)GLES30.glDeleteShader(fs);
            if(program==0){log("fatal","GLES3 program unavailable");return;}
            useTexLocation=GLES30.glGetUniformLocation(program,"useTex");
            int[] buffers=new int[1];GLES30.glGenBuffers(1,buffers,0);vbo=buffers[0];
            plain=texture(GLES30.GL_RGBA8,128,128,128,255);
            srgb=texture(GLES30.GL_SRGB8_ALPHA8,128,128,128,255);
            smoke=texture(GLES30.GL_RGBA8,255,15,0,128);
            log("resource_init","unorm="+plain+" srgb="+srgb+" rgbaSmoke="+smoke+
                " gl_error=0x"+Integer.toHexString(GLES30.glGetError()));
        }
        @Override public void onSurfaceChanged(GL10 gl,int w,int h) {
            width=Math.max(1,w);height=Math.max(1,h);GLES30.glViewport(0,0,width,height);
        }
        void quad(float x0,float y0,float x1,float y1,float r,float g,float b,float a,int tex) {
            float[] values={
                x0,y0,r,g,b,a,0,0, x1,y0,r,g,b,a,1,0,
                x0,y1,r,g,b,a,0,1, x1,y1,r,g,b,a,1,1
            };
            draw(values,tex);
        }
        void draw(float[] array,int tex) {
            ByteBuffer memory=ByteBuffer.allocateDirect(array.length*4).order(ByteOrder.nativeOrder());
            FloatBuffer data=memory.asFloatBuffer();data.put(array);data.position(0);
            GLES30.glBindBuffer(GLES30.GL_ARRAY_BUFFER,vbo);
            GLES30.glBufferData(GLES30.GL_ARRAY_BUFFER,array.length*4,data,GLES30.GL_STREAM_DRAW);
            GLES30.glEnableVertexAttribArray(0);GLES30.glVertexAttribPointer(0,2,GLES30.GL_FLOAT,false,32,0);
            GLES30.glEnableVertexAttribArray(1);GLES30.glVertexAttribPointer(1,4,GLES30.GL_FLOAT,false,32,8);
            GLES30.glEnableVertexAttribArray(2);GLES30.glVertexAttribPointer(2,2,GLES30.GL_FLOAT,false,32,24);
            GLES30.glUniform1i(useTexLocation,tex==0?0:1);
            GLES30.glActiveTexture(GLES30.GL_TEXTURE0);GLES30.glBindTexture(GLES30.GL_TEXTURE_2D,tex);
            GLES30.glDrawArrays(GLES30.GL_TRIANGLE_STRIP,0,4);
        }
        void pixel(String name,int x,int y) {
            ByteBuffer buffer=ByteBuffer.allocateDirect(4);
            GLES30.glReadPixels(x,y,1,1,GLES30.GL_RGBA,GLES30.GL_UNSIGNED_BYTE,buffer);
            log("pixel_rgba",name+"="+(buffer.get(0)&255)+","+(buffer.get(1)&255)+","
                +(buffer.get(2)&255)+","+(buffer.get(3)&255));
        }
        @Override public void onDrawFrame(GL10 gl) {
            GLES30.glDisable(GLES30.GL_BLEND);GLES30.glClearColor(0.07f,0.07f,0.10f,1f);
            GLES30.glClear(GLES30.GL_COLOR_BUFFER_BIT);
            if(program==0)return;
            GLES30.glUseProgram(program);GLES30.glUniform1i(GLES30.glGetUniformLocation(program,"imageTex"),0);
            int current=caseIndex;
            switch(current) {
                case 0:
                    quad(-1,-1,-.34f,1,1,0,0,1,0);
                    quad(-.34f,-1,.34f,1,0,1,0,1,0);
                    quad(.34f,-1,1,1,0,0,1,1,0);
                    break;
                case 1:
                    draw(new float[]{
                        -1,-1,1,0,0,1,0,0, 1,-1,0,1,0,1,1,0,
                        -1,1,0,0,1,1,0,1, 1,1,1,1,1,1,1,1
                    },0);
                    break;
                case 2:
                    quad(-.95f,-.9f,.95f,.9f,0,.2f,.85f,1,0);
                    GLES30.glEnable(GLES30.GL_BLEND);
                    GLES30.glBlendFunc(GLES30.GL_SRC_ALPHA,GLES30.GL_ONE_MINUS_SRC_ALPHA);
                    quad(-.72f,-.7f,.72f,.7f,1,1,1,1,smoke);
                    GLES30.glDisable(GLES30.GL_BLEND);
                    break;
                case 3:
                    quad(-.95f,-.9f,-.05f,.9f,0,.1f,.85f,1,0);
                    quad(.05f,-.9f,.95f,.9f,0,.1f,.85f,1,0);
                    GLES30.glEnable(GLES30.GL_BLEND);
                    GLES30.glBlendFunc(GLES30.GL_SRC_ALPHA,GLES30.GL_ONE_MINUS_SRC_ALPHA);
                    quad(-.87f,-.6f,-.13f,.6f,1,.1f,0,.5f,0);
                    GLES30.glBlendFunc(GLES30.GL_ONE,GLES30.GL_ONE_MINUS_SRC_ALPHA);
                    quad(.13f,-.6f,.87f,.6f,.5f,.05f,0,.5f,0);
                    GLES30.glDisable(GLES30.GL_BLEND);
                    break;
                case 4:
                    quad(-.95f,-.9f,-.05f,.9f,1,1,1,1,plain);
                    quad(.05f,-.9f,.95f,.9f,1,1,1,1,srgb);
                    break;
                case 5:
                    if(!negativeChecked){
                        negativeChecked=true;
                        int bad=compile(GLES30.GL_FRAGMENT_SHADER,
                            "#version 300 es\nprecision mediump float;out vec4 x;void main(){x = INVALID_TOKEN;}","expected_negative");
                        if(bad==0)log("negative_control","PASS invalid shader rejected");
                        else{log("negative_control","FAIL invalid shader compiled unexpectedly");
                            GLES30.glDeleteShader(bad);}
                    }
                    quad(-1,-1,1,1,.1f,.45f,.8f,1,0);
                    break;
                default:break;
            }
            pixel("left_center",width/4,height/2);pixel("right_center",3*width/4,height/2);
            log("render","case=CASE0"+(current+1)+" gl_error=0x"+Integer.toHexString(GLES30.glGetError())
                +" viewport="+width+"x"+height);
        }
    }
}
