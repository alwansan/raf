package com.alwansan.raftlab;

public final class UnifiedResultPolicyTest {
    static int checked;
    static void check(boolean expected, boolean actual, String label) {
        ++checked;
        if (expected != actual) throw new AssertionError(label + " expected=" + expected + " got=" + actual);
    }
    public static void main(String[] args) {
        check(true, UnifiedResultPolicy.reusable("EVIDENCE_READY",true,false,false),"file SHA survives AUTO ALL");
        check(false, UnifiedResultPolicy.passed("EVIDENCE_READY",true),"file hash awaits owner review");
        check(true, UnifiedResultPolicy.pending("manual","EVIDENCE_READY",true),"file review stays visible");
        check(true, UnifiedResultPolicy.reusable("EVIDENCE_READY",true,true,true),"real picture cached");
        check(false, UnifiedResultPolicy.reusable("EVIDENCE_READY",true,true,false),"missing picture invalidates cache");
        check(false, UnifiedResultPolicy.reusable("EVIDENCE_READY",false,false,false),"case edit invalidates cache");
        check(true, UnifiedResultPolicy.reusable("FAIL",true,true,false),"failed auto case retained");
        check(true, UnifiedResultPolicy.pending("auto","FAIL",true),"failed auto case visible");
        check(false, UnifiedResultPolicy.passed("FAIL",true),"failure never counted as pass");
        check(true, UnifiedResultPolicy.reusable("USER_FAIL",true,false,false),"human failure retained");
        check(true, UnifiedResultPolicy.pending("manual","USER_FAIL",true),"human failure remains visible");
        check(false, UnifiedResultPolicy.passed("USER_FAIL",true),"human failure never counted as pass");
        check(true, UnifiedResultPolicy.reusable("BLOCKED",true,false,false),"blocked result not silently repeated");
        check(true, UnifiedResultPolicy.pending("auto","BLOCKED",true),"blocked auto remains visible");
        check(true, UnifiedResultPolicy.pending("assisted","",false),"unrun visual request visible");
        check(true, UnifiedResultPolicy.passed("PASS",true),"real auto pass counted");
        check(false, UnifiedResultPolicy.pending("auto","PASS",true),"successful auto case no request");
        check(false, UnifiedResultPolicy.reusable("PASS",true,true,false),"lost required picture invalidates success");
        check(false, UnifiedResultPolicy.reusable("PASS",false,false,false),"changed GPU driver invalidates pass");
        check(false, UnifiedResultPolicy.reusable("NEEDS_INPUT",true,false,false),"unresolved input is not success");
        System.out.println("UnifiedResultPolicy: " + checked + " checks PASS");
    }
}
