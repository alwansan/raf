package com.alwansan.raftlab;

/**
 * Pure Java screenshot integrity gate. GPU readback and PixelCopy SurfaceView
 * must describe the same pixels before a PNG is released as EVIDENCE_READY.
 * This never grades the visual test PASS; it only rejects mismatched evidence.
 */
public final class SharedSurfacePixelPolicy {
    public static final int MAX_RGB_DELTA = 18;
    private SharedSurfacePixelPolicy() {}

    /** RGBA byte order from GLES30.glReadPixels, and ARGB int from Bitmap.getPixel. */
    public static int[] bitmapPixelToRgba(int argb) {
        return new int[]{(argb >>> 16) & 255, (argb >>> 8) & 255, argb & 255, (argb >>> 24) & 255};
    }

    public static String validate(int[] gpuLeft,int[] gpuRight,int[] imageLeft,int[] imageRight) {
        if(!valid(gpuLeft)||!valid(gpuRight)||!valid(imageLeft)||!valid(imageRight))
            return "invalid RGBA pixel tuples";
        if(dark(imageLeft)&&dark(imageRight))
            return "image SurfaceView is blank/black although GLES rendered this case";
        if(!close(gpuLeft,imageLeft)||!close(gpuRight,imageRight))
            return "PixelCopy SurfaceView pixels differ from GLES readback; refuse stale/blank capture";
        return null;
    }

    private static boolean valid(int[] color) {
        if(color==null||color.length!=4)return false;
        for(int value:color)if(value<0||value>255)return false;
        return true;
    }

    private static boolean dark(int[] color) {
        return Math.max(color[0],Math.max(color[1],color[2]))<=8;
    }

    private static boolean close(int[] a,int[] b) {
        for(int i=0;i<3;i++)if(Math.abs(a[i]-b[i])>MAX_RGB_DELTA)return false;
        return a[3]>=128&&b[3]>=128;
    }
}
