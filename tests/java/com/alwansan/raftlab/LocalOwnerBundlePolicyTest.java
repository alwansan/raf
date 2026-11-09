package com.alwansan.raftlab;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;

/** Source-only JVM guard: no Android/device/OBB claims. */
public final class LocalOwnerBundlePolicyTest {
    private static void ok(boolean condition,String message){
        if(!condition)throw new AssertionError(message);
    }
    private static void kind(String name,String parent,String expected){
        String actual=LocalOwnerBundlePolicy.kind(name,parent);
        ok(expected.equals(actual),name+" expected "+expected+" got "+actual);
    }
    public static void main(String[] args)throws Exception{
        kind("com.alwansan.raft.androidtest.apk","Raft-Android-Test/","GAME_APK");
        kind("main.91.com.alwansan.raft.androidtest.obb",
            "Raft-Android-Test/Android/obb/com.alwansan.raft.androidtest/","MAIN_OBB");
        kind("patch.91.com.alwansan.raft.androidtest.obb",
            "Raft-Android-Test/Android/obb/com.alwansan.raft.androidtest/","PATCH_OBB");
        kind("main.91.com.evil.raft.androidtest.obb","Raft-Android-Test/","UNKNOWN");
        kind("main.91.com.alwansan.raft.androidtest.obb.exe","Raft-Android-Test/","UNKNOWN");
        kind("manifest.json","Raft-Android-Test/","MANIFEST");
        kind("manifest.json","","UNKNOWN");
        kind("team-testpack.json","","TEAM_PACK");
        kind("T3.json","","OLD_T3_PACK");
        kind("t2-water-render-testpack.json","","OLD_T2_PACK");
        kind("t4-mouse-testpack.json","","OLD_T4_PACK");
        kind("top.niunaijun.blackbox_logcat.txt","","BLACKBOX_LOG");
        ok(!LocalOwnerBundlePolicy.isHashCandidate("TEAM_PACK"),"json cannot hash as OBB");
        ok(LocalOwnerBundlePolicy.isHashCandidate("MAIN_OBB"),"main OBB selectable");
        ok(!LocalOwnerBundlePolicy.arabicRole("MAIN_OBB").contains("سليم"),"no implicit OBB PASS");
        ok(LocalOwnerBundlePolicy.safeLabel("log\n../secret\\name").indexOf('\n')<0,"no line breaks");
        String original="UID=2000 alice@example.com ultimate_water_invalid_pass "+
                "water_fft_invalid_compute_kernel dx11fft dx11fft "+ 
                "main.91.com.alwansan.raft.androidtest.obb";
        String result=LocalOwnerLogEvidence.summarize(
            new ByteArrayInputStream(original.getBytes(StandardCharsets.UTF_8)));
        ok(result.contains("ultimate_water_invalid_pass = 1"),"water count");
        ok(result.contains("dx11fft = 2"),"FFT count");
        ok(result.contains("main.91.com.alwansan.raft.androidtest.obb = 1"),"main91 count");
        ok(!result.contains("alice@example.com")&&!result.contains("UID=2000"),"redact raw log");
        try{LocalOwnerLogEvidence.summarize(new ByteArrayInputStream(new byte[0]));
            throw new AssertionError("empty stream accepted");
        }catch(IOException expected){}
        InputStream stuck=new InputStream(){
            @Override public int read(){return 0;}
            @Override public int read(byte[] b,int off,int length){return 0;}
        };
        try{LocalOwnerLogEvidence.summarize(stuck);
            throw new AssertionError("stuck stream accepted");
        }catch(IOException expected){}
        System.out.println("T5 LOCAL OWNER SAF POLICY TESTS: PASS 19 controls");
    }
}
