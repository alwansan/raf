# T1 scheduled — 20261111T0706Z-T1-scheduled-count-partition-5c81
origin=scheduled
baseline_sha=8d05dfc6d1132651148f94777f9b0bc70cc0e8a5
owner_device_run=42058825739
source_run_sha=e9c358eda01785b65e4eb14f18723da426635628
issue=WATER-001; readiness=NOT_READY 0/3
scope=work/T1-20261111T0706Z-T1-scheduled-count-partition-5c81.md

## Owner evidence read first
Owner entered/saved/exited/reentered world from artifact; publishing APK/OBB/XAPK failed. CL pinned at 520c4cf409aa20a4db54ff80ed87d8807d9cba57. Report aggregates: 220911-559 = 23884 water-pass, 3850 FFT; 230108-327 = 39132 water-pass, 6026 FFT. These are NOT scanner-derived totals; never compare them as such.

## Engineering
Comparator now requires kernel6_nonerror_mentions and enforces kernel6_lines == kernel6_error_lines + kernel6_nonerror_mentions. Four isolated regression cases cover consistent, underreported, overreported and boolean partitions. This closes a sanitized-input integrity gap; it does not establish original FFT kernel identity, GUID, FindKernel/Dispatch binding, Vulkan-vs-Unity numeric equivalence or device water correctness.
Recent Actions 42975017749 and 42975017713 completed success (integration checks, not GPU proof). No CI dispatched, no T4/T5 source touched. Tests are staged as source and not yet independently executed in repository.

## Next
Run python3 -m unittest discover -s scripts -p 'test_t1_kernel6_*.py' and python3 -m unittest discover -s scripts -p 'test_t1_compare_kernel6_sessions.py'; acquire each pinned CL log separately; use --errors-only scanner and verify SHA; trace first actual error to original ComputeShader/GUID and FindKernel/Dispatch; compare first divergent FFT pass with genuine Vulkan/Unity numeric captures. Recheck HEAD and team work before any edits.
