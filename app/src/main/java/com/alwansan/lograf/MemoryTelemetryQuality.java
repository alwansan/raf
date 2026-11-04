package com.alwansan.lograf;

/**
 * PSS quality. Compare a slow sampled PSS against RSS collected around that
 * SAME sample, not against an unrelated later RSS after memory has changed.
 */
final class MemoryTelemetryQuality {
    private MemoryTelemetryQuality(){}
    static String classify(Long pssKb,Long referenceRssKb,long ageMs){
        if(pssKb==null || pssKb<=0)return "unavailable";
        if(referenceRssKb==null || referenceRssKb<=0)
            return "unverified_no_reference_rss";
        if(pssKb>referenceRssKb+8192L)
            return "android_meminfo_reported_above_proc_rss";
        return ageMs>5000?"validated_cached":"validated_recent";
    }
    static boolean usable(String quality){
        return "validated_recent".equals(quality) || "validated_cached".equals(quality)
                || "android_meminfo_reported_above_proc_rss".equals(quality);
    }
    static boolean comparableToProcRss(String quality){
        return "validated_recent".equals(quality) || "validated_cached".equals(quality);
    }
}
