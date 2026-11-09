# T1 WATER-001: executable-evidence gate (2026-11-09)

Baseline HEAD: ddc14f24ef4cd173547ecfe8bf8d25ab712dbcae. Source examined: scripts/t1_fft_dispatch_pair_audit.py at branch HEAD; owner reports docs/DEVICE_FEEDBACK_42058825739_AR.md and apk-for-testing/OWNER_FEEDBACK_2026-11-08_AR.md.

## Discriminating observation
The *native* BEFORE parser hard-requires original_findkernel_callsite_present=false, original_runtime_mapping=unverified, gpu_result=unverified and source_sha_prefix=8aa32937d423. The *native* AFTER parser requires managed_dispatch_call_returned=true AND gpu_result=unverified. audit() unconditionally returns runtime_kernel_identity_proven=False and gpu_execution_proven=False. Thus paired_count > 0 can mean only syntactically paired managed entry/return, never original FindKernel binding, successful GPU execution, or Vulkan/Unity numerical parity. This is source-level proof of an evidence gap, not a claim that runtime fails.

## Owner device evidence kept separate
42058825739 (source e9c358eda01785b65e4eb14f18723da426635628): owner entered, saved, exited and re-entered world from Artifact; packaging publish failed. CL session 220911-559: 23,884 invalid water passes and 3,850 FFT kernel errors. CL 230108-327: 39,132 invalid passes and 6,026 FFT kernel errors. New 8 Nov CL session 164850-270: 74,359 invalid passes and 11,165 FFT kernel errors. These are independent counts, not cumulative. None proves a particular original shader GUID, Unity kernel index, or first numerical mismatch.

## Required next falsifiable experiment (not executed)
1. In an isolated original/Unity FFT harness, log per-dispatch shader GUID, original program hash, kernel name, FindKernel return index, resource GUID/shape/format, FFT length, radix/pass index, group XYZ, and source/build/session IDs. No proprietary shader bytes in public logs.
2. Capture first pass output for *identical* bounded deterministic input on Vulkan reference and Unity compute; compare complex components with explicit absolute and relative tolerances, record first mismatch and stage. Distinguish missing FindKernel/dispatch from numerical mismatch.
3. Test invalid kernel name and valid name separately, recording exception vs actual dispatch return; GPU result requires readback, not just returned call.
4. Use unified mini-lab T5 coordination before requesting device build; no duplicate Actions or change to shared resources.

## Result and limits
Source-level gate: NOT PROVEN. This closes the false-positive interpretation of passive trace counts, not WATER-001. No new phone execution, no numeric outputs, no Unity test, no build. Existing audit script was read but not modified. No tests claimed executed.
