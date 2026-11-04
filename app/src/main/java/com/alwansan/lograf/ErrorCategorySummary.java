package com.alwansan.lograf;

import org.json.JSONObject;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Privacy-conscious, fixed-vocabulary error classification. It never retains
 * or emits raw exception messages, filenames, stack traces or stream URLs.
 * Raw Logcat remains unmodified in the recorder's own log segments.
 */
final class ErrorCategorySummary {
    private static final class Group {
        final AtomicLong count=new AtomicLong();
        final AtomicLong firstUnixMs=new AtomicLong();
        final AtomicLong lastUnixMs=new AtomicLong();
        void add(){
            long timestamp=System.currentTimeMillis();
            count.incrementAndGet();
            firstUnixMs.compareAndSet(0,timestamp);
            lastUnixMs.set(timestamp);
        }
    }
    private final LinkedHashMap<String,Group> groups=new LinkedHashMap<>();
    ErrorCategorySummary(){
        for(String name:new String[]{
                "postfx_bloom_invalid_pass",
                "ultimate_water_invalid_pass",
                "bilateral_blur_invalid_pass",
                "other_invalid_shader_pass",
                "water_fft_invalid_compute_kernel",
                "other_invalid_compute_kernel",
                "haptics_asset_path_not_found",
                "other_file_path_missing",
                "java_fatal_exception",
                "native_fatal_signal",
                "java_out_of_memory",
                "graphics_context_lost", "fmod_initialization_failed", "fmod_event_not_found"
        }) groups.put(name,new Group());
    }
    void reset(){
        for(Group g:groups.values()){
            g.count.set(0);g.firstUnixMs.set(0);g.lastUnixMs.set(0);
        }
    }
    void observe(String line){
        // Every expensive categorization is gated by a known error token.
        // One log line belongs to one category at most.
        String category=null;
        if(line.contains("Invalid pass number") && line.contains("Graphics.Blit")){
            if(line.contains("PostFX - Bloom"))category="postfx_bloom_invalid_pass";
            else if(line.contains("UltimateWater"))category="ultimate_water_invalid_pass";
            else if(line.contains("BilateralBlur"))category="bilateral_blur_invalid_pass";
            else category="other_invalid_shader_pass";
        }else if(line.contains("Invalid kernelIndex")){
            if(line.contains("Dx11FFT") || line.contains("ComputeFFT"))
                category="water_fft_invalid_compute_kernel";
            else category="other_invalid_compute_kernel";
        }else if(line.contains("DirectoryNotFoundException") ||
                line.contains("FileNotFoundException")){
            category=line.contains("Haptics")?"haptics_asset_path_not_found":
                    "other_file_path_missing";
        }else if(line.contains("[FMOD] Initialization failed") || line.contains("SystemNotInitializedException")){
            category="fmod_initialization_failed";
        }else if(line.contains("EventNotFoundException") || (line.contains("FMOD") && line.contains("Event not found"))){
            category="fmod_event_not_found";
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
        if(category!=null)groups.get(category).add();
    }
    JSONObject snapshot(){
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