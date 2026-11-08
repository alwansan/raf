# 20261108T0315Z-T1-scheduled-original-trace-gap-6e91
origin: scheduled
baseline_head: e669605c40d000edb926ddad332d7221c0a57bff
scope: WATER-001 authentic FFT resource and Unity kernel trace evidence audit (read-only source; independent from T4 mouse and T5 display/delivery)
files: this work record; clients/T1/sessions/20261108T0315Z-T1-scheduled-original-trace-gap-6e91.md
hypothesis: a structurally valid synthetic FindKernel/Dispatch record cannot establish original Kernel Index 6 identity without the source ComputeShader GUID and runtime trace.
experiment_key: T1-FFT-ORIGINAL-TRACE-GAP-20261108; shared_resource: none; no CI requested.
owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md and CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57; 220911-559 water 23884/kernel 3850; 230108-327 water 39132/kernel 6026. Successful world enter/save/reenter from artifact 42058825739, publishing failed. Not APK86.
previous: clients/T1/sessions/20261108T0206Z-T1-scheduled-capture-path-regression-b6e4.md; commit 388c53ad7d841bb89864a6a321e7bb3e1064f432.
method: inspect scripts/t1_fft_dispatch_coverage.py and scripts/t1_fft_first_divergence.py; compare their input contracts to actual source evidence; avoid speculative kernel remapping or false parity.
expected deliverable: explicit trace acquisition contract and blocker with reproducible next step; do not claim a GPU/device fix.
