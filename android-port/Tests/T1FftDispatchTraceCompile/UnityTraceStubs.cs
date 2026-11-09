// Source-only ABI and behavioral smoke; fake Unity types, no actual GPU.
using System;
using System.Collections.Generic;
using RaftAndroid.Diagnostics;

namespace UnityEngine
{
    public sealed class ComputeShader
    {
        public int GetInstanceID() { return 1234; }
    }
    public static class SystemInfo
    {
        public static bool supportsComputeShaders { get { return true; } }
    }
    public static class Time
    {
        public static int frameCount { get { return 42; } }
        public static float realtimeSinceStartup { get { return 1.5f; } }
    }
}

namespace RaftAndroid.Diagnostics
{
    public static class AndroidRuntimeLog
    {
        public static readonly List<string> Entries = new List<string>();
        public static bool FailWrites;
        public static void Initialize() { if (FailWrites) throw new InvalidOperationException(); }
        public static void Write(string area, string operation, string detail = "", bool critical = false)
        {
            if (FailWrites) throw new InvalidOperationException();
            Entries.Add(area + ":" + operation + ":" + detail);
        }
    }
}

internal static class T1TraceCompileSmoke
{
    private static void Need(bool condition)
    {
        if (!condition) throw new Exception("Synthetic source-only FFT trace contract FAILED");
    }

    public static void Main()
    {
        var shader = new UnityEngine.ComputeShader();
        int first = T1FftDirectDispatchTrace.BeforeDispatch(shader, 6, 1, 256, 1, 8, 0);
        Need(first == 1);
        T1FftDirectDispatchTrace.AfterDispatch(first);
        Need(AndroidRuntimeLog.Entries.Count == 2);
        string firstLog = AndroidRuntimeLog.Entries[0];
        Need(firstLog.Contains("numeric_kernel_argument=6"));
        Need(firstLog.Contains("source_bank0_candidate"));
        Need(firstLog.Contains("original_exponent=8"));
        Need(firstLog.Contains("original_runtime_mapping=unverified"));
        Need(firstLog.Contains("shader_instance_session_local=1234"));
        Need(AndroidRuntimeLog.Entries[1].Contains("managed_dispatch_call_returned=true"));
        Need(AndroidRuntimeLog.Entries[1].Contains("gpu_result=unverified"));

        int bank1 = T1FftDirectDispatchTrace.BeforeDispatch(shader, 16, 1, 256, 1, 8, 0);
        T1FftDirectDispatchTrace.AfterDispatch(bank1);
        Need(AndroidRuntimeLog.Entries[2].Contains("source_bank1_candidate"));
        int unexpected = T1FftDirectDispatchTrace.BeforeDispatch(shader, 5, 1, 256, 1, 8, 0);
        T1FftDirectDispatchTrace.AfterDispatch(unexpected);
        Need(AndroidRuntimeLog.Entries[4].Contains("outside_source_bank_candidates"));
        Need(AndroidRuntimeLog.Entries.Count == 6);

        // Instrumentation must never make original game calls throw.
        AndroidRuntimeLog.FailWrites = true;
        int noSink = T1FftDirectDispatchTrace.BeforeDispatch(null, 6, 1, 64, 1, 8, 0);
        T1FftDirectDispatchTrace.AfterDispatch(noSink);
        Need(AndroidRuntimeLog.Entries.Count == 6);
        AndroidRuntimeLog.FailWrites = false;

        // Original error identity is preserved and the passive helper never
        // logs the exception message, which could contain sensitive source text.
        Exception actualError = new ArgumentException("DO_NOT_EXPORT_PRIVATE_DETAILS");
        int errorSequence = T1FftDirectDispatchTrace.BeforeDispatch(shader, 6, 1, 256, 1, 8, 0);
        bool caughtOriginal = false;
        try
        {
            try { throw actualError; }
            catch (Exception ex)
            {
                T1FftDirectDispatchTrace.DispatchThrew(errorSequence, ex);
                throw;
            }
        }
        catch (Exception caught)
        {
            caughtOriginal = Object.ReferenceEquals(caught, actualError);
        }
        Need(caughtOriginal);
        Need(AndroidRuntimeLog.Entries.Count == 8);
        Need(AndroidRuntimeLog.Entries[7].Contains("t1_original_fft_dispatch.threw"));
        Need(AndroidRuntimeLog.Entries[7].Contains("managed_dispatch_threw=true"));
        Need(AndroidRuntimeLog.Entries[7].Contains("exception_kind=argument"));
        Need(AndroidRuntimeLog.Entries[7].Contains("gpu_result=unverified"));
        Need(!AndroidRuntimeLog.Entries[7].Contains("DO_NOT_EXPORT_PRIVATE_DETAILS"));
        AndroidRuntimeLog.FailWrites = true;
        T1FftDirectDispatchTrace.DispatchThrew(errorSequence, actualError);
        AndroidRuntimeLog.FailWrites = false;
        Need(AndroidRuntimeLog.Entries.Count == 8);

        // The remaining bounded calls reach the hard limit, then stop recording.
        for (int n = 0; n < 30; n++)
        {
            int sequence = T1FftDirectDispatchTrace.BeforeDispatch(
                shader, 6, 1, 64, 1, 8, 0);
            T1FftDirectDispatchTrace.AfterDispatch(sequence);
        }
        Need(AndroidRuntimeLog.Entries.Count == 30);
        Console.WriteLine("T1_ORIGINAL_FFT_ANDROID_HELPER compile_csharp9=true bounded_16=true preserves_dispatch=true gpu_executed=false");
    }
}
