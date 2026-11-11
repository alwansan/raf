# T1 scheduled session — 2026-11-11 12:10 UTC
session_id: 20261111T1210Z-T1-scheduled-fft-ambiguous-nearest-8e31
origin: scheduled
issue: WATER-001
baseline_sha: 83a6a7d9f200640f17dbc4e81a8837ec6a283582
observed_head_after_changes: 27dc4044cf049acc84e4de35ba13ea5134684aad
owner_device_baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md (42058825739; world entry/save/reentry confirmed, water FFT unresolved)
work: prompt/coordination/T_TEAM/work/T1/20261111T1210Z-T1-scheduled-fft-ambiguous-nearest-8e31.md
source_commit: ace115a2878296a50050bb41342b245cc14ca44c
regression_commit: 27dc4044cf049acc84e4de35ba13ea5134684aad

## Engineering result
Prior nearest-marker algorithm used tuple min(distance,pass,direction) and silently selected alphabetically first pass for equally near distinct passes, or lexicographically first direction for equal-distance markers. That is not an evidentiary basis for selecting a program. New algorithm separates unique nearest from ambiguous nearest, de-duplicates repeated identical markers, and reports safe aggregate ambiguous bins. Added five synthetic regression cases (distinct pass tie, duplicate pass, before/after tie, nearer wins, unmatched).

## Verification and limitations
Code and regression source published. Local Python execution unavailable because container cannot resolve raw.githubusercontent.com (curl exit 6); CI was not launched, and these tests are NOT claimed passed. No raw CL scan executed. No proof of original ComputeShader GUID, FindKernel, Dispatch or numeric Vulkan/Unity equivalence. No phone/GPU run. Existing 2026-11-08 unified mini lab and T4/T5 input/resolution scopes unchanged.

## Next
Run python -m unittest scripts/test_t1_fft_pass_proximity_ambiguity.py with scripts on sys.path, and existing t1 proximity tests; if failures, fix while retaining unique nearest output contract. Then process sanitized CL 220911-559 and 230108-327 independently, check first actual FFT error and nearby water pass. Obtain original program GUID/kernel mapping and numeric first mismatch using pinned source; no identity inference from log proximity. WATER-001 OPEN NOT_READY 0/3.
