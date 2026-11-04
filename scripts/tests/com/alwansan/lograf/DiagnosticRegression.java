package com.alwansan.lograf;
import org.json.JSONObject;

/** Deterministic, actual JVM tests, no Android device or mock source parsing. */
public final class DiagnosticRegression {
    private static final String EVENT="2026-11-04 21:09:01.604220 10265 30942  2248 E Unity   : ";
    private static final String OTHER="2026-11-04 21:09:01.604220 10265 30942  9999 E Unity   : ";
    private static final String NEXT="2026-11-04 21:09:02.604220 10265 30942  2248 E Unity   : ";
    static void eq(long expected,long actual,String message){
        if(expected!=actual)
            throw new AssertionError(message+" expected="+expected+" actual="+actual);
    }
    static void expect(String actual,String expected){
        if(!expected.equals(actual))throw new AssertionError(expected+" != "+actual);
    }
    static long count(ErrorCategorySummary classifier,String category){
        JSONObject report=classifier.snapshot();
        return report.has(category)?report.getJSONObject(category).getLong("count"):0;
    }
    public static void main(String[] args){
        ErrorCategorySummary c=new ErrorCategorySummary();
        c.observe(EVENT+"IndexOutOfRangeException: Invalid kernelIndex (6) passed, must be non-negative less than 0.");
        c.observe(OTHER+"at UltimateWater.Internal.Dx11FFT.ComputeFFT()");
        c.observe(EVENT+"at UltimateWater.Internal.Dx11FFT.ComputeFFT()");
        eq(1,count(c,"water_fft_invalid_compute_kernel"),"same-event FFT");
        eq(0,count(c,"other_invalid_compute_kernel"),"no double count");
        c.observe(NEXT+"IndexOutOfRangeException: Invalid kernelIndex (0) passed");
        c.observe(OTHER+"at UltimateWater.Internal.Dx11FFT.ComputeFFT()");
        c.finish();
        eq(1,count(c,"other_invalid_compute_kernel"),"different thread cannot attribute FFT");
        c.observe(NEXT+"Unable to load GUID for '/storage/emulated/0/Android/obb/pkg/patch.86.pkg.obb'");
        eq(1,count(c,"obb_guid_load_failed"),"OBB GUID");
        c.observe(NEXT+"Unable to load GUID for 'Assets/scene.asset'");
        eq(1,count(c,"other_asset_guid_load_failed"),"asset GUID");
        c.observe(NEXT+"Opened /storage/emulated/0/Android/obb/pkg/main.86.pkg.obb successfully");
        eq(1,count(c,"obb_guid_load_failed"),"benign OBB mention");
        c.observe(NEXT+"FileNotFoundException: /Android/obb/pkg/main.86.pkg.obb");
        eq(1,count(c,"obb_file_missing"),"OBB missing");
        c.observe(NEXT+"Permission denied /Android/obb/pkg/");
        eq(1,count(c,"obb_access_denied"),"OBB denied");
        c.observe(EVENT+"NullReferenceException: Object reference not set to an instance of an object.");
        c.observe(EVENT+"at FMODUnity.RuntimeManager.Initialize ()");
        eq(1,count(c,"fmod_initialization_failed"),"FMOD inferred by matching frame");
        c.observe(NEXT+"NullReferenceException: object reference");
        c.observe(NEXT+"at unrelated.Game.Update()");
        c.finish();
        eq(1,count(c,"fmod_initialization_failed"),"unrelated NPE not FMOD");
        c.observe(NEXT+"EventNotFoundException: unavailable");
        eq(1,count(c,"fmod_event_not_found"),"missing event");
        c.reset();
        eq(0,count(c,"water_fft_invalid_compute_kernel"),"reset");
        // Replay observed high-frequency pattern: bounded association holds.
        for(int i=0;i<17178;i++){
            c.observe(EVENT+"IndexOutOfRangeException: Invalid kernelIndex (6) passed");
            c.observe(EVENT+"at UltimateWater.Internal.Dx11FFT.ComputeFFT()");
        }
        c.finish();
        eq(17178,count(c,"water_fft_invalid_compute_kernel"),"flood classification exact");
        eq(0,count(c,"other_invalid_compute_kernel"),"no flood duplicate");
        expect(MemoryTelemetryQuality.classify(1000L,1050L,200),"validated_recent");
        expect(MemoryTelemetryQuality.classify(1000L,1050L,11000),"validated_cached");
        expect(MemoryTelemetryQuality.classify(20000L,1000L,11000),"android_meminfo_reported_above_proc_rss");
        expect(MemoryTelemetryQuality.classify(1000L,null,200),"unverified_no_reference_rss");
        expect(MemoryTelemetryQuality.classify(null,1000L,200),"unavailable");
        if(!MemoryTelemetryQuality.usable("validated_cached"))
            throw new AssertionError("Aged but validated PSS must be explicit, not false null");
        if(!MemoryTelemetryQuality.usable("android_meminfo_reported_above_proc_rss"))
            throw new AssertionError("Android framework reported PSS must remain available with caveat");
        if(MemoryTelemetryQuality.comparableToProcRss("android_meminfo_reported_above_proc_rss"))
            throw new AssertionError("GPU-inclusive memory must not be certified equal to Linux RSS");
        if(MemoryTelemetryQuality.usable("unverified_no_reference_rss"))
            throw new AssertionError("No reference means only a candidate can be exported");
                c.reset();
        c.observe(EVENT+"Custom cursor: Attempt to set a custom cursor that is not RGBA32 format failed.");
        c.observe(EVENT+"The referenced script on this Behaviour (Game Object 'test') is missing!");
        c.observe(EVENT+"There can be only one active Event System.");
        c.observe(EVENT+"DllNotFoundException: Unable to load DLL 'steam_api64'");
        c.observe(EVENT+"Couldn't create a Convex Mesh from source mesh within the maximum polygons limit (256).");
        eq(1,count(c,"unity_cursor_rgba32_required"),"cursor format");
        eq(1,count(c,"unity_missing_mono_script"),"missing script");
        eq(1,count(c,"unity_duplicate_event_system"),"duplicate UI EventSystem");
        eq(1,count(c,"steam_api64_unavailable"),"Steam library dependency");
        eq(1,count(c,"unity_convex_mesh_polygon_limit"),"convex geometry limit");
        c.observe(EVENT+"Custom cursor applied RGBA32 successfully");
        eq(1,count(c,"unity_cursor_rgba32_required"),"benign cursor success");
        eq(PidProbeObservation.UNKNOWN,PidProbeObservation.gamePid(-1,"pidof_probe_failed"),"probe failure unknown");
        eq(PidProbeObservation.UNKNOWN,PidProbeObservation.gamePid(-1,"main_cmdline_unverified"),"cmdline inaccessible unknown");
        eq(PidProbeObservation.NOT_RUNNING,PidProbeObservation.gamePid(-1,"pidof_empty"),"verified no process");
        eq(2345,PidProbeObservation.gamePid(2345,"main_pid_verified"),"verified process");
        System.out.println("Diagnostic regression PASS: FFT/OBB/FM​​OD/PSS/PID/gameplay categories + 17178-event replay");
    }
}
