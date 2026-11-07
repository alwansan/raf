# T1 WATER-001 — private FFT capture confinement
session_id: 20261107T2214Z-T1-scheduled-private-capture-guard-7b3e
origin: scheduled
baseline_sha: 2ac5c39417ac912060286f54cd9ff38fc26a3a22
scope: scripts/t1_fft_first_divergence.py; tests/test_t1_fft_first_divergence_capture_guard.py; isolated session and work files
hypothesis: existing private manifest accepts absolute paths, ../ traversal and symlinks and reads unbounded capture bytes. This can leak private metadata or exhaust CI memory before numeric Vulkan/Unity comparison.
experiment_key: T1-FFT-PRIVATE-CAPTURE-PATH-GUARD-7b3e
shared_resource: none; no Unity/CI run requested
owner baseline: device feedback 42058825739 world/save/reopen confirmed; water kernel6 and Spectrum/Foam errors open.
prior evidence: T1 20261107T2110Z-T1-scheduled-fft-evidence-a4d9; no authentic paired captures yet.
planned validation: synthetic isolated manifests for in-directory regular files, traversal, absolute paths, symlinks, oversized input; no game resources.
status: source_fixed_unverified_tests
source_commit: 0b2c6b187ea40cd4fcb45b886563e8989baf7e8f
test_commit: 197e40d7d1ca9d97d08eff689943b7260df51ee7
session_commit: c723147732521178095f425ae3a86877bee13ea2
validation: tests committed but not executed; local checkout unavailable due DNS; no GPU/device claims
next_step: execute regression suite on a checkout; then authentic paired Unity/Vulkan FFT capture
