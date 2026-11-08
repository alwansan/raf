# T1 WATER-001 scoped work — 20261108T1714Z-T1-scheduled-fft-shared-lab-b6d2
origin: scheduled
base_sha: 31412fcbd7b0db23c4c07787c1ce1e6dbfe06caf
scope: FFT original-kernel attribution and unified lab evidence gate (read-only audit, no overlapping shared driver edits).
experiment_key: t1-fft-unity-vulkan-first-divergence-20261108
resource_key: none (no Unity/GPU job).
intended_files: this work record; prompt/coordination/clients/T1/sessions/20261108T1714Z-T1-scheduled-fft-shared-lab-b6d2.md
evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; apk-for-testing/OWNER_FEEDBACK_2026-11-08_AR.md; apk-for-testing/unified/pack/team-testpack.json
hypothesis: synthetic GLES SSBO success can exclude some driver-wide failures but cannot identify original Unity FFT FindKernel index 6 or water invalid pass root cause. Need matched shader provenance and same-input per-pass readback.
non_overlap: T4 physical mouse; T5 unified APK/build/readiness; T2 water pass materials. No shared testpack or driver edits.
status: IN_PROGRESS; do not launch duplicate CI while shared mini source compile 42503889895 is in_progress.
