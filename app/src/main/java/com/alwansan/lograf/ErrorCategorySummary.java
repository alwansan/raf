package com.alwansan.lograf;

import org.json.JSONObject;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Bounded, privacy-preserving classification for game-UID Logcat.
 * Only a short logcat timestamp/UID/PID/TID prefix is retained temporarily.
 * Full messages stay in raw segments and are not copied to metrics summaries.
 */
final class ErrorCategorySummary {
    private static final class Group {
        final AtomicLong count=new AtomicLong();
        final AtomicLong firstUnixMs=new AtomicLong();
        final AtomicLong lastUnixMs=new AtomicLong();
        void add() {
            long timestamp=System.currentTimeMillis();
            count.incrementAndGet();
            firstUnixMs.compareAndSet(0,timestamp);
            lastUnixMs.set(timestamp);
        }
    }
    private final LinkedHashMap<String,Group> groups=new LinkedHashMap<>();
    private String pendingKind,pendingPrefix;
    private int pendingLines;
    private long pendingAtNano;
    private static final int MAX_ASSOCIATION_LINES=24;
    private static final long MAX_ASSOCIATION_NS=1_500_000_000L;

    ErrorCategorySummary() {
        for(String name:new String[]{
                "postfx_bloom_invalid_pass",
                "ultimate_water_invalid_pass",
                "bilateral_blur_invalid_pass",
                "other_invalid_shader_pass",
                "water_fft_invalid_compute_kernel",
                "other_invalid_compute_kernel",
                "obb_guid_load_failed",
                "other_asset_guid_load_failed",
                "obb_access_denied",
                "obb_file_missing",
                "haptics_asset_path_not_found",
                "other_file_path_missing",
                "fmod_initialization_failed",
                "fmod_event_not_found",
                "java_fatal_exception",
                "native_fatal_signal",
                "java_out_of_memory",
                "graphics_context_lost"
        }) groups.put(name,new Group());
    }

    synchronized void reset() {
        clearPending();
        for(Group g:groups.values()){
            g.count.set(0);g.firstUnixMs.set(0);g.lastUnixMs.set(0);
        }
    }

    private void add(String category) {groups.get(category).add();}

    private static String unityEventKey(String line) {
        // -v threadtime -v uid -v year -v usec; consecutive stack lines
        // from the same Unity exception have an identical event prefix.
        int index=line.indexOf(" Unity   :");
        return index>0 && index<150?line.substring(0,index):null;
    }

    private void clearPending() {
        pendingKind=null;pendingPrefix=null;pendingLines=0;pendingAtNano=0;
    }

    private void flushPending() {
        if("kernel".equals(pendingKind))add("other_invalid_compute_kernel");
        // A generic NullReferenceException cannot be assumed to involve FMOD.
        clearPending();
    }

    private void beginPending(String kind,String line) {
        String key=unityEventKey(line);
        if(key==null){
            if("kernel".equals(kind))add("other_invalid_compute_kernel");
            return;
        }
        pendingKind=kind;pendingPrefix=key;pendingLines=0;
        pendingAtNano=System.nanoTime();
    }

    synchronized void observe(String line) {
        if(line==null)return;
        boolean kernel=line.contains("Invalid kernelIndex");
        boolean nullRef=line.contains("NullReferenceException");
        if(pendingKind!=null) {
            boolean same=pendingPrefix.equals(unityEventKey(line));
            if(same && "kernel".equals(pendingKind) &&
                    (line.contains("UltimateWater.Internal.Dx11FFT") ||
                     line.contains("UltimateWater.Internal.ComputeFFT"))) {
                add("water_fft_invalid_compute_kernel");
                clearPending();
            } else if(same && "fmod_null".equals(pendingKind) &&
                    (line.contains("FMODUnity.RuntimeManager.Initialize") ||
                     line.contains("FMODUnity.RuntimeManager:Initialize"))) {
                add("fmod_initialization_failed");
                clearPending();
            } else if(++pendingLines>=MAX_ASSOCIATION_LINES ||
                    System.nanoTime()-pendingAtNano>MAX_ASSOCIATION_NS ||
                    kernel || nullRef) {
                flushPending();
            }
        }

        String category=null;
        if(line.contains("Invalid pass number") && line.contains("Graphics.Blit")){
            if(line.contains("PostFX - Bloom"))category="postfx_bloom_invalid_pass";
            else if(line.contains("UltimateWater"))category="ultimate_water_invalid_pass";
            else if(line.contains("BilateralBlur"))category="bilateral_blur_invalid_pass";
            else category="other_invalid_shader_pass";
        }else if(kernel){
            if(line.contains("Dx11FFT") || line.contains("ComputeFFT"))
                category="water_fft_invalid_compute_kernel";
            else beginPending("kernel",line);
        }else if(line.contains("Unable to load GUID")){
            category=(line.contains(".obb") || line.contains("/Android/obb/"))?
                    "obb_guid_load_failed":"other_asset_guid_load_failed";
        }else if((line.contains(".obb") || line.contains("/Android/obb/") ||
                    line.contains("jar:file:")) && line.contains("Permission denied")){
            category="obb_access_denied";
        }else if((line.contains(".obb") || line.contains("/Android/obb/") ||
                    line.contains("jar:file:")) &&
                    (line.contains("FileNotFoundException") ||
                     line.contains("DirectoryNotFoundException"))){
            category="obb_file_missing";
        }else if(line.contains("DirectoryNotFoundException") ||
                line.contains("FileNotFoundException")){
            category=line.contains("Haptics")?"haptics_asset_path_not_found":
                    "other_file_path_missing";
        }else if(line.contains("[FMOD] Initialization failed") ||
                line.contains("SystemNotInitializedException")){
            category="fmod_initialization_failed";
        }else if(line.contains("EventNotFoundException") ||
                (line.contains("FMOD") && line.contains("Event not found"))){
            category="fmod_event_not_found";
        }else if(nullRef){
            // Classify only when a later stack frame proves FMOD origin.
            beginPending("fmod_null",line);
        }else if(line.contains("FATAL EXCEPTION")){
            category="java_fatal_exception";
        }else if(line.contains("Fatal signal") || line.contains("SIGSEGV") ||
                line.contains("SIGABRT")){
            category="native_fatal_signal";
        }else if(line.contains("OutOfMemoryError")){
            category="java_out_of_memory";
        }else if(line.contains("EGL_CONTEXT_LOST") || line.contains("VK_ERROR_DEVICE_LOST")){
            category="graphics_context_lost";
        }
        if(category!=null)add(category);
    }

    synchronized void finish(){flushPending();}

    synchronized JSONObject snapshot(){
        // Avoid premature classification while the stack is arriving.
        if(pendingKind!=null && System.nanoTime()-pendingAtNano>MAX_ASSOCIATION_NS)
            flushPending();
        JSONObject out=new JSONObject();
        try{
            for(Map.Entry<String,Group> entry:groups.entrySet()){
                Group g=entry.getValue();
                if(g.count.get()==0)continue;
                JSONObject data=new JSONObject();
                data.put("count",g.count.get());
                data.put("first_observed_unix_ms",g.firstUnixMs.get());
                data.put("last_observed_unix_ms",g.lastUnixMs.get());
                out.put(entry.getKey(),data);
            }
        }catch(Exception ignored){}
        return out;
    }
}
