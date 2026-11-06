# T1 scheduled | 20261106T1215Z-T1-scheduled-coordinate-overflow-r6q2

- origin: scheduled
- issue_id: WATER-001; remains OPEN; NOT_READY 0/3.
- resumed_from_sessions: 20261106T110837Z-T1-scheduled-fft-first-divergence; 20261106T113707Z-T1-chat-bitcarrier-producer-c8f1.
- initial_head: 1cc26ea5c9b525d07e3b7116f0caf9fa034c2920
- work_reservation_commit: d9f7816342946691b5636cd9efc2772c5e000340
- source_commit: 61ce53f0f3523927bc7e782c2c4080ddcdbdf7cf
- tests_commit: 04f9c9782b49fd6e37ce190ca3c42b3b6d20f218
- exact_files: scripts/t1_fft_coordinate_probe_compare.py; tests/test_t1_fft_coordinate_probe_compare.py
- experiment_key: fft-coordinate-probe-overflow-and-resource-bound-regression-v1
- resource_key: source-only-python-no-gpu

## Latest owner and original evidence
Read docs/DEVICE_FEEDBACK_42058825739_AR.md before prioritizing. Owner confirmed entering/saving/reopening world from run 42058825739 artifact; publication failed. Pinned original phone logs 220911-559: 23,884 water-pass and 3,850 FFT kernel errors; 230108-327: 39,132 water-pass and 6,026 kernel errors. This remains a graphics failure despite world success. Most recent original FFT branch evidence: CI 42212055131 SUCCESS, 13/13 typed carrier tests and SHA-authenticated original slot0 private Vulkan audit. Site1 Y has signed-32-bit bitcarrier and float constant as MAY-reaching candidates, not proven runtime branch. The source-only comparator is independent of that active chat investigation.

## Concrete source correction
Existing coordinate-keyed Vulkan/Unity probe reader called math.isfinite on unbounded JSON integer; Python raises OverflowError for a 400-digit integer, bypassing the declared invalid-value ValueError. Independently, arbitrary-sized capture files/arrays could exhaust memory before comparison. Added bounded binary read (2 MiB + 1 sentinel), max 8192 samples, explicit finite float conversion with OverflowError handling. Four new regression tests cover oversized integer, bytes, sample count, and normal valid capture. No original game data used.

## Verification and limits
Local minimal Python reproducer confirmed pre-fix OverflowError and post-fix numeric guard accepts finite values/rejects overflowing integer. Full updated repository tests **not run**: sandbox cannot resolve github.com for clone; no new CI dispatched. This is a source-only parser robustness improvement, **not** original Vulkan↔Unity numerical parity, FindKernel mapping, Adreno water, or phone verification. Existing 42212055131 green CI predates these changes. Last checked branch HEAD 04f9c9782b49fd6e37ce190ca3c42b3b6d20f218; no active workflow in most recent 12-run listing. No T4 mouse or T5 Resolution edits; sound/Settings preserved.

## Next
Run python -m unittest tests.test_t1_fft_coordinate_probe_compare on exact commit or dedicated light CI, then feed SHA-pinned paired Vulkan/Unity coordinate samples. In parallel, isolate original butterfly site1 Y bitcarrier vs float-constant control-flow predicate (latest T1 chat result) without leaking private values. Do not equate static may-reach with actual dispatch.