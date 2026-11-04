package com.alwansan.lograf;

import org.json.JSONObject;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Fixed-cardinality render failure counters for game-UID Logcat.
 * Material names are mapped to constants, never retained as strings or paths.
 * Kernel index by itself is NOT proof that an error belongs to UltimateWater;
 * cross-check water_fft_invalid_compute_kernel in ErrorCategorySummary.
 */
final class RenderFailureSummary {
    private static final String[] MATERIAL_KEYS = {
        "spectrum", "foam_global", "subsurface_blur", "utility_noise", "other_ultimate_water"
    };
    private final AtomicLong[] passCounts = new AtomicLong[MATERIAL_KEYS.length];
    private final AtomicLong kernel6 = new AtomicLong();
    private final AtomicLong kernelOther = new AtomicLong();

    RenderFailureSummary(){
        for(int i=0;i<passCounts.length;i++)passCounts[i]=new AtomicLong();
    }
    void reset(){
        for(AtomicLong counter:passCounts)counter.set(0);
        kernel6.set(0);kernelOther.set(0);
    }
    void observe(String line){
        if(line==null)return;
        if(line.contains("Invalid pass number") &&
                line.contains("Graphics.Blit") && line.contains("UltimateWater")){
            int bucket;
            if(line.contains("UltimateWater/Spectrum/Water Spectrum"))bucket=0;
            else if(line.contains("UltimateWater/Foam/Global"))bucket=1;
            else if(line.contains("UltimateWater/Utilities/Blur (Subsurface Scattering)"))bucket=2;
            else if(line.contains("UltimateWater/Utility/Noise"))bucket=3;
            else bucket=4;
            passCounts[bucket].incrementAndGet();
        }
        if(line.contains("Invalid kernelIndex")){
            if(line.contains("Invalid kernelIndex (6)"))kernel6.incrementAndGet();
            else kernelOther.incrementAndGet();
        }
    }

    static boolean renderErrorFlood(double rootLinesPerSecond){
        return Double.isFinite(rootLinesPerSecond) && rootLinesPerSecond>=100.0;
    }

    JSONObject snapshot(){
        JSONObject out=new JSONObject();
        JSONObject passes=new JSONObject(),kernels=new JSONObject();
        try{
            for(int i=0;i<MATERIAL_KEYS.length;i++)
                passes.put(MATERIAL_KEYS[i],passCounts[i].get());
            kernels.put("index_6",kernel6.get());
            kernels.put("other_index",kernelOther.get());
            out.put("ultimate_water_invalid_pass_by_material",passes);
            out.put("invalid_kernel_index_root_lines",kernels);
            out.put("scope","game-UID raw Logcat root messages; kernel index alone does not prove water origin");
        }catch(Exception ignored){}
        return out;
    }
}
