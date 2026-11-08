# T2 scheduled — device GPU evidence boundary
session_id: 20261108T2015Z-T2-scheduled-cl-gpu-evidence-v8q2
origin: scheduled
base_sha: 16665ef14d7bbdf9d8469647a92c35af47e466e1
resumed_from: clients/T2/sessions/20261108T1956Z-T2-chat-pass1-source-kind-4d6a.md
issue_id: WATER-001
scope: read-only new CL shared mini-lab results; no overlap with T2 original-Cecil scanner chat scope.
experiment_key: T2-CL-SHARED-20261108-223850-465101153-PACK-6e19b05c
resource_key: shared mini-lab device evidence (read-only)
source: https://github.com/alwansan/CL/blob/main/test/shared-20261108-223850-465101153/summary-20261108-223850-465101153.json
source app SHA: cbe7a038bad2c7ca5ad587b242e8baf7128ecb8b
pack SHA256: 6e19b05c697334be6ee7740846f2817f29fdcb185a118c8f5d36bbd06b04066f

## Observations
T2-01 PASS: Adreno 730 GLES 3.2, max texture 16384.
T2-02 PASS: synthetic 2-pass RGBA8 FBO baseline [32,96,159,255] contrast [223,32,64,255], tolerance 2. This shows the tested FBO pipeline distinguishes two synthetic colors; does not validate original water shader or CB0.
T2-03 PASS: expected invalid unattached FBO status 0x8cd7.
T2-04 PASS: intentionally invalid fragment shader rejected.
T3-01 through T3-06: EVIDENCE_READY only, not visual PASS.
T4 cases: NEEDS_INPUT, not PASS.
Earlier phone owner evidence: https://github.com/alwansan/raf/blob/feature/android-native-port/docs/DEVICE_FEEDBACK_42058825739_AR.md ; world save/reopen confirmed on that artifact only, water still open.

## Outcome and continuation
This closes the synthetic GPU-driver/FBO contrast question for this device/pack, NOT WATER-001. No reason to rebuild an equivalent mini APK. Next: original IL producer identity/CB0 binding, plus review T3 captured screenshots; coordinate with T3/T5, do not infer Raft pixel correctness from synthetic PASS. No Unity build, no source changes, no CI launched. Work scope complete (read-only evidence triage).
