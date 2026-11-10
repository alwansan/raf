# T1 scheduled session — 20261110T1110Z-T1-scheduled-first-divergence-6d31

origin: scheduled
baseline_sha: 58f770fe2e350169d3d7ecc6fba9512434da11c2
scope_commit: ceca4009c1ad60009902a8a1f83cf3d3ceffeb25
code_commits: a6858dec47b48c046150b957f98528ddb8f048d7, 2fd0eb93ee0248681e5bc252aef51a34852b00c9

## Verified owner evidence and constraints
Read docs/DEVICE_FEEDBACK_42058825739_AR.md before priorities: world entered/saved/reentered on phone from artifact of run 42058825739; package publication/delivery failed. CL session 220911-559: 23884 water pass errors and 3850 FFT kernel errors; 230108-327: 39132/6026. These are session-local counts, not unique faults or a causal ordering. No original FFT GPU evidence yet. AGENTS and owner requirements prioritize unified mini lab since Nov 8; T4 mouse, T5 Resolution/three buttons; no shared file touched.

## Work
Reviewed existing scripts/t1_fft_first_divergence.py and tests: strict bounded private RGBA32F comparison already exists, so did not overwrite concurrent work. Added separate metadata-only scripts/t1_fft_readback_provenance.py with 4 regression tests: immutable build SHA, paired Vulkan/Unity capture sizes, unique passes, SHA256 digests and RGBA32F alignment; outputs metadata only and explicitly leaves gpu_execution_proven and original_kernel_binding_proven false. No private game data emitted. Local unittest attempt blocked because container DNS cannot resolve raw.githubusercontent.com; CI not launched, tests NOT VERIFIED. The separate original scope title first-divergence was adapted to provenance gate after discovering existing comparator.

## Remaining
Read current HEAD, run tests on exact SHA containing 2fd0eb93, obtain actual paired GPU captures from same build/session, and prove Unity original FindKernel/Dispatch binding before interpreting numerical divergence. Do not claim readiness. WATER-001 OPEN / NOT_READY 0/3. Avoid duplicate CI and T4/T5 files.
