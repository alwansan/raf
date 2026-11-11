package com.alwansan.gfx109;

import android.app.Activity;
import android.content.ContentValues;
import android.net.Uri;
import android.graphics.Bitmap;
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
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;
import javax.microedition.khronos.egl.EGLConfig;
import javax.microedition.khronos.opengles.GL10;

import static android.opengl.GLES30.*;

public final class MainActivity extends Activity {
    private static final String[] SNAPSHOTS = {"M00", "M01", "M02", "M04", "M05"};
    private static final String DIRECTORY = "Download/Games/cl/test/g/";
    private static final int STRIDE = 56;
    private static final String VERTEX = "#version 300 es\n"
        + "precision highp float; precision highp int;\n"
        + "layout(location=0) in vec3 position; layout(location=1) in vec4 weight;\n"
        + "layout(location=2) in uvec4 bone; layout(std140) uniform Palette { mat4 matrices[100]; };\n"
        + "out vec3 skinned; uniform bool uRaster; uniform mat4 uCamera;\n"
        + "void main() { vec4 p=vec4(position,1.0); skinned=vec3(0.0);\n"
        + "for (int i=0;i<4;++i) if (weight[i]>0.0) { vec4 q=matrices[bone[i]]*p;\n"
        + "skinned+=weight[i]*(q.xyz/q.w); } gl_Position=uRaster ? uCamera*vec4(skinned,1.0) : vec4(0.0,0.0,0.0,1.0); }\n";
    private static final String FRAGMENT = "#version 300 es\n"
        + "precision mediump float; out vec4 color; void main(){color=vec4(1.0);}\n";

    private String experiment() {
        if ("com.alwansan.gfx114".equals(getPackageName())) return "GFX114";
        return "com.alwansan.gfx112".equals(getPackageName()) ? "GFX112" : "GFX109";
    }

    private String[] cases() {
        if ("GFX109".equals(experiment())) return SNAPSHOTS;
        String[] poses = new String[15];
        for (int i = 0; i < poses.length; i++) poses[i] = "C" + (i / 5) + "P" + (i % 5);
        return poses;
    }

    private static final int SIDE = 256;
    private final Map<String, byte[]> images = new LinkedHashMap<>();

    private TextView status;
    private GLSurfaceView surface;
    private volatile byte[] report;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        status = new TextView(this);
        status.setText(experiment() + ": comparing source vertices on the GPU…");
        layout.addView(status);
        Button export = new Button(this);
        export.setText("Export ZIP");
        export.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View view) { if (report != null) exportReport(); }
        });
        layout.addView(export);
        surface = new GLSurfaceView(this);
        surface.setEGLContextClientVersion(3);
        surface.setRenderer(new GLSurfaceView.Renderer() {
            public void onSurfaceCreated(GL10 ignored, EGLConfig config) { if (report == null) runProbe(); }
            public void onSurfaceChanged(GL10 ignored, int width, int height) { glViewport(0, 0, width, height); }
            public void onDrawFrame(GL10 ignored) { glClear(GL_COLOR_BUFFER_BIT); }
        });
        surface.setRenderMode(GLSurfaceView.RENDERMODE_WHEN_DIRTY);
        layout.addView(surface, new LinearLayout.LayoutParams(-1, 0, 1));
        setContentView(layout);
    }

    @Override protected void onPause() { surface.onPause(); super.onPause(); }
    @Override protected void onResume() { super.onResume(); surface.onResume(); }

    private void display(final String message) {
        runOnUiThread(new Runnable() {
            @Override public void run() { status.setText(message); }
        });
    }

    private static int compile(int type, String source) {
        int shader = glCreateShader(type);
        glShaderSource(shader, source);
        glCompileShader(shader);
        int[] result = new int[1];
        glGetShaderiv(shader, GL_COMPILE_STATUS, result, 0);
        if (result[0] == 0) throw new IllegalStateException(glGetShaderInfoLog(shader));
        return shader;
    }

    private static int program() {
        int vertex = compile(GL_VERTEX_SHADER, VERTEX);
        int fragment = compile(GL_FRAGMENT_SHADER, FRAGMENT);
        int program = glCreateProgram();
        glAttachShader(program, vertex);
        glAttachShader(program, fragment);
        glTransformFeedbackVaryings(program, new String[]{"skinned"}, GL_INTERLEAVED_ATTRIBS);
        glLinkProgram(program);
        glDeleteShader(vertex);
        glDeleteShader(fragment);
        int[] result = new int[1];
        glGetProgramiv(program, GL_LINK_STATUS, result, 0);
        if (result[0] == 0) throw new IllegalStateException(glGetProgramInfoLog(program));
        int block = glGetUniformBlockIndex(program, "Palette");
        if (block < 0) throw new IllegalStateException("Palette uniform block missing");
        glUniformBlockBinding(program, block, 0);
        return program;
    }

    private byte[] asset(String name) throws Exception {
        try (InputStream in = getAssets().open(name);
             ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[8192];
            for (int length; (length = in.read(buffer)) != -1;) out.write(buffer, 0, length);
            return out.toByteArray();
        }
    }

    private JSONObject compare(String model, int program) throws Exception {
        byte[] bytes = asset(model + ".bin");
        ByteBuffer source = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN);
        int magic = source.getInt();
        int vertices = source.getInt();
        int bones = source.getInt();
        if (magic != 0x39303147 || vertices < 1 || vertices > 150000 || bones < 1 || bones > 100
            || source.remaining() != bones * 64 + vertices * STRIDE) {
            throw new IllegalStateException("Invalid input shape for " + model);
        }
        ByteBuffer palette = ByteBuffer.allocateDirect(6400);
        palette.put(bytes, source.position(), bones * 64).position(0);
        int start = source.position() + bones * 64;
        ByteBuffer input = ByteBuffer.allocateDirect(vertices * STRIDE);
        input.put(bytes, start, vertices * STRIDE).flip();

        int[] buffers = new int[3];
        int[] arrays = new int[1];
        int[] query = new int[1];
        glGenBuffers(3, buffers, 0);
        glGenVertexArrays(1, arrays, 0);
        glGenQueries(1, query, 0);
        glBindVertexArray(arrays[0]);
        try {
            glUseProgram(program);
            glBindBuffer(GL_UNIFORM_BUFFER, buffers[0]);
            glBufferData(GL_UNIFORM_BUFFER, 6400, palette, GL_STATIC_DRAW);
            glBindBufferBase(GL_UNIFORM_BUFFER, 0, buffers[0]);
            glBindBuffer(GL_ARRAY_BUFFER, buffers[1]);
            glBufferData(GL_ARRAY_BUFFER, input.remaining(), input, GL_STATIC_DRAW);
            glVertexAttribPointer(0, 3, GL_FLOAT, false, STRIDE, 0);
            glVertexAttribPointer(1, 4, GL_FLOAT, false, STRIDE, 12);
            glVertexAttribIPointer(2, 4, GL_UNSIGNED_INT, STRIDE, 28);
            for (int i = 0; i < 3; i++) glEnableVertexAttribArray(i);

            int resultBytes = vertices * 12;
            glBindBuffer(GL_TRANSFORM_FEEDBACK_BUFFER, buffers[2]);
            glBufferData(GL_TRANSFORM_FEEDBACK_BUFFER, resultBytes, null, GL_STREAM_READ);
            glBindBufferBase(GL_TRANSFORM_FEEDBACK_BUFFER, 0, buffers[2]);
            glEnable(GL_RASTERIZER_DISCARD);
            glBeginQuery(GL_TRANSFORM_FEEDBACK_PRIMITIVES_WRITTEN, query[0]);
            glBeginTransformFeedback(GL_POINTS);
            glDrawArrays(GL_POINTS, 0, vertices);
            glEndTransformFeedback();
            glEndQuery(GL_TRANSFORM_FEEDBACK_PRIMITIVES_WRITTEN);
            glDisable(GL_RASTERIZER_DISCARD);
            checkGl("transform feedback");
            int[] written = new int[1];
            glGetQueryObjectuiv(query[0], GL_QUERY_RESULT, written, 0);
            if (written[0] != vertices) throw new IllegalStateException("GPU vertex count mismatch");

            ByteBuffer output = (ByteBuffer) glMapBufferRange(GL_TRANSFORM_FEEDBACK_BUFFER, 0, resultBytes, GL_MAP_READ_BIT);
            if (output == null) throw new IllegalStateException("GPU readback unavailable");
            output.order(ByteOrder.nativeOrder());
            int failingVertices = 0;
            int nonfiniteVertices = 0;
            double maxError = 0;
            try {
                for (int i = 0; i < vertices; i++) {
                    boolean passed = true;
                    boolean finite = true;
                    for (int axis = 0; axis < 3; axis++) {
                        float actual = output.getFloat();
                        float expected = source.getFloat(start + i * STRIDE + 44 + axis * 4);
                        if (!Float.isFinite(actual)) {
                            finite = false;
                            passed = false;
                            continue;
                        }
                        double error = Math.abs((double) actual - expected);
                        maxError = Math.max(maxError, error);
                        passed &= error <= 0.0001 + 0.000001 * Math.abs(expected);
                    }
                    if (!passed) failingVertices++;
                    if (!finite) nonfiniteVertices++;
                }
            } finally {
                if (!glUnmapBuffer(GL_TRANSFORM_FEEDBACK_BUFFER)) {
                    throw new IllegalStateException("GPU mapped buffer invalidated");
                }
            }
            checkGl("readback");
            JSONObject result = new JSONObject().put("model", model).put("vertices", vertices).put("bones", bones)
                .put("gpu_vertices_written", written[0]).put("source_payload_sha256", sha256(bytes)).put("failing_vertices", failingVertices)
                .put("nonfinite_vertices", nonfiniteVertices).put("max_absolute_error", maxError);
            if ("GFX114".equals(experiment())) result.put("raster", raster(model, program));
            return result;
        } finally {
            glBindVertexArray(0);
            glBindBufferBase(GL_TRANSFORM_FEEDBACK_BUFFER, 0, 0);
            glBindBufferBase(GL_UNIFORM_BUFFER, 0, 0);
            glDeleteQueries(1, query, 0);
            glDeleteVertexArrays(1, arrays, 0);
            glDeleteBuffers(3, buffers, 0);
        }
    }

    private JSONObject raster(String model, int program) throws Exception {
        byte[] mesh = asset("raster114.bin");
        byte[] expected = asset(model + ".mask");
        if (mesh.length <= 64 || (mesh.length - 64) % 6 != 0 || expected.length != SIDE * SIDE) {
            throw new IllegalStateException("Wrong raster assets");
        }
        ByteBuffer packed = ByteBuffer.wrap(mesh).order(ByteOrder.LITTLE_ENDIAN);
        float[] camera = new float[16];
        for (int i = 0; i < camera.length; i++) camera[i] = packed.getFloat();
        ByteBuffer indices = ByteBuffer.allocateDirect(mesh.length - 64);
        indices.put(mesh, 64, mesh.length - 64).flip();
        int[] fbo = new int[1], color = new int[1], ebo = new int[1];
        glGenFramebuffers(1, fbo, 0);
        glGenTextures(1, color, 0);
        glGenBuffers(1, ebo, 0);
        int mode = glGetUniformLocation(program, "uRaster");
        int projection = glGetUniformLocation(program, "uCamera");
        if (mode < 0 || projection < 0) throw new IllegalStateException("Raster uniforms missing");
        try {
            glBindTexture(GL_TEXTURE_2D, color[0]);
            glTexStorage2D(GL_TEXTURE_2D, 1, GL_RGBA8, SIDE, SIDE);
            glBindFramebuffer(GL_FRAMEBUFFER, fbo[0]);
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, color[0], 0);
            if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE)
                throw new IllegalStateException("Raster framebuffer incomplete");
            glViewport(0, 0, SIDE, SIDE);
            glDisable(GL_DITHER);
            glDisable(GL_BLEND);
            glDisable(GL_DEPTH_TEST);
            glDisable(GL_CULL_FACE);
            glClearColor(0, 0, 0, 1);
            glClear(GL_COLOR_BUFFER_BIT);
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo[0]);
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.remaining(), indices, GL_STATIC_DRAW);
            glUniformMatrix4fv(projection, 1, false, camera, 0);
            glUniform1i(mode, 1);
            glDrawElements(GL_TRIANGLES, (mesh.length - 64) / 2, GL_UNSIGNED_SHORT, 0);
            ByteBuffer pixels = ByteBuffer.allocateDirect(SIDE * SIDE * 4);
            glReadPixels(0, 0, SIDE, SIDE, GL_RGBA, GL_UNSIGNED_BYTE, pixels);
            checkGl("indexed raster readback");
            int[] argb = new int[SIDE * SIDE];
            int intersection = 0, union = 0, differences = 0;
            for (int y = 0; y < SIDE; y++) {
                for (int x = 0; x < SIDE; x++) {
                    int screen = y * SIDE + x;
                    int gl = ((SIDE - 1 - y) * SIDE + x) * 4;
                    int r = pixels.get(gl) & 255, g = pixels.get(gl + 1) & 255;
                    int b = pixels.get(gl + 2) & 255, a = pixels.get(gl + 3) & 255;
                    if (a != 255 || r != g || r != b || (r != 0 && r != 255))
                        throw new IllegalStateException("Nonbinary raster pixel");
                    boolean actual = r == 255;
                    boolean reference = expected[screen] != 0;
                    if (actual && reference) intersection++;
                    if (actual || reference) union++;
                    if (actual != reference) differences++;
                    argb[screen] = 0xff000000 | (r << 16) | (g << 8) | b;
                }
            }
            Bitmap image = Bitmap.createBitmap(argb, SIDE, SIDE, Bitmap.Config.ARGB_8888);
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            boolean encoded = image.compress(Bitmap.CompressFormat.PNG, 100, out);
            image.recycle();
            if (!encoded) throw new IllegalStateException("PNG encoding failed");
            byte[] png = out.toByteArray();
            String filename = model + ".png";
            images.put(filename, png);
            return new JSONObject().put("image", filename).put("image_sha256", sha256(png))
                .put("reference_sha256", sha256(expected)).put("intersection", intersection)
                .put("union", union).put("different_pixels", differences);
        } finally {
            glUniform1i(mode, 0);
            glBindFramebuffer(GL_FRAMEBUFFER, 0);
            glDeleteBuffers(1, ebo, 0);
            glDeleteTextures(1, color, 0);
            glDeleteFramebuffers(1, fbo, 0);
        }
    }

    private static void checkGl(String operation) {
        int error = glGetError();
        if (error != GL_NO_ERROR) throw new IllegalStateException(operation + " GLES error " + error);
    }

    private static String sha256(byte[] data) throws Exception {
        StringBuilder result = new StringBuilder();
        for (byte b : MessageDigest.getInstance("SHA-256").digest(data)) {
            result.append(Character.forDigit((b & 255) >>> 4, 16)).append(Character.forDigit(b & 15, 16));
        }
        return result.toString();
    }

    private void runProbe() {
        JSONObject result = new JSONObject();
        JSONArray cases = new JSONArray();
        int program = 0;
        try {
            result.put("experiment", experiment()).put("renderer", glGetString(GL_RENDERER))
                .put("gles", glGetString(GL_VERSION)).put("cases", cases).put("phase_closed", false)
                .put("absolute_tolerance", 0.0001).put("relative_tolerance", 0.000001);
            program = program();
            boolean passed = true;
            for (String model : cases()) {
                JSONObject evidence = compare(model, program);
                cases.put(evidence);
                passed &= evidence.getInt("failing_vertices") == 0;
            }
            result.put("gpu_source_position_match", passed);
        } catch (Exception ex) {
            try { result.put("error", ex.toString()).put("gpu_source_position_match", false); }
            catch (Exception invalidReport) { display(invalidReport.toString()); return; }
        } finally {
            if (program != 0) glDeleteProgram(program);
        }
        report = result.toString().getBytes(StandardCharsets.UTF_8);
        exportReport();
    }

    private void exportReport() {
        new Thread(new Runnable() {
            @Override public void run() { writeReport(); }
        }).start();
    }

    private void writeReport() {
        Uri uri = null;
        String name = experiment() + "-ALL-TEST-LOGS-" + System.currentTimeMillis() + ".zip";
        try {
            ContentValues values = new ContentValues();
            values.put(MediaStore.Downloads.DISPLAY_NAME, name);
            values.put(MediaStore.Downloads.MIME_TYPE, "application/zip");
            values.put(MediaStore.Downloads.RELATIVE_PATH, DIRECTORY);
            values.put(MediaStore.Downloads.IS_PENDING, 1);
            uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
            if (uri == null) throw new IllegalStateException("Cannot create download");
            try (OutputStream out = getContentResolver().openOutputStream(uri)) {
                if (out == null) throw new IllegalStateException("Cannot open download");
                try (ZipOutputStream zip = new ZipOutputStream(out)) {
                    zip.putNextEntry(new ZipEntry("summary.json"));
                    zip.write(report);
                    zip.closeEntry();
                    for (Map.Entry<String, byte[]> entry : images.entrySet()) {
                        zip.putNextEntry(new ZipEntry(entry.getKey()));
                        zip.write(entry.getValue());
                        zip.closeEntry();
                    }
                }
            }
            values.clear();
            values.put(MediaStore.Downloads.IS_PENDING, 0);
            if (getContentResolver().update(uri, values, null, null) != 1) {
                throw new IllegalStateException("Cannot publish download");
            }
            display("GPU position match: " + new JSONObject(new String(report, StandardCharsets.UTF_8))
                .optBoolean("gpu_source_position_match") + "\nSaved " + DIRECTORY + name);
        } catch (Exception ex) {
            if (uri != null) getContentResolver().delete(uri, null, null);
            display("Export failed. Tap Export ZIP to retry.\n" + ex);
        }
    }
}
