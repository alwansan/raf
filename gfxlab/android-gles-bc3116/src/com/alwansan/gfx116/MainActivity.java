package com.alwansan.gfx116;

import android.app.Activity;
import android.content.ContentValues;
import android.net.Uri;
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
    private static final int BC3 = 0x83F3, BC3_SRGB = 0x8C4F;
    private static final int SIZE = 1024, MIPS = 11;
    private static final String DIR = "Download/Games/cl/test/g/";
    private static final String VS = "#version 300 es\n"
        + "void main(){vec2 p=vec2((gl_VertexID<<1)&2,gl_VertexID&2);gl_Position=vec4(p*2.0-1.0,0.0,1.0);}";
    private static final String FS = "#version 300 es\n"
        + "precision highp float; uniform highp sampler2D tex; uniform int level; uniform bool srgb;\n"
        + "out vec4 color; void main(){color=texelFetch(tex,ivec2(gl_FragCoord.xy),level);\n"
        + "if(srgb){vec3 v=color.rgb;color.rgb=mix(1.055*pow(v,vec3(1.0/2.4))-0.055,12.92*v,lessThanEqual(v,vec3(0.0031308)));}}";

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
        status.setText("GFX116: جارٍ فحص الخامات الأصلية…");
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

    private JSONObject sample(String mode, byte[] upload, byte[] reference, boolean srgb,
                              boolean compressed, int program) throws Exception {
        JSONObject row = new JSONObject().put("mode", mode);
        int[] ids = new int[1];
        glGenTextures(1, ids, 0);
        glBindTexture(GL_TEXTURE_2D, ids[0]);
        try {
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_NEAREST);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, MIPS - 1);
            int offset = 0;
            for (int level = 0; level < MIPS; level++) {
                int size = SIZE >> level;
                int length = compressed ? ((size + 3) / 4) * ((size + 3) / 4) * 16 : size * size * 4;
                ByteBuffer data = ByteBuffer.allocateDirect(length);
                data.put(upload, offset, length).flip();
                if (compressed)
                    glCompressedTexImage2D(GL_TEXTURE_2D, level, srgb ? BC3_SRGB : BC3, size, size, 0, length, data);
                else
                    glTexImage2D(GL_TEXTURE_2D, level, srgb ? GL_SRGB8_ALPHA8 : GL_RGBA8,
                                 size, size, 0, GL_RGBA, GL_UNSIGNED_BYTE, data);
                int error = glGetError();
                if (error != GL_NO_ERROR) {
                    if (compressed && level == 0 && (error == GL_INVALID_ENUM || error == GL_INVALID_OPERATION))
                        return row.put("status", "NATIVE_FORMAT_REJECTED").put("gl_error", error);
                    throw new IllegalStateException(mode + " upload level " + level + " GL error " + error);
                }
                offset += length;
            }
            if (offset != upload.length) throw new IllegalStateException("Texture size mismatch");
            JSONArray samples = new JSONArray();
            int levelUniform = glGetUniformLocation(program, "level");
            glUniform1i(glGetUniformLocation(program, "srgb"), srgb ? 1 : 0);
            ByteBuffer pixels = ByteBuffer.allocateDirect(SIZE * SIZE * 4);
            int start = 0;
            for (int level = 0; level < MIPS; level++) {
                int size = SIZE >> level;
                glViewport(0, 0, size, size);
                glUniform1i(levelUniform, level);
                glDrawArrays(GL_TRIANGLES, 0, 3);
                glReadPixels(0, 0, size, size, GL_RGBA, GL_UNSIGNED_BYTE, pixels);
                check("texture sample " + level);
                int maximum = 0, overTwo = 0;
                long sum = 0;
                for (int i = 0; i < size*size*4; i++) {
                    int error = Math.abs((pixels.get(i) & 255) - (reference[start + i] & 255));
                    maximum = Math.max(maximum,error);
                    sum += error;
                    if (error > 2) overTwo++;
                }
                samples.put(new JSONObject().put("level",level).put("texels",size*size)
                    .put("max_channel_error",maximum).put("channel_absolute_error_sum",sum)
                    .put("channels_over_two",overTwo));
                start += size*size*4;
            }
            if (start != reference.length) throw new IllegalStateException("Reference size mismatch");
            return row.put("status", "SAMPLED").put("mips", samples);
        } finally {
            glDeleteTextures(1, ids, 0);
        }
    }

    private void probe() {
        JSONObject summary = new JSONObject();
        try {
            summary.put("experiment","GFX116").put("renderer",glGetString(GL_RENDERER))
                .put("gles",glGetString(GL_VERSION)).put("phase_closed",false);
            String ext = glGetString(GL_EXTENSIONS);
            summary.put("s3tc_advertised",ext.contains("GL_EXT_texture_compression_s3tc"))
                .put("s3tc_srgb_advertised",ext.contains("GL_EXT_texture_compression_s3tc_srgb"));
            int program = glCreateProgram();
            int vertex = shader(GL_VERTEX_SHADER, VS), fragment = shader(GL_FRAGMENT_SHADER, FS);
            glAttachShader(program,vertex); glAttachShader(program,fragment); glLinkProgram(program);
            glDeleteShader(vertex); glDeleteShader(fragment);
            int[] ok = new int[1];
            glGetProgramiv(program,GL_LINK_STATUS,ok,0);
            if (ok[0] == 0) throw new IllegalStateException(glGetProgramInfoLog(program));
            glUseProgram(program);
            int[] fbo = new int[1], color = new int[1], vao = new int[1];
            glGenVertexArrays(1,vao,0); glBindVertexArray(vao[0]);
            glGenFramebuffers(1,fbo,0); glBindFramebuffer(GL_FRAMEBUFFER,fbo[0]);
            glGenTextures(1,color,0); glBindTexture(GL_TEXTURE_2D,color[0]);
            glTexStorage2D(GL_TEXTURE_2D,1,GL_RGBA8,SIZE,SIZE);
            glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,color[0],0);
            if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE)
                throw new IllegalStateException("Framebuffer incomplete");
            glDisable(GL_DITHER);
            check("setup");
            JSONArray roles = new JSONArray();
            summary.put("roles",roles);
            int nativeCount = 0;
            for (String role : new String[]{"basecolor","normal","metallic"}) {
                boolean srgb = !"normal".equals(role);
                byte[] bc3 = asset(role + ".bc3"), rgba = asset(role + ".rgba");
                JSONObject nativeResult = sample("native_bc3",bc3,rgba,srgb,true,program);
                JSONObject fallback = sample("decoded_rgba",rgba,rgba,srgb,false,program);
                roles.put(new JSONObject().put("role",role).put("srgb",srgb)
                    .put("bc3_sha256",sha256(bc3)).put("rgba_sha256",sha256(rgba))
                    .put("native",nativeResult).put("fallback",fallback));
                if ("SAMPLED".equals(nativeResult.getString("status"))) nativeCount++;
            }
            summary.put("native_roles_sampled",nativeCount);
            result = "اكتمل فحص 33 مستوى. الخامات التي قرأها الجهاز مباشرة من BC3: " + nativeCount + "/3";
            glBindFramebuffer(GL_FRAMEBUFFER,0);
            glDeleteFramebuffers(1,fbo,0); glDeleteTextures(1,color,0); glDeleteVertexArrays(1,vao,0);
            glDeleteProgram(program);
        } catch (Exception ex) {
            result = "توقف الاختبار. تفاصيل الخطأ في السجل.";
            try { summary.put("error",ex.toString()); }
            catch (Exception invalid) { display(invalid.toString()); return; }
        }
        report = summary.toString().getBytes(StandardCharsets.UTF_8);
        export();
    }

    private void export() {
        new Thread(new Runnable() { @Override public void run() { writeReport(); } }).start();
    }

    private void writeReport() {
        Uri uri = null;
        String name = "GFX116-ALL-TEST-LOGS-" + System.currentTimeMillis() + ".zip";
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
