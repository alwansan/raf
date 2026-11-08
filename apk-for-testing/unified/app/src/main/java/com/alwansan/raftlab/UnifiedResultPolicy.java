package com.alwansan.raftlab;

/** Pure Java rules for cached test evidence; no synthetic result can become PASS here. */
final class UnifiedResultPolicy {
    private UnifiedResultPolicy() { }

    static boolean reusable(String status, boolean fingerprintMatches,
                            boolean screenshotRequired, boolean screenshotReadable) {
        if (!fingerprintMatches) return false;
        if ("PASS".equals(status) || "USER_PASS".equals(status)
                || "EVIDENCE_READY".equals(status)) {
            return !screenshotRequired || screenshotReadable;
        }
        // Failures are cached failures, not successful tests. Keep them visible for review
        // until their inputs/driver change or the user explicitly requests a force rerun.
        return "FAIL".equals(status) || "USER_FAIL".equals(status)
                || "BLOCKED".equals(status);
    }

    static boolean pending(String mode, String status, boolean reusable) {
        if (reusable) return !"PASS".equals(status) && !"USER_PASS".equals(status);
        return "manual".equals(mode) || "assisted".equals(mode)
                || "NEEDS_INPUT".equals(status) || "NEEDS_SCREENSHOT".equals(status)
                || "EVIDENCE_READY".equals(status) || "FAIL".equals(status)
                || "USER_FAIL".equals(status) || "BLOCKED".equals(status);
    }

    static boolean passed(String status, boolean reusable) {
        return reusable && ("PASS".equals(status) || "USER_PASS".equals(status));
    }
}
