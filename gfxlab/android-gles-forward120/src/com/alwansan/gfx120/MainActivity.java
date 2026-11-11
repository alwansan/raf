package com.alwansan.gfx120;

import android.app.Activity;
import android.content.ContentValues;
import android.net.Uri;
import android.graphics.Bitmap;
import java.util.LinkedHashMap;
import java.util.Map;
import android.opengl.GLSurfaceView;
import android.os.Bundle;
import android.provider.MediaStore;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;
import javax.microedition.khronos.egl.EGLConfig;
import javax.microedition.khronos.opengles.GL10;
import static android.opengl.GLES30.*;

public final class MainActivity extends Activity {
    private static final int SIZE = 256;
    private static final String DIR = "Download/Games/cl/test/g/";
    private final Map<String,byte[]> images = new LinkedHashMap<>();

    private TextView status;
    private GLSurfaceView surface;
    private volatile byte[] report;
    private volatile String result = "";

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        status = new TextView(this);
        status.setText("GFX120: جارٍ رسم المجسم بالشيدر الأصلي…");
        layout.addView(status);
        Button export = new Button(this);
        export.setText("إعادة تصدير السجل");
        export.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View view) { if (report != null) export(); }
        });
        layout.addView(export);
        surface = new GLSurfaceView(this);
        surface.setEGLContextClientVersion(3);
        surface.setRenderer(new GLSurfaceView.Renderer() {
            @Override public void onSurfaceCreated(GL10 ignored, EGLConfig config) { if (report == null) probe(); }
            @Override public void onSurfaceChanged(GL10 ignored, int width, int height) {}
            @Override public void onDrawFrame(GL10 ignored) { glClear(GL_COLOR_BUFFER_BIT); }
        });
        surface.setRenderMode(GLSurfaceView.RENDERMODE_WHEN_DIRTY);
        layout.addView(surface, new LinearLayout.LayoutParams(-1, 0, 1));
        setContentView(layout);
    }

    @Override protected void onPause() { surface.onPause(); super.onPause(); }
    @Override protected void onResume() { super.onResume(); surface.onResume(); }

    private void display(final String message) {
        runOnUiThread(new Runnable() { @Override public void run() { status.setText(message); } });
    }

    private byte[] asset(String name) throws Exception {
        try (InputStream in = getAssets().open(name); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[32768];
            for (int n; (n = in.read(buffer)) != -1;) out.write(buffer, 0, n);
            return out.toByteArray();
        }
    }

    private static String sha256(byte[] data) throws Exception {
        StringBuilder hex = new StringBuilder();
        for (byte b : MessageDigest.getInstance("SHA-256").digest(data))
            hex.append(Character.forDigit((b & 255) >>> 4, 16)).append(Character.forDigit(b & 15, 16));
        return hex.toString();
    }

    private static int shader(int type, String source) {
        int id = glCreateShader(type);
        glShaderSource(id, source);
        glCompileShader(id);
        int[] ok = new int[1];
        glGetShaderiv(id, GL_COMPILE_STATUS, ok, 0);
        if (ok[0] == 0) throw new IllegalStateException(glGetShaderInfoLog(id));
        return id;
    }

    private static void check(String stage) {
        int error = glGetError();
        if (error != GL_NO_ERROR) throw new IllegalStateException(stage + " GLES error " + error);
    }

    private static ByteBuffer direct(byte[] data, int offset, int length) {
        ByteBuffer buffer = ByteBuffer.allocateDirect(length);
        buffer.put(data, offset, length).flip();
        return buffer;
    }

    private int createProgram() throws Exception {
        int program = glCreateProgram();
        int vertex = shader(GL_VERTEX_SHADER,new String(asset("probe.vert"),StandardCharsets.UTF_8));
        int fragment = shader(GL_FRAGMENT_SHADER,new String(asset("probe.frag"),StandardCharsets.UTF_8));
        glAttachShader(program,vertex);
        glAttachShader(program,fragment);
        glLinkProgram(program);
        glDeleteShader(vertex);
        glDeleteShader(fragment);
        int[] status = new int[1];
        glGetProgramiv(program,GL_LINK_STATUS,status,0);
        if (status[0] == 0) throw new IllegalStateException(glGetProgramInfoLog(program));
        glUseProgram(program);
        return program;
    }

    private static int buffer(int target, byte[] bytes) {
        int[] ids = new int[1];
        glGenBuffers(1,ids,0);
        glBindBuffer(target,ids[0]);
        glBufferData(target,bytes.length,direct(bytes,0,bytes.length),GL_STATIC_DRAW);
        return ids[0];
    }

    private void bindBlocks(int program, JSONArray blocks, boolean light) throws Exception {
        for (int i=0; i<blocks.length(); i++) {
            JSONObject row=blocks.getJSONObject(i);
            int index=glGetUniformBlockIndex(program,row.getString("name"));
            if (index < 0) throw new IllegalStateException("Expected block missing");
            int[] size=new int[1];
            glGetActiveUniformBlockiv(program,index,GL_UNIFORM_BLOCK_DATA_SIZE,size,0);
            byte[] bytes=asset(row.getString(light ? "light" : "dark"));
            if (size[0] != bytes.length || bytes.length != row.getInt("bytes"))
                throw new IllegalStateException("Unexpected driver block size");
            glUniformBlockBinding(program,index,i);
            int id=buffer(GL_UNIFORM_BUFFER,bytes);
            glBindBufferBase(GL_UNIFORM_BUFFER,i,id);
        }
    }

    private void bindTextures(int program, JSONArray samplers, String control) throws Exception {
        for (int i=0; i<samplers.length(); i++) {
            JSONObject row=samplers.getJSONObject(i);
            String kind=row.getString("kind"), role=row.getString("role");
            int target;
            switch (kind) {
                case "sampler2D": target=GL_TEXTURE_2D; break;
                case "sampler3D": target=GL_TEXTURE_3D; break;
                case "samplerCube": target=GL_TEXTURE_CUBE_MAP; break;
                default: throw new IllegalStateException("Unexpected sampler target");
            }
            boolean source=!role.isEmpty();
            boolean replaced=(control.equals("flat") && role.equals("normal"))
                || (control.equals("nonmetal") && role.equals("metallic"));
            int[] ids=new int[1];
            glGenTextures(1,ids,0);
            glActiveTexture(GL_TEXTURE0+i);
            glBindTexture(target,ids[0]);
            glTexParameteri(target,GL_TEXTURE_WRAP_S,source ? GL_REPEAT : GL_CLAMP_TO_EDGE);
            glTexParameteri(target,GL_TEXTURE_WRAP_T,source ? GL_REPEAT : GL_CLAMP_TO_EDGE);
            glTexParameteri(target,GL_TEXTURE_MAG_FILTER,GL_LINEAR);
            glTexParameteri(target,GL_TEXTURE_MIN_FILTER,source ? GL_LINEAR_MIPMAP_NEAREST : GL_LINEAR);
            glTexParameteri(target,GL_TEXTURE_MAX_LEVEL,source && !replaced ? 10 : 0);
            int format=role.equals("normal") || !source ? GL_RGBA8 : GL_SRGB8_ALPHA8;
            byte[] black={0,0,0,(byte)255};
            if (source && !replaced) {
                byte[] raw=asset(role+".rgba");
                int offset=0;
                for (int mip=0; mip<=10; mip++) {
                    int width=1024>>mip, length=width*width*4;
                    glTexImage2D(target,mip,format,width,width,0,GL_RGBA,GL_UNSIGNED_BYTE,direct(raw,offset,length));
                    offset+=length;
                }
                if (offset!=raw.length) throw new IllegalStateException("Unexpected mip chain length");
            } else if (target==GL_TEXTURE_2D) {
                byte[] rgba=!replaced ? new byte[]{-1,-1,-1,-1}
                    : role.equals("normal") ? new byte[]{-1,-128,-1,-128} : black;
                glTexImage2D(target,0,format,1,1,0,GL_RGBA,GL_UNSIGNED_BYTE,direct(rgba,0,4));
            } else if (target==GL_TEXTURE_CUBE_MAP) {
                for (int face=0; face<6; face++)
                    glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X+face,0,format,1,1,0,
                        GL_RGBA,GL_UNSIGNED_BYTE,direct(black,0,4));
            } else {
                glTexImage3D(target,0,format,1,1,1,0,GL_RGBA,GL_UNSIGNED_BYTE,direct(black,0,4));
            }
            int location=glGetUniformLocation(program,row.getString("name"));
            if (location<0) throw new IllegalStateException("Expected combined sampler missing");
            glUniform1i(location,i);
        }
    }

    private JSONObject capture(String name) throws Exception {
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);
        glDrawElements(GL_TRIANGLES,2388*3,GL_UNSIGNED_SHORT,0);
        ByteBuffer pixels=ByteBuffer.allocateDirect(SIZE*SIZE*4);
        glReadPixels(0,0,SIZE,SIZE,GL_RGBA,GL_UNSIGNED_BYTE,pixels);
        check("Forward draw " + name);
        byte[] raw=new byte[pixels.capacity()];
        pixels.position(0);
        pixels.get(raw);
        byte[] reference=asset(name+".rgba");
        if (reference.length!=raw.length) throw new IllegalStateException("Wrong reference size");
        int[] argb=new int[SIZE*SIZE];
        int coverage=0, coverageDiff=0, rgbCount=0, maxError=0;
        long rgbError=0;
        for (int y=0; y<SIZE; y++) for (int x=0; x<SIZE; x++) {
            int i=(y*SIZE+x)*4;
            int r=raw[i]&255, g=raw[i+1]&255, b=raw[i+2]&255, a=raw[i+3]&255;
            boolean covered=a==255, expected=(reference[i+3]&255)==255;
            if (a!=0 && !covered) throw new IllegalStateException("Unexpected output alpha");
            if (covered) coverage++;
            if (covered!=expected) coverageDiff++;
            if (covered && expected) {
                for (int ch=0; ch<3; ch++) {
                    int error=Math.abs((raw[i+ch]&255)-(reference[i+ch]&255));
                    maxError=Math.max(maxError,error);
                    rgbError+=error;
                    rgbCount++;
                }
            }
            argb[(SIZE-1-y)*SIZE+x]=(a<<24)|(r<<16)|(g<<8)|b;
        }
        if (coverage==0) throw new IllegalStateException("Empty original Forward draw");
        Bitmap bitmap=Bitmap.createBitmap(argb,SIZE,SIZE,Bitmap.Config.ARGB_8888);
        ByteArrayOutputStream out=new ByteArrayOutputStream();
        boolean ok=bitmap.compress(Bitmap.CompressFormat.PNG,100,out);
        bitmap.recycle();
        if (!ok) throw new IllegalStateException("PNG capture failed");
        byte[] png=out.toByteArray();
        String filename=name+".png";
        images.put(filename,png);
        return new JSONObject().put("name",name).put("image",filename)
            .put("image_sha256",sha256(png)).put("raw_rgba_sha256",sha256(raw))
            .put("mesa_rgba_sha256",sha256(reference)).put("covered_pixels",coverage)
            .put("coverage_different_pixels",coverageDiff).put("rgb_channels",rgbCount)
            .put("rgb_absolute_error_sum",rgbError).put("max_rgb_channel_error",maxError);
    }

    private void probe() {
        JSONObject summary=new JSONObject();
        try {
            summary.put("experiment","GFX120").put("renderer",glGetString(GL_RENDERER))
                .put("gles",glGetString(GL_VERSION)).put("phase_closed",false);
            JSONObject scene=new JSONObject(new String(asset("scene.json"),StandardCharsets.UTF_8));
            JSONArray blocks=scene.getJSONArray("blocks"), samplers=scene.getJSONArray("samplers");
            if (blocks.length()!=8 || samplers.length()!=7) throw new IllegalStateException("Wrong fixture shape");
            int program=createProgram();
            int[] fbo=new int[1], color=new int[1], depth=new int[1], vao=new int[1];
            glGenVertexArrays(1,vao,0);
            glBindVertexArray(vao[0]);
            glGenFramebuffers(1,fbo,0);
            glBindFramebuffer(GL_FRAMEBUFFER,fbo[0]);
            glGenTextures(1,color,0);
            glBindTexture(GL_TEXTURE_2D,color[0]);
            glTexStorage2D(GL_TEXTURE_2D,1,GL_RGBA8,SIZE,SIZE);
            glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,color[0],0);
            glGenRenderbuffers(1,depth,0);
            glBindRenderbuffer(GL_RENDERBUFFER,depth[0]);
            glRenderbufferStorage(GL_RENDERBUFFER,GL_DEPTH_COMPONENT24,SIZE,SIZE);
            glFramebufferRenderbuffer(GL_FRAMEBUFFER,GL_DEPTH_ATTACHMENT,GL_RENDERBUFFER,depth[0]);
            if (glCheckFramebufferStatus(GL_FRAMEBUFFER)!=GL_FRAMEBUFFER_COMPLETE)
                throw new IllegalStateException("Framebuffer incomplete");

            byte[] mesh=asset("mesh.bin"), indices=asset("indices.bin");
            if (mesh.length!=1666*48 || indices.length!=2388*6) throw new IllegalStateException("Wrong mesh shape");
            buffer(GL_ARRAY_BUFFER,mesh);
            int[][] attributes={{0,3,0},{1,3,12},{2,2,40},{4,4,24}};
            for (int[] row:attributes) {
                glVertexAttribPointer(row[0],row[1],GL_FLOAT,false,48,row[2]);
                glEnableVertexAttribArray(row[0]);
            }
            glVertexAttrib2f(3,0,0);
            buffer(GL_ELEMENT_ARRAY_BUFFER,indices);
            glViewport(0,0,SIZE,SIZE);
            glEnable(GL_DEPTH_TEST);
            glDepthFunc(GL_LESS);
            glDepthMask(true);
            glClearDepthf(1);
            glDisable(GL_DITHER);
            glDisable(GL_BLEND);
            glDisable(GL_CULL_FACE);
            glClearColor(0,0,0,0);
            JSONArray captures=new JSONArray();
            summary.put("captures",captures);
            bindTextures(program,samplers,"light");
            bindBlocks(program,blocks,true);
            captures.put(capture("light"));
            bindBlocks(program,blocks,false);
            captures.put(capture("dark"));
            bindBlocks(program,blocks,true);
            bindTextures(program,samplers,"flat");
            captures.put(capture("flat"));
            bindTextures(program,samplers,"nonmetal");
            captures.put(capture("nonmetal"));
            summary.put("bound_cb_blocks",blocks.length()).put("bound_samplers",samplers.length())
                .put("original_forward_draw_completed",true);
            result="اكتمل رسم Forward وحُفظت أربع صور للمقارنة.";
            glBindFramebuffer(GL_FRAMEBUFFER,0);
            glDeleteProgram(program);
        } catch (Exception ex) {
            result="توقف الاختبار. تفاصيل الخطأ في السجل.";
            try { summary.put("error",ex.toString()).put("original_forward_draw_completed",false); }
            catch (Exception invalid) { display(invalid.toString()); return; }
        }
        report=summary.toString().getBytes(StandardCharsets.UTF_8);
        export();
    }

    private void export() {
        new Thread(new Runnable() { @Override public void run() { writeReport(); } }).start();
    }

    private void writeReport() {
        Uri uri = null;
        String name = "GFX120-ALL-TEST-LOGS-" + System.currentTimeMillis() + ".zip";
        try {
            ContentValues values = new ContentValues();
            values.put(MediaStore.Downloads.DISPLAY_NAME,name);
            values.put(MediaStore.Downloads.MIME_TYPE,"application/zip");
            values.put(MediaStore.Downloads.RELATIVE_PATH,DIR);
            values.put(MediaStore.Downloads.IS_PENDING,1);
            uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,values);
            if (uri == null) throw new IllegalStateException("Cannot create download");
            try (OutputStream out = getContentResolver().openOutputStream(uri)) {
                if (out == null) throw new IllegalStateException("Cannot open download");
                try (ZipOutputStream zip = new ZipOutputStream(out)) {
                    zip.putNextEntry(new ZipEntry("summary.json"));
                    zip.write(report);
                    zip.closeEntry();
                    for (Map.Entry<String,byte[]> entry : images.entrySet()) {
                        zip.putNextEntry(new ZipEntry(entry.getKey()));
                        zip.write(entry.getValue());
                        zip.closeEntry();
                    }
                }
            }
            values.clear();
            values.put(MediaStore.Downloads.IS_PENDING,0);
            if (getContentResolver().update(uri,values,null,null) != 1)
                throw new IllegalStateException("Cannot publish download");
            display(result + "\n" + DIR + name);
        } catch (Exception ex) {
            if (uri != null) getContentResolver().delete(uri,null,null);
            display("تعذّر حفظ السجل. جرّب زر إعادة التصدير.\n" + ex);
        }
    }
}
