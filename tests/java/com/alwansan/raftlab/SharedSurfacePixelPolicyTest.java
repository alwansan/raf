package com.alwansan.raftlab;

/** True Java contract: reject owner-observed window-black even when GLES succeeded. */
public final class SharedSurfacePixelPolicyTest {
    private static int checks=0;
    private static void check(boolean ok,String msg){if(!ok)throw new AssertionError(msg);checks++;}
    public static void main(String[] args){
        int[] red={255,0,0,255},blue={0,0,255,255};
        int[] black={0,0,0,255},green={0,255,0,255};
        check(SharedSurfacePixelPolicy.validate(red,blue,red,blue)==null,"real T3 RGB accepted");
        check(SharedSurfacePixelPolicy.validate(red,blue,black,black)!=null,"owner screenshot vs blank PNG rejected");
        check(SharedSurfacePixelPolicy.validate(red,blue,red,black)!=null,"partial black mismatch rejected");
        check(SharedSurfacePixelPolicy.validate(red,blue,blue,red)!=null,"swapped stale frame rejected");
        check(SharedSurfacePixelPolicy.validate(red,blue,red,green)!=null,"wrong color rejected");
        check(SharedSurfacePixelPolicy.validate(red,blue,new int[]{253,2,3,255},new int[]{1,2,250,255})==null,"minor compositor error tolerated");
        check(SharedSurfacePixelPolicy.validate(red,blue,null,blue)!=null,"missing pixel denied");
        check(SharedSurfacePixelPolicy.validate(red,blue,new int[]{256,0,0,255},blue)!=null,"bad rgba denied");
        check(SharedSurfacePixelPolicy.validate(red,blue,new int[]{255,0,0,0},blue)!=null,"missing alpha denied");
        check(SharedSurfacePixelPolicy.bitmapPixelToRgba(0xffe1269b)[0]==0xe1,"argb red decode");
        check(SharedSurfacePixelPolicy.bitmapPixelToRgba(0xffe1269b)[1]==0x26,"argb green decode");
        check(SharedSurfacePixelPolicy.bitmapPixelToRgba(0xffe1269b)[2]==0x9b,"argb blue decode");
        check(SharedSurfacePixelPolicy.bitmapPixelToRgba(0xffe1269b)[3]==255,"argb alpha decode");
        int[] left={128,33,108,255},right={128,33,108,255};
        check(SharedSurfacePixelPolicy.validate(left,right,left,right)==null,"smoke/alpha case valid");
        int[] grey={55,55,55,255};
        check(SharedSurfacePixelPolicy.validate(grey,grey,grey,grey)==null,"sRGB dark gray valid");
        System.out.println("PASS screenshot fidelity checks="+checks);
    }
}
