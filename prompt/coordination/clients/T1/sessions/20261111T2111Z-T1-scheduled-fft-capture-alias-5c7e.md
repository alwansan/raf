# T1 WATER-001 — 20261111T2111Z-T1-scheduled-fft-capture-alias-5c7e
origin=scheduled
date_utc=2026-11-11T21:11Z
status=source_fixed_unverified
resumed_from_sessions=20261111T1907Z-T1-scheduled-chronology-count-guard-4f2a; 20261111T1712Z-T1-scheduled-preworld-order-93ac
owner_phone=42058825739 source e9c358eda01785b65e4eb14f18723da426635628; world entered/saved/reopened from artifact; release publish failed
CL=alwansan/CL@520c4cf409aa20a4db54ff80ed87d8807d9cba57
issue=WATER-001 OPEN NOT_READY 0/3
scope=private paired RGBA32F FFT first-divergence capture provenance (not runtime Unity/Adreno)
experiment_key=fft-private-rgba-capture-alias-guard-v1
source_change=https://github.com/alwansan/raf/commit/fcb0c5c82380b6b0feb94b3066527ff1a082dea6
tests_change=https://github.com/alwansan/raf/commit/7f75485a8ef788276d6fd7a902072478a1623d71

## Finding and bounded change
The existing first-divergence CLI allowed a manifest with reference and observed resolving to the SAME regular file (including hardlinks). Such a self-comparison can incorrectly produce all_match=true, a false-positive numerical parity claim. Added reject_aliased_capture_pair after per-file confinement/size validation and before opening private pixels. Tests cover same path, hardlink, and independent byte-identical files (allowed). Existing synthetic compare_passes intentionally still accepts equal byte values; only manifest file provenance is guarded. Source/3 tests published; execution in CI not verified this cycle. No private pixel values, original game data or secrets published.

## Next
Run tests/test_t1_fft_first_divergence.py via cheap CI; check real paired capture manifests have distinct source/reference files and authenticated build/asset provenance. Follow actual original FFT resource GUID, named kernels/FindKernel, direct Dispatch metadata on same game build and first Vulkan/Unity numerical divergence. Do not infer GPU success from synthetic captures. T4 physical mouse and T5 right-side controls/Resolution remain distinct scopes. No game APK or Unity job started.
