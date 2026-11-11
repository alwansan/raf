# T1 WATER-001 session
session_id: 20261111T0514Z-T1-scheduled-comparison-invariants-c7d2
origin: scheduled
resumed_from_sessions: 20261111T0415Z-T1-scheduled-cross-session-triage-7a2d (prior report; verify file path), 20261109T185616Z-T1-chat-fft-audit-run-34c243
base_sha: 6f9992fd647103234f4b1dfbcd932bf3a7f3555b (scope commit)
issue_id: WATER-001
experiment_key: kernel6-sanitized-compare-invariants-v1
status: source_fix_published_tests_not_executed

## Evidence
Read docs/DEVICE_FEEDBACK_42058825739_AR.md first: 42058825739 source e9c358eda01785b65e4eb14f18723da426635628; world entry/save/reentry from Artifact succeeded; package publication failed. CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57; 220911-559 water 23884/kernel 3850, 230108-327 water 39132/kernel 6026; these are session summary counts not original runtime kernel identity.
Read current owner requirements and team chat/schedule protocol, AGENTS/STATUS and earlier T1 memory. Current owner update 8 Nov adds shared mini-lab and newer CL evidence. Do not infer new device proof.
Reviewed scripts/t1_compare_kernel6_sessions.py and five existing synthetic regression tests. Found validation accepted sampled error event when kernel6_error_lines=0 and accepted boolean sampled_hits=True as integer equality to 1. This could make fabricated/inconsistent summary appear comparable.
Source fix commit 966f7ab167fbe19e369f39462d0d742aceb74bd3 adds two fail-closed checks; regression commit f9a242dfb61a34943455138c026225794f7a7696 adds two tests. No game source, shader, .meta, GUID, audio, settings or save data changed.
Local git ls-remote failed DNS: Could not resolve host github.com. GitHub connector fetch and writes succeeded. Full Python test execution and CL real-log scan not yet performed; no Unity/Adreno/phone proof; no CI dispatched. No Actions cancelled.
Scope: prompt/coordination/clients/T1/work/20261111T0514Z-T1-scheduled-comparison-invariants-c7d2.md. Avoid T4 mouse and T5 Resolution/packaging overlap.

## Next
Run python3 -m unittest discover -s scripts -p 'test_t1_compare_kernel6_sessions.py' in checked-out repo, then execute both sanitized scans from pinned CL sessions with exact source hashes. Trace original ComputeShader GUID, actual Unity FindKernel and Dispatch and first divergent FFT numeric pass; original compiled program slot 6 != runtime kernel ID 6 without proof. WATER-001 OPEN; NOT_READY 0/3.
