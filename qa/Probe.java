package org.raft.qa.fixture;

import android.app.Activity;
import android.opengl.GLES20;
import android.opengl.GLSurfaceView;
import android.os.Bundle;
import android.util.Log;
import android.view.MotionEvent;
import javax.microedition.khronos.egl.EGLConfig;
import javax.microedition.khronos.opengles.GL10;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.FloatBuffer;

public final class Probe extends Activity implements GLSurfaceView.Renderer {
    private GLSurfaceView surface;
    private int program;
    private boolean flipped;
    private boolean videoMode;
    private boolean frameReported;
    private boolean reportedFlip;
    private int viewportWidth, viewportHeight;
    private static final String TAG = "RaftQaFixture";
    private final FloatBuffer quad = ByteBuffer.allocateDirect(32)
        .order(ByteOrder.nativeOrder()).asFloatBuffer();

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        quad.put(new float[] {-1,-1, 1,-1, -1,1, 1,1}).position(0);
        surface = new GLSurfaceView(this);
        surface.setEGLContextClientVersion(2);
        surface.setRenderer(this);
        videoMode = getIntent().getBooleanExtra("capture_video", false);
        surface.setRenderMode(videoMode ? GLSurfaceView.RENDERMODE_CONTINUOUSLY
                                        : GLSurfaceView.RENDERMODE_WHEN_DIRTY);
        surface.setOnTouchListener((v, event) -> {
            if (event.getAction() == MotionEvent.ACTION_UP) {
                v.performClick();
                surface.queueEvent(() -> { flipped = !flipped; Log.i(TAG, "TOUCH_ACCEPTED"); });
                surface.requestRender();
            }
            return true;
        });
        setContentView(surface);
    }

    private int shader(int type, String source) {
        int shader = GLES20.glCreateShader(type);
        GLES20.glShaderSource(shader, source);
        GLES20.glCompileShader(shader);
        int[] ok = new int[1];
        GLES20.glGetShaderiv(shader, GLES20.GL_COMPILE_STATUS, ok, 0);
        if (ok[0] == 0) throw new IllegalStateException(GLES20.glGetShaderInfoLog(shader));
        return shader;
    }

    @Override public void onSurfaceCreated(GL10 ignored, EGLConfig config) {
        program = GLES20.glCreateProgram();
        GLES20.glAttachShader(program, shader(GLES20.GL_VERTEX_SHADER,
            "attribute vec2 p; varying vec2 uv; void main(){gl_Position=vec4(p,0.,1.);uv=p;}"));
        GLES20.glAttachShader(program, shader(GLES20.GL_FRAGMENT_SHADER,
            "precision mediump float; varying vec2 uv; uniform float flip;"
            + "void main(){bool left=(uv.x<0.) != (flip>0.5);"
            + "gl_FragColor=left?vec4(1.,0.,0.,1.):vec4(0.,1.,0.,1.);}"));
        GLES20.glBindAttribLocation(program, 0, "p");
        GLES20.glLinkProgram(program);
        int[] ok = new int[1];
        GLES20.glGetProgramiv(program, GLES20.GL_LINK_STATUS, ok, 0);
        if (ok[0] == 0) throw new IllegalStateException(GLES20.glGetProgramInfoLog(program));
        Log.i(TAG, "GL_RENDERER=" + GLES20.glGetString(GLES20.GL_RENDERER)
            + " GL_VERSION=" + GLES20.glGetString(GLES20.GL_VERSION)
            + " GL_VENDOR=" + GLES20.glGetString(GLES20.GL_VENDOR));
    }
    @Override public void onSurfaceChanged(GL10 ignored, int w, int h) {
        viewportWidth = w;
        viewportHeight = h;
        GLES20.glViewport(0, 0, w, h);
    }
    @Override public void onDrawFrame(GL10 ignored) {
        GLES20.glUseProgram(program);
        GLES20.glUniform1f(GLES20.glGetUniformLocation(program, "flip"), flipped ? 1 : 0);
        GLES20.glEnableVertexAttribArray(0);
        GLES20.glVertexAttribPointer(0, 2, GLES20.GL_FLOAT, false, 0, quad);
        GLES20.glDrawArrays(GLES20.GL_TRIANGLE_STRIP, 0, 4);
        if (videoMode && viewportWidth > 0 && viewportHeight > 0) {
            // Keep the encoder receiving changing frames even while both measured
            // color regions are static. This marker cannot touch the sampled row.
            int tick = (int)(android.os.SystemClock.elapsedRealtime() / 125L % 4L);
            GLES20.glEnable(GLES20.GL_SCISSOR_TEST);
            GLES20.glScissor(0, 0, Math.min(16, viewportWidth),
                             Math.min(16, viewportHeight));
            GLES20.glClearColor((tick & 1) != 0 ? 1f : 0f,
                                (tick & 2) != 0 ? 1f : 0f, 1f, 1f);
            GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT);
            GLES20.glDisable(GLES20.GL_SCISSOR_TEST);
        }
        int error = GLES20.glGetError();
        if (error != GLES20.GL_NO_ERROR) throw new IllegalStateException("GLES error: " + error);
        if (!videoMode || !frameReported || reportedFlip != flipped) {
            Log.i(TAG, flipped ? "FRAME_FLIPPED" : "FRAME_BASELINE");
            frameReported = true;
            reportedFlip = flipped;
        }
    }
}
