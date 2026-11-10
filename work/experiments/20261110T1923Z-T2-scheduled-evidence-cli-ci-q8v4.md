# T2 WATER-001 scope 20261110T1923Z-T2-scheduled-evidence-cli-ci-q8v4
origin: scheduled
baseline_sha: dad5efb4ab8540d947ea0d6ba6ef680e12991b56
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL@520c4cf; run 42058825739
hypothesis: The newly committed Foam evidence sanitizer CLI regression has no dedicated Actions runner, so source-only changes can remain untested despite prior test publication.
experiment_key: T2-FOAM-EVIDENCE-CLI-CI-20261110
files: .github/workflows/raft-t2-foam-evidence-cli-gate.yml; clients/T2/sessions/20261110T1923Z-T2-scheduled-evidence-cli-ci-q8v4.md; this work file
shared_resource: GitHub Actions ubuntu-24.04 source-only 5-minute job; no Unity, no LFS, no native build
non_overlap: New isolated workflow and unique session/work files; T1 FFT, T3 effects, T4 mouse, T5 packaging untouched.
readiness: WATER-001 OPEN; NOT_READY 0/3
