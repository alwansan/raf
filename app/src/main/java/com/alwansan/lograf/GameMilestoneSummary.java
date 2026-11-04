package com.alwansan.lograf;

import org.json.JSONObject;

/**
 * Fixed, bounded milestones observed solely from Raft-UID Logcat lines.
 * A marker shows a line was emitted, not that its operation completed.
 * Raw paths, stack traces, profiles, and bank data are never retained.
 */
final class GameMilestoneSummary {
    private static final String[] NAMES = {
        "fmod_bootstrap_log_observed",
        "raft_android_early_startup_log_observed",
        "unity_scene_callback_log_observed",
        "player_add_callback_log_observed",
        "world_loaded_message_observed"
    };
    private final long[] count = new long[NAMES.length];
    private final long[] firstObservedUnixMs = new long[NAMES.length];
    private final long[] lastObservedUnixMs = new long[NAMES.length];

    synchronized void reset() {
        for (int i = 0; i < NAMES.length; i++) {
            count[i] = 0;
            firstObservedUnixMs[i] = 0;
            lastObservedUnixMs[i] = 0;
        }
    }

    synchronized void observe(String line) {
        if (line == null) return;
        // Nearly all logcat lines are noise for milestone tracking;
        // skip with an allocation-free fast gate under heavy shader floods.
        if (line.indexOf("RAFT_") < 0 &&
            line.indexOf("Raft_Network:") < 0 &&
            line.indexOf("World has been loaded") < 0) return;
        int index = -1;
        if (line.contains("RAFT_FMOD_ANDROID_BOOTSTRAP")) index = 0;
        else if (line.contains("RAFT_ANDROID_DEVICE_TEST")) index = 1;
        else if (line.contains("Raft_Network:OnSceneLoaded")) index = 2;
        else if (line.contains("Raft_Network:InternalAddPlayer")) index = 3;
        else if (line.contains("World has been loaded")) index = 4;
        if (index < 0) return;
        long observedAt = System.currentTimeMillis();
        count[index]++;
        if (firstObservedUnixMs[index] == 0) firstObservedUnixMs[index] = observedAt;
        lastObservedUnixMs[index] = observedAt;
    }

    synchronized JSONObject snapshot() {
        JSONObject out = new JSONObject();
        try {
            for (int i = 0; i < NAMES.length; i++) {
                if (count[i] == 0) continue;
                JSONObject row = new JSONObject();
                row.put("count", count[i]);
                row.put("first_observed_unix_ms", firstObservedUnixMs[i]);
                row.put("last_observed_unix_ms", lastObservedUnixMs[i]);
                out.put(NAMES[i], row);
            }
        } catch (Exception ignored) {}
        return out;
    }
}
