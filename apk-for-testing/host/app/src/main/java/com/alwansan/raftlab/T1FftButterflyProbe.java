package com.alwansan.raftlab;

import android.opengl.GLES20;
import android.opengl.GLES30;
import android.opengl.GLES31;

import java.nio.Buffer;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;

/**
 * T1-05: real on-device GLES compute/SSBO numerical test, not original Raft.
 * Both GLSL programs are fixed in this APK. JSON testpacks may select the
 * already compiled driver by ID, but cannot inject or replace shader source.
 *
 * Two passes use 512 local invocations, one workgroup each, 512 complex
 * samples (1024 floats) and an SSBO barrier. A separate CPU float reference
 * compares every component; GLSL validation is not mistaken for pixels or a
 * Unity FindKernel/Dispatch proof.
 */
final class T1FftButterflyProbe {
    private static final int N = 512;
    private static final int BYTES = N * 2 * Float.BYTES;
    private static final float TWIDDLE = 0.70710678f;
    private static final float TOL = 0.00003f;

    private static final String INIT =
        "#version 310 es\n" +
        "precision highp float; precision highp int;\n" +
        "layout(local_size_x=512,local_size_y=1,local_size_z=1) in;\n" +
        "layout(std430,binding=0) buffer Samples { vec2 s[]; };\n" +
        "void main(){ uint i=gl_GlobalInvocationID.x; if(i<512u)\n" +
        " s[i]=vec2(float(i%19u)/19.0, float((i*7u)%29u)/29.0); }\n";

    private static final String BUTTERFLY =
        "#version 310 es\n" +
        "precision highp float; precision highp int;\n" +
        "layout(local_size_x=512,local_size_y=1,local_size_z=1) in;\n" +
        "layout(std430,binding=0) buffer Samples { vec2 s[]; };\n" +
        "void main(){ uint p=gl_GlobalInvocationID.x; if(p<256u){\n" +
        " uint i=p*2u; vec2 a=s[i]; vec2 b=s[i+1u];\n" +
        " const float k=0.70710678; vec2 t=vec2((b.x+b.y)*k,(b.y-b.x)*k);\n" +
        " s[i]=a+t; s[i+1u]=a-t; } }\n";

    private T1FftButterflyProbe() {}

    static String run() {
        int[] queried = new int[1];
        GLES31.glGetIntegeri_v(GLES31.GL_MAX_COMPUTE_WORK_GROUP_SIZE,0,queried,0);
        int maxLocalX=queried[0];
        GLES20.glGetIntegerv(GLES31.GL_MAX_COMPUTE_WORK_GROUP_INVOCATIONS,queried,0);
        int maxInvocations=queried[0];
        int limitError=GLES20.glGetError();
        if(limitError!=GLES20.GL_NO_ERROR)
            return "FAIL fft_limits_gl_error=0x"+Integer.toHexString(limitError);
        if(maxLocalX<N||maxInvocations<N)
            return "FAIL fft_local512_unsupported max_local_x="+maxLocalX+
                   " max_invocations="+maxInvocations;

        int[] handles=new int[1];
        int init=0,butterfly=0;
        try {
            init=compile(INIT);
            butterfly=compile(BUTTERFLY);
            GLES30.glGenBuffers(1,handles,0);
            if(handles[0]==0)throw new IllegalStateException("FFT SSBO allocation=0");
            GLES30.glBindBuffer(GLES31.GL_SHADER_STORAGE_BUFFER,handles[0]);
            ByteBuffer zero=ByteBuffer.allocateDirect(BYTES).order(ByteOrder.nativeOrder());
            GLES30.glBufferData(GLES31.GL_SHADER_STORAGE_BUFFER,BYTES,zero,GLES30.GL_DYNAMIC_DRAW);
            GLES31.glBindBufferBase(GLES31.GL_SHADER_STORAGE_BUFFER,0,handles[0]);

            GLES20.glUseProgram(init);
            GLES31.glDispatchCompute(1,1,1);
            GLES31.glMemoryBarrier(GLES31.GL_SHADER_STORAGE_BARRIER_BIT);
            GLES20.glUseProgram(butterfly);
            GLES31.glDispatchCompute(1,1,1);
            GLES31.glMemoryBarrier(GLES31.GL_SHADER_STORAGE_BARRIER_BIT |
                                    GLES31.GL_BUFFER_UPDATE_BARRIER_BIT);
            int dispatchError=GLES20.glGetError();
            if(dispatchError!=GLES20.GL_NO_ERROR)
                return "FAIL fft_dispatch_gl_error=0x"+Integer.toHexString(dispatchError);

            GLES30.glBindBuffer(GLES31.GL_SHADER_STORAGE_BUFFER,handles[0]);
            Buffer raw=GLES30.glMapBufferRange(GLES31.GL_SHADER_STORAGE_BUFFER,0,
                                               BYTES,GLES30.GL_MAP_READ_BIT);
            if(!(raw instanceof ByteBuffer))
                return "FAIL fft_readback_null_no_gpu_proof";
            ByteBuffer bytes=((ByteBuffer)raw).order(ByteOrder.nativeOrder());

            float maxError=0f,firstActual=0f,firstExpected=0f;
            int firstMismatch=-1,checked=0;
            for(int pair=0;pair<N/2;pair++) {
                int i=pair*2,j=i+1;
                float ar=(i%19)/19.0f,ai=((i*7)%29)/29.0f;
                float br=(j%19)/19.0f,bi=((j*7)%29)/29.0f;
                float tr=(br+bi)*TWIDDLE,ti=(bi-br)*TWIDDLE;
                // The CPU reference does not read GPU results as inputs.
                float[] expected={ar+tr,ai+ti,ar-tr,ai-ti};
                for(int channel=0;channel<4;channel++) {
                    int index=i*2+channel;
                    float actual=bytes.getFloat(index*Float.BYTES);
                    float error=Math.abs(actual-expected[channel]);
                    checked++;
                    if(Float.isFinite(error))maxError=Math.max(maxError,error);
                    if((!Float.isFinite(actual)||error>TOL)&&firstMismatch<0) {
                        firstMismatch=index;firstActual=actual;
                        firstExpected=expected[channel];
                    }
                }
            }
            boolean unmapped=GLES30.glUnmapBuffer(GLES31.GL_SHADER_STORAGE_BUFFER);
            int finalError=GLES20.glGetError();
            boolean pass=firstMismatch<0&&checked==N*2&&unmapped&&
                         finalError==GLES20.GL_NO_ERROR;
            return (pass?"PASS":"FAIL")+" fft_synthetic_two_pass_local512"+
                " checked_floats="+checked+" max_abs_error="+maxError+
                " tolerance="+TOL+" first_mismatch="+firstMismatch+
                (firstMismatch<0?"":" actual="+firstActual+" expected="+firstExpected)+
                " unmap="+unmapped+" gl_error=0x"+Integer.toHexString(finalError)+
                " original_raft_compute_executed=false";
        } finally {
            GLES20.glUseProgram(0);
            GLES31.glBindBufferBase(GLES31.GL_SHADER_STORAGE_BUFFER,0,0);
            GLES30.glBindBuffer(GLES31.GL_SHADER_STORAGE_BUFFER,0);
            if(handles[0]!=0)GLES30.glDeleteBuffers(1,handles,0);
            if(init!=0)GLES20.glDeleteProgram(init);
            if(butterfly!=0)GLES20.glDeleteProgram(butterfly);
        }
    }

    private static int compile(String source) {
        int shader=GLES20.glCreateShader(GLES31.GL_COMPUTE_SHADER);
        if(shader==0)throw new IllegalStateException("glCreateShader=0");
        try {
            GLES20.glShaderSource(shader,source);
            GLES20.glCompileShader(shader);
            int[] status=new int[1];
            GLES20.glGetShaderiv(shader,GLES20.GL_COMPILE_STATUS,status,0);
            if(status[0]!=GLES20.GL_TRUE)
                throw new IllegalStateException("FFT shader compile: "+bounded(GLES20.glGetShaderInfoLog(shader)));
            int program=GLES20.glCreateProgram();
            if(program==0)throw new IllegalStateException("glCreateProgram=0");
            GLES20.glAttachShader(program,shader);
            GLES20.glLinkProgram(program);
            GLES20.glGetProgramiv(program,GLES20.GL_LINK_STATUS,status,0);
            if(status[0]!=GLES20.GL_TRUE) {
                String message=bounded(GLES20.glGetProgramInfoLog(program));
                GLES20.glDeleteProgram(program);
                throw new IllegalStateException("FFT program link: "+message);
            }
            return program;
        } finally {
            GLES20.glDeleteShader(shader);
        }
    }

    private static String bounded(String text) {
        return text==null?"":text.substring(0,Math.min(text.length(),200)).replace('\n',' ');
    }
}
