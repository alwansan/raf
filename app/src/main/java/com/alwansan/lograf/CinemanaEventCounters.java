package com.alwansan.lograf;

import org.json.JSONObject;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Numeric-only counters tailored to the Cinemana patched Smali/DEX pipeline.
 * The raw Logcat is preserved separately; this class never retains URLs,
 * download IDs, account data, filenames, stack traces or message text.
 */
final class CinemanaEventCounters {
    private final LinkedHashMap<String,AtomicLong> counters=new LinkedHashMap<>();
    CinemanaEventCounters(){
        for(String name:new String[]{
                "startup_markers","main_looper_blocked","choreographer_frame_skips",
                "ui_frame_trace","filedownloader_events","download_repair_events",
                "download_errors","mkv_queue_enqueued","mkv_queue_started",
                "mkv_ffmpeg_acquired","mkv_ffmpeg_released","mkv_watchdog_stalls",
                "mkv_orphan_removed","mkv_rebuild_started","mkv_worker_errors",
                "subtitle_failures","room_database_errors","player_decoder_events",
                "player_buffering_events","notification_episode_events",
                "java_fatal_exceptions","art_verify_errors","missing_java_classes",
                "java_class_casts","oom_exceptions","native_fatal_signals",
                "android_anrs","android_process_deaths","android_low_memory_kills"
        })counters.put(name,new AtomicLong());
    }
    synchronized void reset(){
        for(AtomicLong counter:counters.values())counter.set(0);
    }
    private void inc(String key){
        AtomicLong count=counters.get(key);
        if(count!=null)count.incrementAndGet();
    }
    void observe(String line,boolean system){
        if(line==null||line.isEmpty())return;
        if(system){
            if(line.contains("am_anr") || line.contains("ANR in com.cinemana.pro"))
                inc("android_anrs");
            if(line.contains("am_proc_died"))inc("android_process_deaths");
            if(line.contains("lmkd") || line.contains("lowmemorykiller") ||
                    line.contains("low memory kill") || line.contains("am_kill"))
                inc("android_low_memory_kills");
            return;
        }
        if(line.contains("CinemanaStartupTrace") || line.contains("PATCH321_BOOT_"))
            inc("startup_markers");
        if(line.contains("main_blocked"))inc("main_looper_blocked");
        if(line.contains("Choreographer") && line.contains("Skipped"))
            inc("choreographer_frame_skips");
        if(line.contains("CinemanaUITrace") || line.contains("ui_performance"))
            inc("ui_frame_trace");
        if(line.contains("FileDownloader") || line.contains("filedownloader"))
            inc("filedownloader_events");
        if(line.contains("download_repair") || line.contains("DownloadRepair129") ||
                line.contains("CinemanaLoadTrace") || line.contains("PATCH319_"))
            inc("download_repair_events");
        if(line.contains("DOWNLOAD_FAILED") || line.contains("FileDownloadException") ||
                line.contains("DownloadTask") && line.contains("ERROR"))
            inc("download_errors");
        if(line.contains("QUEUE_ENQUEUED"))inc("mkv_queue_enqueued");
        if(line.contains("QUEUE_START"))inc("mkv_queue_started");
        if(line.contains("MKV_FFMPEG_SLOT_ACQUIRED"))inc("mkv_ffmpeg_acquired");
        if(line.contains("MKV_FFMPEG_SLOT_RELEASED"))inc("mkv_ffmpeg_released");
        if(line.contains("FFMPEG_STALL") || line.contains("PATCH328_FFMPEG_STALL"))
            inc("mkv_watchdog_stalls");
        if(line.contains("STAGE_ORPHAN_REMOVED"))inc("mkv_orphan_removed");
        if(line.contains("STAGE_REBUILD_STARTED"))inc("mkv_rebuild_started");
        if(line.contains("RECOVERED_ENQUEUE_FAILED") ||
                line.contains("MKV_QUEUE_REJECTED") ||
                line.contains("MKV_AUDIT_FAILURE_CLASS"))
            inc("mkv_worker_errors");
        if((line.contains("subtitle") || line.contains("SUBTITLE")) &&
                (line.contains("FAILED") || line.contains("missing") || line.contains("unresolved")))
            inc("subtitle_failures");
        if(line.contains("SQLiteException") || line.contains("SQLiteDatabaseLocked") ||
                line.contains("ROOM_") && line.contains("FAILED") ||
                line.contains("Too many open files"))
            inc("room_database_errors");
        if(line.contains("MediaCodec") || line.contains("ExoPlayer") ||
                line.contains("H26410SoftwareRenderer") ||
                line.contains("player_diagnostics"))
            inc("player_decoder_events");
        if(line.contains("BUFFERING") || line.contains("player_playback_state=2"))
            inc("player_buffering_events");
        if(line.contains("LocalEpisodeJob") || line.contains("episode_notification") ||
                line.contains("PATCH_NOTIF_") || line.contains("CinemanaEpisode"))
            inc("notification_episode_events");
        if(line.contains("FATAL EXCEPTION"))inc("java_fatal_exceptions");
        if(line.contains("VerifyError"))inc("art_verify_errors");
        if(line.contains("NoClassDefFoundError") || line.contains("ClassNotFoundException"))
            inc("missing_java_classes");
        if(line.contains("ClassCastException"))inc("java_class_casts");
        if(line.contains("OutOfMemoryError"))inc("oom_exceptions");
        if(line.contains("Fatal signal") || line.contains("SIGSEGV") ||
                line.contains("SIGABRT"))inc("native_fatal_signals");
    }
    synchronized JSONObject snapshot(){
        JSONObject o=new JSONObject();
        try {
            for(Map.Entry<String,AtomicLong> entry:counters.entrySet())
                o.put(entry.getKey(),entry.getValue().get());
        }catch(org.json.JSONException ignored){}
        return o;
    }
}
