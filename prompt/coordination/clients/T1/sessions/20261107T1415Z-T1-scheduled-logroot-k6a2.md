# T1 — 20261107T1415Z-T1-scheduled-logroot-k6a2
origin: scheduled
resumed_from: 20261107T1308Z-T1-scheduled-kernel6-materialsplit-n4q7; 20261107T1211Z-T1-scheduled-cl-timing-f8c2
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md; phone world/save/reopen confirmed by owner from 42058825739 Artifact; publication failed.
CL_read_only: alwansan/CL@520c4cf409aa20a4db54ff80ed87d8807d9cba57; summary 220911-559 and 230108-327.
result: Added bounded, redacted, streaming private Logcat first-root classifier. Recognizes kernel index 6 vs other and Spectrum/Foam Global pass failures; emits first timestamp and counts only, never raw line or private names. Three synthetic unit tests passed locally.
limits: Could not download 33MB raw CL segments from runtime (DNS unavailable, connector file range empty). Classifier has NOT been calibrated against actual raw Logcat; no original Unity kernel mapping, no Vulkan/Unity numeric comparison, no FindKernel/Dispatch runtime proof. Do not treat synthetic test as phone evidence. Summary kernel 3850/6026 and pass 23884/39132 unchanged. No CI, Unity or APK launched. T4/T5 files untouched. WATER-001 OPEN, NOT_READY 0/3.
next: Run python3 scripts/t1_water_logcat_first_roots.py <pinned-private-raw-segments> locally or isolated CI without publishing input. Compare counts/timestamps to session-summary, investigate unmatched patterns privately. Trace C# caller and imported ComputeShader to FindKernel/Dispatch and pair authentic FFT traces before claiming GPU fix.
