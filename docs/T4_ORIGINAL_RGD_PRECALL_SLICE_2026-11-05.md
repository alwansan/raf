# T4 LOCAL-005 — original SaveWorld/SaveUser private RGD pre-call type origin classifier

## New, distinct question

Original managed [T4 CI42053882300](https://github.com/alwansan/raf/actions/runs/42053882300) confirmed one original Save(string,RGD) call each in SaveWorld and SaveUser, but neither a direct RGD constructor nor generic Load<RGD> occurs in either. The immediate pre-call type source was UNKNOWN. A 2,941-byte shipped StreamingAssets/Data.rgd root is a different original CLR type, proven in [CI42047540260](https://github.com/alwansan/raf/actions/runs/42047540260); it cannot serve as world RGD fixture.

This new experiment makes an independent **read-only** Mono.Cecil 0.11.5 structural classification of the instruction preceding each genuine Save(string,RGD) call (ignoring NOPs), with metadata type relation: EXACT_RGD, DERIVED_RGD or OTHER_OR_UNRESOLVED. Cases include field load, local, constructor, call return, cast/box, branch/null/stack uncertainty. Output is a finite source-free category, not original code/opcode/type/member/field identity.

ZIP2 immutable provider commit 15964ea8f246b6e076ce26b60931ee2e1a9a2385; original Assembly-CSharp.dll 3,211,776 bytes SHA256 0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e, original byte SHA rechecked before inspection. No original serialization, player/world object construction, original method invocation, save files, Android/Unity/IL2CPP or game project modification. Static pre-call adjacency alone is not SSA identity proof, especially around branches or compound expressions.

## Repro and safety

Isolated project `android-port/Experiments/T4/OriginalRgdPrecallSlice`, Python strict output verifier `scripts/t4_validate_original_rgd_precall_slice.py`, and synthetic controls `tests/test_t4_validate_original_rgd_precall_slice.py`; workflow `.github/workflows/raft-t4-original-rgd-precall-slice.yml` with no payload artifacts, independent concurrency, pinned checkout and negative SHA check.

## Results

[**CI42058900699 SUCCESS**](https://github.com/alwansan/raf/actions/runs/42058900699) at exact source commit `71cd16300ab995f4da4e0a7f0be24d1b90fa61e5`: **22/22 source-free negative/safety tests**, .NET8/Mono.Cecil v0.11.5 compile, immutable original DLL SHA/size verification before read-only IL inspection and rejection of mutated original SHA. The original compiled `SaveWorld` immediate pre-call was classified **`LOCAL_DERIVED_RGD`**: a local variable's declared type derives from original `RGD`. Original `SaveUser` immediate pre-call classified **`FIELD_DERIVED_RGD`**: a field whose declared type derives from the original `RGD`. Both were independently matched to the exact original `Save(string,RGD)` compiled call sites. No original game Save method, file write/read or serialized object was executed.

This supports a bounded, **structural** subtype relationship, not actual object identity or initialized runtime data. The classifying instruction immediately preceding the call is not a complete branch-aware stack/SSA provenance proof, nor does it show where SaveWorld's local was assigned or SaveUser's field initialized. Attempts to extend this cycle's inspector to last lexical local store and field declaration/write counts were not published due tool safety checks; those **additional** hypotheses remain untested and no new CI evidence was claimed for them.

**Next:** inspect the assignment and initialization of those derived RGD types in a distinct, permitted original-source experiment, or prioritize the next T5-coordinated signed native candidate after the strict water gate is resolved. Native [run42052375742](https://github.com/alwansan/raf/actions/runs/42052375742) failed at strict water validation before Editor package, not at Save/Load or Android device. Owner must still demonstrate actual offline playable world → authentic user-generated .rgd save → full process exit → reopen same world playable. LOCAL-005 **OPEN**, overall **NOT_READY 0/3**.
