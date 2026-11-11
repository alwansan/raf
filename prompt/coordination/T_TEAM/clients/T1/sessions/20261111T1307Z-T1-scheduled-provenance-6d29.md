# T1 scheduled checkpoint — 2026-11-11 13:07 UTC
session_id: 20261111T1307Z-T1-scheduled-provenance-6d29
origin: scheduled
resumed_from_sessions: 20261111T1210Z-T1-scheduled-fft-ambiguous-nearest-8e31; 20261111T0605Z-T1-scheduled-endtoend-log-contract-a73e
base_sha: bbff0465f001167663ec46a48fb53feba064d591
scope_commit: 1906345762953a7c4982e8489feeb533cf77c29a
source_commit: c9fe3eaf825a51c691bb873de0f5a87d62d49632
test_commit: 0ad7337b6c6783e0c3dabcd4937b59d9bd0df0f4
work: prompt/coordination/T_TEAM/work/T1/20261111T1307Z-T1-scheduled-provenance-6d29.md
issue_id: WATER-001

## Owner device evidence
docs/DEVICE_FEEDBACK_42058825739_AR.md, run 42058825739 source e9c358eda01785b65e4eb14f18723da426635628. World entry/save/reentry confirmed via Artifact, not package publication. CL immutable snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57. 220911-559: 23,884 water-pass errors, 3,850 FFT kernel errors; 230108-327: 39,132 and 6,026. No inference of causality or GPU pass identity from counts.

## Engineering result
The proximity tool previously indexed scan["session_id"] and scan["source_sha256"] only at return time; absent metadata raised KeyError after aggregation and malformed identifiers were emitted without verification. Added early validation of nonblank bounded session identifier and exactly 64 lowercase hexadecimal source digest, and a separate synthetic regression suite covering missing, malformed and valid provenance. Does not touch existing tie handling or T2 water pass code. This is a diagnostics-integrity improvement, NOT original program binding proof.

## Verification / limits
GitHub source/test commits published. Container curl to raw.githubusercontent.com failed DNS resolution (exit 6), so repository tests were NOT executed here. No CL raw scan, Vulkan/Unity numerical comparison, FindKernel/Dispatch instrumentation, GPU run, Unity build, APK or phone test. Latest HEAD before work bbff0465f001167663ec46a48fb53feba064d591. No Actions launched; T2 workflow 43020319051 failed and requires separate owner triage. T4 mouse/pointer and T5 Resolution/three buttons remain independent scopes; general touch layout deferred.

## Next
Execute PYTHONPATH=scripts python -m unittest scripts/test_t1_fft_pass_proximity_provenance.py scripts/test_t1_fft_pass_proximity.py and ambiguity suite. Process CL sanitized scans separately; inspect first real FFT error and pass association; verify ComputeShader asset GUID, kernel name/index, FindKernel and Dispatch, then first numeric Vulkan/Unity divergence with pinned inputs. WATER-001 OPEN / NOT_READY 0/3.
