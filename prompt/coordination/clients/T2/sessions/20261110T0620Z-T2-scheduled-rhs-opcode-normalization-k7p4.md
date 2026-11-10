# T2 scheduled checkpoint — 2026-11-10 06:20 UTC
session_id: 20261110T0620Z-T2-scheduled-rhs-opcode-normalization-k7p4
origin: scheduled
base_sha: 54fd9143eda9a10b6ac9f29879e98f8caa0985d9
resumed_from_sessions: T2 scheduled 2026-11-10 Foam RHS guard (160c77efc6c41c7181ae2df63e395b3dec8c5ea1, tests 4307592c7ff1c3946fe437b20d5f05155010075d); historical T2 chat state 20261108T1956Z-T2-chat-pass1-source-kind-4d6a.
owner_device_baseline: 42058825739, original e9c358eda01785b65e4eb14f18723da426635628; world/save/reopen PASS from artifact, package publishing failed, water/FFT NOT_FIXED.
work: prompt/coordination/work/WATER-001/20261110T0620Z-T2-scheduled-rhs-opcode-normalization-k7p4.md
result: Recognized only operand-free CIL ldloc.0..3 and ldarg.0..3 as LOCAL_READ and ARGUMENT_READ. Previous classifier returned UNKNOWN for these legitimate CIL opcodes. Deliberately reject ldloc.s/ldarg.s without separate operand provenance, ldloca/ldarga, noncanonical indices. Does NOT prove local index, receiver alias, runtime Texture identity or ShaderLab.
commits: code 804c61b963e49865c758066ace0e4356264d706f; tests d3848e969918c82a8f1c30b340813ab3a447a4a9.
validation: eight short-form examples and seven negative/edge examples exercised in local Python reproduction; current repository unittest suite not run in this cycle. No Unity/CI build dispatched. No original DLL analyzed this cycle.
status: source-only improvement; WATER-001 OPEN, NOT_READY 0/3.
next_step: run repository unittest suite on immutable SHA; feed original Cecil opcode slices only after explicit operand/receiver and CFG validation. Coordinate with T3 on fire/smoke but do not edit T3-owned shader paths.
