package com.alwansan.raftlab;

/** Classification and bounded display for documents deliberately shared through Android SAF.
 * This code never implies that an APK/OBB is installed, signed, mounted or correct.
 */
public final class LocalOwnerBundlePolicy {
    private LocalOwnerBundlePolicy() {}

    static String kind(String name, String relativePath) {
        if (name==null || relativePath==null) return "UNKNOWN";
        String n=name.trim();
        if (n.equals("com.alwansan.raft.androidtest.apk")) return "GAME_APK";
        if (n.matches("main\\.[0-9]{1,9}\\.com\\.alwansan\\.raft\\.androidtest\\.obb"))
            return "MAIN_OBB";
        if (n.matches("patch\\.[0-9]{1,9}\\.com\\.alwansan\\.raft\\.androidtest\\.obb"))
            return "PATCH_OBB";
        if (n.equals("manifest.json") && relativePath.contains("Raft-Android-Test/"))
            return "MANIFEST";
        if (n.equals("team-testpack.json")) return "TEAM_PACK";
        if (n.equals("t2-water-render-testpack.json")) return "OLD_T2_PACK";
        if (n.equals("T3.json")) return "OLD_T3_PACK";
        if (n.equals("t4-mouse-testpack.json")) return "OLD_T4_PACK";
        if (n.equals("top.niunaijun.blackbox_logcat.txt")) return "BLACKBOX_LOG";
        return "UNKNOWN";
    }

    static String safeLabel(String source) {
        if (source==null) return "(unnamed)";
        StringBuilder b=new StringBuilder();
        for (int i=0;i<source.length()&&b.length()<110;i++) {
            char c=source.charAt(i);
            if (c<32||c==127||c=='/'||c=='\\')b.append('_');
            else b.append(c);
        }
        return b.length()==0?"(unnamed)":b.toString();
    }

    static boolean isHashCandidate(String kind) {
        return "GAME_APK".equals(kind)||"MAIN_OBB".equals(kind)||"PATCH_OBB".equals(kind);
    }

    static String arabicRole(String kind) {
        switch (kind) {
            case "GAME_APK": return "APK اللعبة (وجود الملف لا يثبت التثبيت)";
            case "MAIN_OBB": return "OBB الرئيسي (وجوده لا يثبت سلامته أو ربطه)";
            case "PATCH_OBB": return "OBB إضافي/patch";
            case "MANIFEST": return "بيان ملفات اللعبة (مصدر غير متحقق)";
            case "TEAM_PACK": return "حزمة الفريق JSON: بيانات فقط";
            case "OLD_T2_PACK": return "حزمة T2 قديمة: لا تُنفّذ تلقائيًا";
            case "OLD_T3_PACK": return "حزمة T3 قديمة: لا تُنفّذ تلقائيًا";
            case "OLD_T4_PACK": return "حزمة T4 قديمة: لا تُنفّذ تلقائيًا";
            case "BLACKBOX_LOG": return "سجل BlackBox: قد يحوي بيانات خاصة، لا يُقرأ تلقائيًا";
            default: return "ملف غير مصنف";
        }
    }
}
