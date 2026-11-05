# T4 LOCAL-005 — original SaveWorld/SaveUser private RGD pre-call type origin classifier

## New, distinct question

Original managed [T4 CI42053882300](https://github.com/alwansan/raf/actions/runs/42053882300) confirmed one original Save(string,RGD) call each in SaveWorld and SaveUser, but neither a direct RGD constructor nor generic Load<RGD> occurs in either. The immediate pre-call type source was UNKNOWN. A 2,941-byte shipped StreamingAssets/Data.rgd root is a different original CLR type, proven in [CI42047540260](https://github.com/alwansan/raf/actions/runs/42047540260); it cannot serve as world RGD fixture.

This new experiment makes an independent **read-only** Mono.Cecil 0.11.5 structural classification of the instruction preceding each genuine Save(string,RGD) call (ignoring NOPs), with metadata type relation: EXACT_RGD, DERIVED_RGD or OTHER_OR_UNRESOLVED. Cases include field load, local, constructor, call return, cast/box, branch/null/stack uncertainty. Output is a finite source-free category, not original code/opcode/type/member/field identity.

ZIP2 immutable provider commit 15964ea8f246b6e076ce26b60931ee2e1a9a2385; original Assembly-CSharp.dll 3,211,776 bytes SHA256 0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e, original byte SHA rechecked before inspection. No original serialization, player/world object construction, original method invocation, save files, Android/Unity/IL2CPP or game project modification. Static pre-call adjacency alone is not SSA identity proof, especially around branches or compound expressions.

## Repro and safety

Isolated project `android-port/Experiments/T4/OriginalRgdPrecallSlice`, Python strict output verifier `scripts/t4_validate_original_rgd_precall_slice.py`, and synthetic controls `tests/test_t4_validate_original_rgd_precall_slice.py`; workflow `.github/workflows/raft-t4-original-rgd-precall-slice.yml` with no payload artifacts, independent concurrency, pinned checkout and negative SHA check.

## Results

Await actual original-source CI. Even successful static classification may require additional original type/method provenance and cannot prove local-world ready, same-world save/reload or Android native behavior. LOCAL-005 OPEN, NOT_READY 0/3.
