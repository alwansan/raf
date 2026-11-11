# T1 scheduled checkpoint — 20261111T1507Z-T1-scheduled-fft-dispatch-contract-6e4b
origin: scheduled
base_sha: 1793aa29bb80eb75ca7e94e37a0ca3a638a654de
resumed_from_sessions: 20261111T1307Z-T1-scheduled-provenance-6d29; 20261109T2115Z-T1-chat-direct-fft-thrown-hook-2b6e
work: prompt/coordination/work/WATER-001/T1-20261111T1507Z-T1-scheduled-fft-dispatch-contract-6e4b.md

## Evidence verified
- Owner's docs/DEVICE_FEEDBACK_42058825739_AR.md explicitly confirms world enter/save/exit/reenter from run 42058825739 artifact, source e9c358eda01785b65e4eb14f18723da426635628. Artifact publishing failed, so no signed-byte identity assertion.
- CL immutable tree 520c4cf409aa20a4db54ff80ed87d8807d9cba57 referenced by owner report; session 220911-559 23,884 water-pass errors and 3,850 FFT kernel errors, session 230108-327 39,132 and 6,026. Different durations/scene states preclude rate or regression inference. Pinned report provides screenshot references, not proof of valid water pixels.
- Existing T1 source-only hook from session 20261109T2115Z distinguishes direct Dispatch thrown/returned but is not in the owner's older installed artifact. Existing proximity script explicitly reports original kernel identity unproven.
- Latest inspected branch HEAD at scope start: 1793aa29bb80eb75ca7e94e37a0ca3a638a654de. Scope published in ee29c40683ec40ce3193fad88d08462de002a35b. No competing T4/T5 file edited.

## Engineering decision / necessary discriminator
The Unity exception `Invalid kernelIndex (6) passed, must be non-negative less than 0` is consistent with zero valid kernels on the ComputeShader object at dispatch. It does **not** prove that original compiled program slot 6 is a Unity runtime kernel ID, nor distinguish missing asset/import from incorrect shader selection. Next real test must pair the same source-authenticated asset GUID with `HasKernel(name)`, `FindKernel(name)`, `GetKernelThreadGroupSizes(index)`, actual `Dispatch` trace and a numeric first-pass output. A sanitized pass proximity correlation cannot resolve asset binding.

## Limits and next step
No new source edit, Unity/Android test, APK/OBB, or numeric Vulkan/Unity comparison this cycle. Container DNS prevented git clone; GitHub connector read/write worked. No new workflow launched or existing job cancelled. WATER-001 OPEN, NOT_READY 0/3. Resume from T1's original Unity probe and direct thrown hook; locate authenticated authored .compute + .meta and actual caller; avoid inventing kernel table. Coordinate T5 shared mini-lab if on-device trace becomes necessary. T4 physical mouse and T5 resolution/right buttons are separate live scopes; touch layout remains deferred.
