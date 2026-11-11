# T1 scheduled checkpoint — 20261111T1612Z-T1-scheduled-fft-dedup-7e91
session_id: 20261111T1612Z-T1-scheduled-fft-dedup-7e91
origin: scheduled
baseline_sha: f5891f15c3731e6487adf2f750388a53faca8901
owner_device: 42058825739 / e9c358eda01785b65e4eb14f18723da426635628
CL_snapshot: 520c4cf409aa20a4db54ff80ed87d8807d9cba57
resumed_from: 20261111T1307Z-T1-scheduled-provenance-6d29; 20261111T1210Z-T1-scheduled-fft-ambiguous-nearest-8e31
work: prompt/coordination/T_TEAM/work/T1/20261111T1612Z-T1-scheduled-fft-dedup-7e91.md

## Result
Source-only diagnostic integrity fix: reject duplicate sampled error line IDs, including nonadjacent duplicates and differing pass labels, to prevent inflated proximity histogram counts. Adds three synthetic regression cases. This does not establish original kernel identity, causality, Vulkan/Unity numeric parity or GPU correctness. Tests not run in GitHub Actions; run PYTHONPATH=scripts python -m unittest scripts/test_t1_fft_pass_proximity_duplicate_lines.py.

## Evidence
Device report confirms world entry/save/reentry from Artifact; published package delivery failed. Session 220911-559: 23,884 water pass errors, 3,850 FFT errors; 230108-327: 39,132 pass errors, 6,026 FFT errors. Do not compare raw counts as performance without normalized duration and workload. kernelIndex 6 cannot be mapped to Unity kernel without original ComputeShader GUID/name and FindKernel/Dispatch runtime evidence.

## Next
Run tests on repository checkout. Apply sanitized scan to pinned CL logs, then identify authentic ComputeShader/.meta GUID and Unity kernel binding, thread-group sizes and first numeric mismatch. WATER-001 OPEN / NOT_READY 0/3. Do not duplicate T4/T5 work or Unity builds.
