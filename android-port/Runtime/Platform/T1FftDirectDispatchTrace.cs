#if UNITY_ANDROID && !UNITY_EDITOR
// T1 WATER-001: passive direct numeric Dispatch metadata, not GPU proof.
using System;
using System.Globalization;
using System.Threading;
using System.Security.Cryptography;
using System.Text;
using UnityEngine;

namespace RaftAndroid.Diagnostics
{
    public static class T1FftDirectDispatchTrace
    {
        private const int MaxCalls = 16;
        private static int nextCall;
        private static int nextBinding;
        private const string OriginalDerivedShaPrefix = "8aa32937d423";
        public static int BeforeBinding(int site, ComputeShader shader)
        {
            int sequence = Interlocked.Increment(ref nextBinding);
            if (sequence <= 0 || sequence > MaxCalls) return 0;
            try
            {
                AndroidRuntimeLog.Initialize();
                bool present = shader != null;
                string name = present ? shader.name : null;
                string digest = "unavailable";
                if (!string.IsNullOrEmpty(name) && name.Length <= 256)
                {
                    using (var hasher = SHA256.Create())
                        digest = BitConverter.ToString(hasher.ComputeHash(Encoding.UTF8.GetBytes(name)))
                            .Replace("-", "").ToLowerInvariant();
                }
                AndroidRuntimeLog.Write("water", "t1_original_fft_bind.before",
                    "sequence=" + sequence + "; site=" + site + "; pass=" + (site / 3)
                    + "; shader_present=" + present + "; shader_name_sha256=" + digest
                    + "; shader_instance_session_local=" + (present ? shader.GetInstanceID() : 0)
                    + "; frame=" + Time.frameCount + "; source_sha_prefix=" + OriginalDerivedShaPrefix, true);
            }
            catch (Exception) { }
            return sequence;
        }

        public static void BindingResult(int sequence, bool threw)
        {
            if (sequence <= 0 || sequence > MaxCalls) return;
            try
            {
                AndroidRuntimeLog.Write("water",
                    threw ? "t1_original_fft_bind.threw" : "t1_original_fft_bind.returned",
                    "sequence=" + sequence + "; gpu_result=unverified", true);
            }
            catch (Exception) { }
        }

        public static int BeforeDispatch(ComputeShader shader, int kernelArg,
            int groupX, int groupY, int groupZ, int originalExponent, int passOffset)
        {
            int sequence = Interlocked.Increment(ref nextCall);
            if (sequence <= 0 || sequence > MaxCalls) return 0;
            try
            {
                AndroidRuntimeLog.Initialize();
                int shaderId = shader == null ? 0 : shader.GetInstanceID();
                // The inferred candidate is NOT the measured original bank bool.
                int delta = kernelArg - (((originalExponent - 5) << 1) + passOffset);
                string bankCandidate = delta == 0 ? "source_bank0_candidate" :
                    delta == 10 ? "source_bank1_candidate" :
                    "outside_source_bank_candidates";
                AndroidRuntimeLog.Write("water", "t1_original_fft_dispatch.before",
                    "sequence=" + sequence +
                    "; source_sha_prefix=" + OriginalDerivedShaPrefix +
                    "; original_findkernel_callsite_present=false" +
                    "; shader_instance_session_local=" + shaderId +
                    "; shader_present=" + (shader != null) +
                    "; original_exponent=" + originalExponent +
                    "; inferred_bank_only=" + bankCandidate +
                    "; pass_offset=" + passOffset +
                    "; numeric_kernel_argument=" + kernelArg +
                    "; group_xyz=" + groupX + "," + groupY + "," + groupZ +
                    "; unity_compute_supported=" + SystemInfo.supportsComputeShaders +
                    "; frame=" + Time.frameCount +
                    "; realtime_s=" + Time.realtimeSinceStartup.ToString("F3", CultureInfo.InvariantCulture) +
                    "; original_runtime_mapping=unverified; gpu_result=unverified", true);
            }
            catch (Exception)
            {
                // Logging must never prevent the original Dispatch.
            }
            return sequence;
        }

        public static void AfterDispatch(int sequence)
        {
            if (sequence <= 0 || sequence > MaxCalls) return;
            try
            {
                AndroidRuntimeLog.Write("water", "t1_original_fft_dispatch.returned",
                    "sequence=" + sequence +
                    "; managed_dispatch_call_returned=true" +
                    "; unity_error_callback_may_follow=true" +
                    "; gpu_result=unverified; water_rendering=unverified", true);
            }
            catch (Exception) { }
        }

        // Called only if the original ComputeShader.Dispatch synchronously throws.
        // The caller still rethrows the EXACT original exception with a bare throw.
        // Never log exception details, stacks, shader bytes or Unity objects.
        public static void DispatchThrew(int sequence, Exception exception)
        {
            if (sequence <= 0 || sequence > MaxCalls) return;
            try
            {
                string kind = exception is ArgumentException ? "argument" :
                    exception is InvalidOperationException ? "invalid_operation" :
                    exception is NullReferenceException ? "null_reference" :
                    "other";
                AndroidRuntimeLog.Write("water", "t1_original_fft_dispatch.threw",
                    "sequence=" + sequence +
                    "; managed_dispatch_threw=true" +
                    "; exception_kind=" + kind +
                    "; original_runtime_mapping=unverified" +
                    "; gpu_result=unverified; water_rendering=unverified", true);
            }
            catch (Exception) { }
        }

    }
}
#endif
