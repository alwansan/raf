package com.alwansan.lograf;

import org.json.JSONObject;
import org.json.JSONException;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Low-overhead aggregate computed as telemetry arrives on the SAF writer.
 * This is a summary, not an alternative to the raw metrics JSONL stream.
 * Unobserved counters remain null and are never interpreted as zeros.
 */
final class SessionMetricsSummary {
    private static final class Stats {
        long observed;
        double min=Double.POSITIVE_INFINITY,max=Double.NEGATIVE_INFINITY,mean;
        void add(Object value){
            if(!(value instanceof Number))return;
            double n=((Number)value).doubleValue();
            if(!Double.isFinite(n))return;
            observed++;
            min=Math.min(min,n);
            max=Math.max(max,n);
            mean+=(n-mean)/observed;
        }
        JSONObject json() throws JSONException {
            JSONObject result=new JSONObject();
            result.put("readable_samples",observed);
            result.put("min",observed>0?Math.round(min*100.0)/100.0:JSONObject.NULL);
            result.put("max",observed>0?Math.round(max*100.0)/100.0:JSONObject.NULL);
            result.put("mean",observed>0?Math.round(mean*100.0)/100.0:JSONObject.NULL);
            return result;
        }
    }
    private final LinkedHashMap<String,Stats> fields=new LinkedHashMap<>();
    private long total,unreadable,gameRunning,gameAbsent,fpsStale;
    private long firstTimestamp=-1,lastTimestamp=-1;
    private long lastShaderErrors,lastComputeErrors,lastAssetErrors,firstFpsAt=-1,lastFpsAt=-1;
    SessionMetricsSummary(){reset();}
    void reset(){
        fields.clear();
        for(String key:new String[]{"presented_fps_estimate",
                "presented_frame_p95_ms","presented_frame_worst_ms",
                "process_cpu_percent_one_core","process_cpu_percent_all_cores",
                "process_rss_kb","process_pss_kb","process_threads",
                "gpu_busy_percent","gpu_clock_hz",
                "device_mem_available_kb","battery_temp_c",
                "game_log_lines_per_second","last_present_progress_age_ms"}){
            fields.put(key,new Stats());
        }
        total=0;unreadable=0;gameRunning=0;gameAbsent=0;fpsStale=0;
        firstTimestamp=-1;lastTimestamp=-1;firstFpsAt=-1;lastFpsAt=-1;
        lastShaderErrors=0;lastComputeErrors=0;lastAssetErrors=0;
    }
    void add(String raw){
        try{
            JSONObject row=new JSONObject(raw.trim());
            if(!row.has("timestamp_unix_ms")){unreadable++;return;}
            total++;
            long t=row.optLong("timestamp_unix_ms");
            if(firstTimestamp<0)firstTimestamp=t;
            lastTimestamp=t;
            if("game_running".equals(row.optString("state")))gameRunning++;
            if("game_not_running".equals(row.optString("state")))gameAbsent++;
            if(row.optBoolean("frame_telemetry_stale",false))fpsStale++;
            for(Map.Entry<String,Stats> metric:fields.entrySet())
                metric.getValue().add(row.opt(metric.getKey()));
            Object fps=row.opt("presented_fps_estimate");
            if(fps instanceof Number){
                if(firstFpsAt<0)firstFpsAt=t;
                lastFpsAt=t;
            }
            lastShaderErrors=Math.max(lastShaderErrors,row.optLong("shader_pass_errors_total"));
            lastComputeErrors=Math.max(lastComputeErrors,row.optLong("invalid_compute_kernel_total"));
            lastAssetErrors=Math.max(lastAssetErrors,row.optLong("missing_asset_path_errors_total"));
        }catch(Exception err){unreadable++;}
    }
    JSONObject toJson(){
        JSONObject o=new JSONObject();
        try{
            o.put("total_samples",total).put("unreadable_samples",unreadable);
            o.put("game_running_samples",gameRunning).put("game_absent_samples",gameAbsent);
            o.put("frame_telemetry_stale_samples",fpsStale);
            o.put("first_sample_unix_ms",firstTimestamp<0?JSONObject.NULL:firstTimestamp);
            o.put("last_sample_unix_ms",lastTimestamp<0?JSONObject.NULL:lastTimestamp);
            o.put("first_readable_fps_unix_ms",firstFpsAt<0?JSONObject.NULL:firstFpsAt);
            o.put("last_readable_fps_unix_ms",lastFpsAt<0?JSONObject.NULL:lastFpsAt);
            o.put("shader_pass_errors_total_at_last_sample",lastShaderErrors);
            o.put("compute_kernel_errors_total_at_last_sample",lastComputeErrors);
            o.put("missing_asset_errors_total_at_last_sample",lastAssetErrors);
            JSONObject stats=new JSONObject();
            for(Map.Entry<String,Stats> e:fields.entrySet())
                stats.put(e.getKey(),e.getValue().json());
            o.put("metrics",stats);
            o.put("fps_caveat","External SurfaceFlinger presented frames; not Unity engine FPS");
        }catch(JSONException ignored){}
        return o;
    }
}