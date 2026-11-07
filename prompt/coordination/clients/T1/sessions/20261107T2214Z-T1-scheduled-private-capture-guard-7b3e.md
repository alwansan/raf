# T1 scheduled — 20261107T2214Z-T1-scheduled-private-capture-guard-7b3e
origin: scheduled
identity: T1
track: WATER-001
baseline_sha: 2ac5c39417ac912060286f54cd9ff38fc26a3a22
scope_commit: a03c2e4ed21a490f002e3433deb965eb0824332f
source_commit: 0b2c6b187ea40cd4fcb45b886563e8989baf7e8f
tests_commit: 197e40d7d1ca9d97d08eff689943b7260df51ee7

## Owner/device baseline
Read docs/DEVICE_FEEDBACK_42058825739_AR.md first. Owner entered world, saved and re-entered from artifact 42058825739; publishing failed. CL pinned 520c4cf; 220911-559: water passes 23884, kernel 3850; 230108-327: passes 39132, kernel 6026. These are observed log categories, not established causal FFT kernel identity. Prior T1 original FFT CPU Vulkan and Unity probe evidence remains separate; no numeric Unity/Adreno parity established.

## Distinct engineering action
Audited existing scripts/t1_fft_first_divergence.py, which previously joined manifest paths and called read_bytes() without directory confinement, symlink rejection or per-file size limit. This could read arbitrary files or exhaust CI memory before any FFT comparison. Added read_private_capture(): reject absolute and parent traversal paths, symlink components, paths escaping the manifest directory, zero/non-RGBA32F-multiple/oversized captures; cap reads at 64 MiB and manifest at 1 MiB. Added source-free regression cases for valid files, traversal, absolute paths, file/directory symlinks, empty/partial/oversized files. No original game files were published or changed.

## Validation and limits
Code and tests committed; test execution is NOT established because container git network DNS cannot resolve github.com and there is no local checkout. No Unity, Vulkan GPU, Android device, CI or APK build triggered. Current branch head after test commit: 197e40d7d1ca9d97d08eff689943b7260df51ee7. The file confinement is not a proof of original FFT identity or water correctness. Potential race between stat and open remains for malicious concurrent filesystem mutation; use immutable private staging.

## Next
Execute python -m unittest tests.test_t1_fft_first_divergence_capture_guard on a fresh checkout, then obtain authenticated paired Vulkan/Unity FFT per-pass captures in isolated private staging; compare first mismatch and actual FindKernel/Dispatch trace. Preserve T4 mouse and T5 Resolution/button scopes, and WATER-001 OPEN / NOT_READY 0/3.
