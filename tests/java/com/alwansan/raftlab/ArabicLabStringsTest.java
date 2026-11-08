package com.alwansan.raftlab;

import java.util.HashSet;
import java.util.Set;

/** Real JVM check: owner sees Arabic titles/instructions/expected in all 29 cases. */
public final class ArabicLabStringsTest {
    public static void main(String[] args) {
        String[] ids={
            "T1-01","T1-02","T1-03","T1-04",
            "T2-01","T2-02","T2-03","T2-04",
            "T3-01","T3-02","T3-03","T3-04","T3-05","T3-06",
            "T4-01","T4-02","T4-03","T4-04","T4-05","T4-06","T4-07","T4-08","T4-09",
            "T5-01","T5-02","T5-03","T5-04","T5-05","T5-06"
        };
        if(ArabicLabStrings.translatedCases()!=29) throw new AssertionError("Expected 29 Arabic cases");
        Set<String> seen=new HashSet<>();
        for(String id:ids){
            if(!seen.add(id))throw new AssertionError("Duplicate "+id);
            for(String value:new String[]{
                ArabicLabStrings.title(id,"EN"),
                ArabicLabStrings.instructions(id,"EN"),
                ArabicLabStrings.expected(id,"EN")
            }){
                if(value==null||value.isEmpty()||value.equals("EN"))
                    throw new AssertionError("Missing Arabic for "+id);
                if(!value.matches("(?s).*[\\u0600-\\u06ff].*"))
                    throw new AssertionError("Missing Arabic letters for "+id+": "+value);
            }
        }
        if(!ArabicLabStrings.title("T1-99","fallback").equals("fallback"))
            throw new AssertionError("External compatible pack fallback broken");
        if(!ArabicLabStrings.status("EVIDENCE_READY").contains("ليس نجاحًا"))
            throw new AssertionError("Never label evidence as actual PASS");
        System.out.println("PASS ArabicLabStrings coverage="+ids.length+" statuses and fallback");
    }
}
