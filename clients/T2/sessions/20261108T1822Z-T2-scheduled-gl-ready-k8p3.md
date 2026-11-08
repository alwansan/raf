# T2 scheduled — bounded GLES context initialization
session_id: 20261108T1822Z-T2-scheduled-gl-ready-k8p3
origin: scheduled
branch: feature/android-native-port
baseline_sha: 67feffde72d6ba7ab7a59244d4f8099840cdd915
work: work/experiments/20261108T1822Z-T2-scheduled-gl-ready-k8p3.md
scope: T2-only GLES3 host driver; no shared build request or T3 shader edits.
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md (world/save/reentry works from artifact; publishing failed; water/FFT errors persist). New 8 Nov unified mini lab supersedes five standalone APKs.
resumed_from: clients/T2/sessions/20261108T1817Z-T2-chat-fbo-contrast-92d4.md
hypothesis: fixed 1s auto-start may misclassify slow EGL initialization as GPU failure.
change_commit: eeeec2c6da50bfe1f16b4f0fe43525c0b0eb51b2
work_commit: d5f4fc95e0e2853b91437c8bbd07d0eef0737242
source_blob_sha: 6a7abb91f3356e4e2fcb688c8953219859d8bc1d
implementation: replace fixed 1000ms auto delay with bounded readiness poll every 100ms up to 7000ms; explicit FAIL and case ID if timeout; activity destruction cancels pending execution. Manual cases unchanged.
validation: re-fetched published blob; five source-level assertions PASS (poll, deadline, explicit FAIL, success branch, fixed-delay removal). NOT a javac/Android/device test. No Actions dispatched; T5 owns unified mini build.
limitations: no original Spectrum/Foam/Blur/CB0 restored or authenticated; WATER-001 OPEN. No real Adreno pass asserted. Further CI compilation and device test required.
next_step: T5 unified Java compile gate and one shared APK when appropriate; T2 should obtain four-pixel FBO device JSONL, then resume original Foam operand/CB0 provenance with T3. Recheck HEAD and active CI before requesting tests.
