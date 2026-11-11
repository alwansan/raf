package com.alwansan.gfx124;

import android.app.Activity;
import android.content.ContentValues;
import android.net.Uri;
import android.graphics.Bitmap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.List;
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
    private ByteBuffer mipUpload;
    private final byte[] mipChunk = new byte[64 * 1024];

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        status = new TextView(this);
        status.setText("GFX124: جارٍ رسم المجسم بالشيدر الأصلي…");
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

    private int createProgram(String folder) throws Exception {
        int program = glCreateProgram();
        int vertex = shader(GL_VERTEX_SHADER,new String(asset(folder+"probe.vert"),StandardCharsets.UTF_8));
        int fragment = shader(GL_FRAGMENT_SHADER,new String(asset(folder+"probe.frag"),StandardCharsets.UTF_8));
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

    private void bindBlocks(Slot slot, boolean light) throws Exception {
        for (int i=0; i<slot.blocks.length(); i++) {
            JSONObject row=slot.blocks.getJSONObject(i);
            int program=slot.program;
            int index=glGetUniformBlockIndex(program,row.getString("name"));
            if (index < 0) throw new IllegalStateException("Expected block missing");
            int[] size=new int[1];
            glGetActiveUniformBlockiv(program,index,GL_UNIFORM_BLOCK_DATA_SIZE,size,0);
            byte[] bytes=asset(slot.folder+row.getString(light ? "light" : "dark"));
            if (size[0] != bytes.length || bytes.length != row.getInt("bytes"))
                throw new IllegalStateException("Unexpected driver block size");
            glUniformBlockBinding(program,index,i);
            int id=slot.addBuffer(GL_UNIFORM_BUFFER,bytes);
            glBindBufferBase(GL_UNIFORM_BUFFER,i,id);
        }
    }

    private void bindTextures(Slot slot, String control) throws Exception {
        for (int i=0; i<slot.samplers.length(); i++) {
            JSONObject row=slot.samplers.getJSONObject(i);
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
            slot.textures.add(ids[0]);
            glActiveTexture(GL_TEXTURE0+i);
            glBindTexture(target,ids[0]);
            glTexParameteri(target,GL_TEXTURE_WRAP_S,source ? GL_REPEAT : GL_CLAMP_TO_EDGE);
            glTexParameteri(target,GL_TEXTURE_WRAP_T,source ? GL_REPEAT : GL_CLAMP_TO_EDGE);
            glTexParameteri(target,GL_TEXTURE_MAG_FILTER,GL_LINEAR);
            glTexParameteri(target,GL_TEXTURE_MIN_FILTER,source ? GL_LINEAR_MIPMAP_NEAREST : GL_LINEAR);
            JSONObject layout=source && slot.layouts!=null ? slot.layouts.getJSONObject(role) : null;
            int levels=layout==null ? 11 : layout.getInt("levels");
            int width=layout==null ? 1024 : layout.getInt("width");
            int height=layout==null ? 1024 : layout.getInt("height");
            int colorSpace=layout==null ? (role.equals("normal") ? 0 : 1) : layout.getInt("source_color_space");
            if (width<1 || height<1 || width>2048 || height>2048 ||
                    levels!=32-Integer.numberOfLeadingZeros(Math.max(width,height)) ||
                    (colorSpace!=0 && colorSpace!=1))
                throw new IllegalStateException("Invalid source mip layout");
            glTexParameteri(target,GL_TEXTURE_MAX_LEVEL,source && !replaced ? levels-1 : 0);
            int format=source && colorSpace==1 ? GL_SRGB8_ALPHA8 : GL_RGBA8;
            byte[] black={0,0,0,(byte)255};
            if (source && !replaced) {
                int capacity=width*height*4;
                if (mipUpload==null || mipUpload.capacity()<capacity)
                    mipUpload=ByteBuffer.allocateDirect(capacity);
                try (InputStream input=getAssets().open(slot.textureFolder+role+".rgba")) {
                    for (int mip=0; mip<levels; mip++) {
                        int w=Math.max(1,width>>mip), h=Math.max(1,height>>mip);
                        mipUpload.clear();
                        int remaining=w*h*4;
                        while (remaining>0) {
                            int read=input.read(mipChunk,0,Math.min(remaining,mipChunk.length));
                            if (read<0) throw new IllegalStateException("Truncated mip chain");
                            mipUpload.put(mipChunk,0,read);
                            remaining-=read;
                        }
                        mipUpload.flip();
                        glTexImage2D(target,mip,format,w,h,0,GL_RGBA,GL_UNSIGNED_BYTE,mipUpload);
                    }
                    if (input.read()!=-1) throw new IllegalStateException("Unexpected mip chain length");
                }
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
            int location=glGetUniformLocation(slot.program,row.getString("name"));
            if (location<0) throw new IllegalStateException("Expected combined sampler missing");
            glUniform1i(location,i);
        }
    }

    private JSONObject capture(String name, String referencePath) throws Exception {
        ByteBuffer pixels=ByteBuffer.allocateDirect(SIZE*SIZE*4);
        glReadPixels(0,0,SIZE,SIZE,GL_RGBA,GL_UNSIGNED_BYTE,pixels);
        check("Forward draw " + name);
        byte[] raw=new byte[pixels.capacity()];
        pixels.position(0);
        pixels.get(raw);
        byte[] reference=asset(referencePath);
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

    private final class Slot implements AutoCloseable {
        final String folder, textureFolder;
        final JSONArray blocks, samplers;
        final JSONObject layouts;
        final List<Integer> buffers=new ArrayList<>();
        final List<Integer> textures=new ArrayList<>();
        int program, vao, indexCount, vertexBuffer, meshBytes;

        Slot(String id) throws Exception { this(id,null); }

        Slot(String id, Slot textureSource) throws Exception {
            if (!id.matches("M[0-9]{2}-[0-9]+(?:-add|-anim)?")) throw new IllegalArgumentException("Invalid slot identifier");
            folder=id+"/";
            textureFolder=textureSource==null ? folder : textureSource.textureFolder;
            JSONObject scene=new JSONObject(new String(asset(folder+"scene.json"),StandardCharsets.UTF_8));
            blocks=scene.getJSONArray("blocks");
            samplers=scene.getJSONArray("samplers");
            layouts=textureSource==null ? scene.optJSONObject("textures") : textureSource.layouts;
            if (blocks.length()!=8 || samplers.length()!=(id.endsWith("-add") ? 4 : 7)) throw new IllegalStateException("Wrong fixture shape");
        }

        int addBuffer(int target, byte[] bytes) {
            int id=buffer(target,bytes);
            buffers.add(id);
            return id;
        }

        void setup() throws Exception {
            program=createProgram(folder);
            byte[] mesh=asset(folder+"mesh.bin"), indices=asset(folder+"indices.bin");
            if (mesh.length==0 || mesh.length%48!=0 || indices.length==0 || indices.length%6!=0)
                throw new IllegalStateException("Wrong indexed mesh shape");
            indexCount=indices.length/2;
            int[] ids=new int[1];
            glGenVertexArrays(1,ids,0);
            vao=ids[0];
            glBindVertexArray(vao);
            vertexBuffer=addBuffer(GL_ARRAY_BUFFER,mesh);
            meshBytes=mesh.length;
            int[][] attributes={{0,3,0},{1,3,12},{2,2,40},{4,4,24}};
            for (int[] row:attributes) {
                glVertexAttribPointer(row[0],row[1],GL_FLOAT,false,48,row[2]);
                glEnableVertexAttribArray(row[0]);
            }
            glVertexAttrib2f(3,0,0);
            addBuffer(GL_ELEMENT_ARRAY_BUFFER,indices);
        }

        void loadPose(String name) throws Exception {
            if (!name.matches("C[0-2]P[0-4]")) throw new IllegalArgumentException("Invalid animation sample");
            byte[] mesh=asset(folder+name+".bin");
            if (mesh.length!=meshBytes) throw new IllegalStateException("Wrong animated mesh size");
            glBindBuffer(GL_ARRAY_BUFFER,vertexBuffer);
            glBufferSubData(GL_ARRAY_BUFFER,0,mesh.length,direct(mesh,0,mesh.length));
        }

        void drawAdd(String control) throws Exception {
            glEnable(GL_BLEND);
            glBlendFuncSeparate(GL_ONE,GL_ONE,GL_ZERO,GL_ONE);
            glDepthMask(false);
            glDepthFunc(control.equals("reject") ? GL_NEVER : GL_LEQUAL);
            try {
                draw(control.equals("off") ? "dark" : "light");
            } finally {
                glDepthFunc(GL_LESS);
                glDepthMask(true);
                glDisable(GL_BLEND);
            }
        }

        void draw(String control) throws Exception {
            glUseProgram(program);
            glBindVertexArray(vao);
            try {
                bindBlocks(this,!control.equals("dark"));
                bindTextures(this,control);
                glDrawElements(GL_TRIANGLES,indexCount,GL_UNSIGNED_SHORT,0);
                check(folder+control);
            } finally {
                deleteTextures();
            }
        }

        private void deleteTextures() {
            for (int id:textures) glDeleteTextures(1,new int[]{id},0);
            textures.clear();
        }

        @Override public void close() {
            deleteTextures();
            glUseProgram(0);
            glBindVertexArray(0);
            for (int id:buffers) glDeleteBuffers(1,new int[]{id},0);
            if (vao!=0) glDeleteVertexArrays(1,new int[]{vao},0);
            if (program!=0) glDeleteProgram(program);
        }
    }

    private void probe() {
        JSONObject summary=new JSONObject();
        int[] fbo=new int[1], color=new int[1], depth=new int[1];
        try {
            summary.put("experiment","GFX124").put("renderer",glGetString(GL_RENDERER))
                .put("gles",glGetString(GL_VERSION)).put("phase_closed",false);
            JSONArray tests=new JSONObject(new String(asset("batch.json"),StandardCharsets.UTF_8)).getJSONArray("tests");
            if (tests.length()==0) throw new IllegalStateException("Empty test batch");
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
            glViewport(0,0,SIZE,SIZE);
            glEnable(GL_DEPTH_TEST);
            glDepthFunc(GL_LESS);
            glDepthMask(true);
            glClearDepthf(1);
            glDisable(GL_DITHER);
            glDisable(GL_BLEND);
            glDisable(GL_CULL_FACE);
            glClearColor(0,0,0,0);
            JSONArray runs=new JSONArray();
            summary.put("tests",runs);
            int completed=0;
            for (int i=0;i<tests.length();i++) {
                JSONObject test=tests.getJSONObject(i);
                String id=test.getString("id"), primary=test.getString("primary");
                if (!id.matches("M[0-9]{2}-(?:[0-9]+|combined|forward-add|animation)")) throw new IllegalArgumentException("Invalid test identifier");
                JSONObject run=new JSONObject().put("id",id);
                runs.put(run);
                JSONArray captures=new JSONArray();
                run.put("captures",captures);
                try (Slot first=new Slot(primary)) {
                    if (!test.has("animation")) first.setup();
                    if (test.has("animation")) {
                        try (Slot animated=new Slot(test.getString("animation"),first)) {
                            animated.setup();
                            bindBlocks(animated,true);
                            bindTextures(animated,"light");
                            for (int clip=0;clip<3;clip++) {
                                for (int pose=0;pose<5;pose++) {
                                    String sample="C"+clip+"P"+pose;
                                    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);
                                    animated.loadPose(sample);
                                    glDrawElements(GL_TRIANGLES,animated.indexCount,GL_UNSIGNED_SHORT,0);
                                    captures.put(capture(id+"-"+sample,animated.folder+sample+".rgba"));
                                }
                            }
                        }
                    } else if (test.has("forward_add")) {
                        try (Slot added=new Slot(test.getString("forward_add"),first)) {
                            added.setup();
                            for (String control:new String[]{"lit","off","reject"}) {
                                glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);
                                first.draw("light");
                                added.drawAdd(control);
                                String reference=control.equals("lit") ? added.folder+"combined.rgba" : first.folder+"light.rgba";
                                captures.put(capture(id+"-"+control,reference));
                            }
                        }
                    } else if (test.has("secondary")) {
                        try (Slot second=new Slot(test.getString("secondary"))) {
                            second.setup();
                            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);
                            first.draw("light");
                            second.draw("light");
                            captures.put(capture(id,first.folder+"combined.rgba"));
                        }
                    } else {
                        for (String control:new String[]{"light","dark","flat","nonmetal"}) {
                            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);
                            first.draw(control);
                            captures.put(capture(id+"-"+control,first.folder+control+".rgba"));
                        }
                    }
                    completed++;
                    run.put("draw_completed",true);
                } catch (Exception ex) {
                    run.put("draw_completed",false).put("error",ex.toString());
                    for (int n=0;n<16 && glGetError()!=GL_NO_ERROR;n++) { /* Drain queued errors. */ }
                }
            }
            summary.put("planned_tests",tests.length()).put("completed_tests",completed);
            result="اكتمل الرسم في "+completed+" من "+tests.length()+" حالات.";
        } catch (Exception ex) {
            result="تعذّر بدء دفعة الاختبار.";
            try { summary.put("error",ex.toString()); }
            catch (Exception invalid) { display(invalid.toString()); return; }
        } finally {
            mipUpload=null;
            glBindFramebuffer(GL_FRAMEBUFFER,0);
            glDeleteFramebuffers(1,fbo,0);
            glDeleteTextures(1,color,0);
            glDeleteRenderbuffers(1,depth,0);
        }
        report=summary.toString().getBytes(StandardCharsets.UTF_8);
        export();
    }

    private void export() {
        new Thread(new Runnable() { @Override public void run() { writeReport(); } }).start();
    }

    private synchronized void writeReport() {
        Uri uri = null;
        String name = "GFX124-ALL-TEST-LOGS-" + System.currentTimeMillis() + ".zip";
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
