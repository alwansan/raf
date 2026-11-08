# T1 scheduled session 20261108T0315Z-T1-scheduled-original-trace-gap-6e91
origin: scheduled
baseline_head: e669605c40d000edb926ddad332d7221c0a57bff
scope_commit: ecdef38050c73003358e340c09f2d98c9a8cceff
scope: WATER-001 authentic original FFT-to-Unity kernel mapping, no T4/T5 overlap

## Owner evidence precedence
Read docs/DEVICE_FEEDBACK_42058825739_AR.md. The owner entered/saved/exited/reentered world from 42058825739 artifact; GitHub release publishing failed. Source SHA e9c358eda01785b65e4eb14f18723da426635628 does not authenticate the installed APK bytes without manifest. Pinned CL 520c4cf409aa20a4db54ff80ed87d8807d9cba57: 220911-559 23,884 water pass / 3,850 kernel errors; 230108-327 39,132 / 6,026. Counts alone do not identify FFT kernel or establish causation.

## Engineering finding
Inspected scripts/t1_fft_dispatch_coverage.py and scripts/t1_fft_first_divergence.py on branch. The geometry gate accepts a caller-provided GUID/name/index/numthreads/dispatch tuple and proves only exact ceiling group coverage; it does not independently look up an original shader or collect a Unity API call. The comparator requires raw paired RGBA32F reference/observed captures; none is present in these reviewed artifacts. Thus passing the synthetic validator cannot map Kernel Index 6 to a named Unity FFT kernel, and no numerical Vulkan↔Unity divergence is measured. Do not patch index 6 blindly or interpret water-pass flood as a single FFT cause.

## Reproducible next acquisition / test
1. On a verified original-resource candidate record ComputeShader asset GUID and source/compiled program hash; capture kernel names and GetKernelThreadGroupSizes at the same immutable candidate SHA.
2. At actual Unity call sites capture the returned FindKernel index, Dispatch index, (x,y,z) groups, logical extent, selected program/variant and per-resource bindings (name, slot, dimensions, format, hash); record device/graphics API and time relative to world-load. Avoid logging raw proprietary shader/data.
3. Match the original Vulkan program/variant and resource hashes; capture ordered pass outputs on identical deterministic inputs in private storage, then run scripts/t1_fft_first_divergence.py to identify the first mismatch and inspect its per-channel nonfinite counts. Only then use scripts/t1_fft_dispatch_coverage.py for structural geometry validation; padded overdispatch requires explicit bounds-check evidence.
4. Correlate exact timestamped first kernel error and water-pass error from each CL session with Unity call-site traces; preserve session/build provenance and do not assume numeric index stability across shaders.

## Execution and limits
GitHub connector branch HEAD verified e669605c40d000edb926ddad332d7221c0a57bff before scope; recent Actions list included completed success 42439391089 for T4 mouse classifier, not FFT. Local git ls-remote failed: Could not resolve host github.com; tests and authentic Unity/Vulkan capture not run. No Unity/APK request, no force push, no CL writes, no original assets published. The scope record itself is the concrete independently published evidence/acquisition protocol, not a shader fix. Trial vote unchanged; WATER-001 OPEN; NOT_READY 0/3.

next: recover network or run existing FFT tests via Actions on fixed SHA; acquire original runtime kernel identity and matched captures. Keep T4 physical mouse and T5 three buttons/Resolution in their assigned scopes.
