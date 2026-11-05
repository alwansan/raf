# T4 LOCAL-005 — exact original SaveAndLoad world-RGD factory returned-local assignments

Date: 2026-11-05, T4 chat session `20261105T1736Z-T4-chat-rgd-return-local-stores-r6n8`; origin=chat. This is a read-only **source-authentic compiled CIL** experiment, not an execution of the original game or serialization.

## Starting verified original code

Immutable owner-supplied ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, exactly `Raft/Raft_Data/Managed/Assembly-CSharp.dll` **3,211,776 bytes**, SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`. The isolated workflow validates commit, length and SHA before .NET8 Mono.Cecil 0.11.5 read-only inspection, rejects one-byte mutated input and does not upload original game DLL/IL/member names, scripts/bytecode, RGD bytes or private game artifacts.

Original compiled world save `SaveWorld` invokes its authentic private `Save(string,RGD)` with a derived-RGD typed local. Prior [CI42072718216](https://github.com/alwansan/raf/actions/runs/42072718216) SUCCESS 50/50 showed the world local was assigned by a zero-argument instance method inside `SaveAndLoad`, which has exactly one compiled return site, immediately preceded by a local load of derived RGD type. That factory contains two derived RGD typed local slots, one direct derived constructor site, one direct call returning derived RGD, 34 conditional branches, 10 null literal loads, and no explicit throw/rethrow. The prior census **did not** identify whether the returned local was the one constructed.

## Distinct original returned-local assignment evidence

This cycle identifies the exact local slot used by the original factory's single `ret` and counts **lexically preceding** `stloc` instructions to that slot. It categorizes the immediate preceding original CIL instruction for every such store as a derived-RGD constructor, derived-RGD returning call, local, field, null literal, or unknown. It also reports the category of the nearest such lexical store, never actual original private method names, raw instructions or user game objects. Static adjacency is not stack/SSA branch-path equivalence.

[**CI42076494669 COMPLETED SUCCESS**](https://github.com/alwansan/raf/actions/runs/42076494669) at exact tested source `961e637a5236ed900c179fe41b96e5f65a26084b`:
- **67/67** original-free Python unit and adversarial safety tests passed; original .NET8 Mono.Cecil program compiled and inspected the genuine SHA-verified original DLL; one-byte altered SHA was refused before analysis.
- `factory_return_local_lexical_store_sites=1`: precisely **one** lexical store to the local loaded immediately before the original factory's one `ret`.
- `factory_return_local_store_derived_constructor=1`: that sole store has an immediately preceding instruction constructing a type derived from original `RGD`.
- `factory_return_local_nearest_lexical_store_source=DERIVED_CONSTRUCTOR`, matching the direct `newobj` → `stloc` local assignment pattern in the original compiled source.
- `factory_return_local_store_derived_call=0`, `factory_return_local_store_derived_local=0`, `factory_return_local_store_derived_field=0`, `factory_return_local_store_null_literal=0`, `factory_return_local_store_other_or_unknown=0`. These zeroes concern **this returned slot's immediate lexical stores only**, not other local variables, branches, calls, fields, static initialization, null state or exceptions.
- Existing original-context evidence unchanged: one `ret` preceded by this local load, two derived-RGD local slots overall, one direct derived-RGD constructor in method, one separate derived-RGD returning method call, 34 conditional branch opcodes, 10 `ldnull` opcodes. The derived-returning method call did **not** immediately feed a direct `stloc` to the returned slot in this structural census.

## Confidence boundaries

**Newly ruled out at an immediate lexical level:** multiple direct stores to the returned local, a direct null literal store to that local, or a direct derived-RGD call return store to that same local. **Not ruled out:** execution paths that never reach the constructor/return; exceptions from invoked dependencies; null returned through other aliased/object fields or state; side effects and persistence failures. The code has conditional branches, and the experiment is deliberately **not** a branch-reachability analysis or runtime test. Neither `newobj` presence nor `stloc`/single return proves a playable world or durable save.

Explicit fail-closed output: `factory_control_flow_paths_or_runtime_values_proven=false`, `derived_RGD_runtime_value_initialized_proven=false`, `same_world_saved_or_reopened_proven=false`, `Android_Unity_IL2CPP_phone_executed=false`, `original_game_payload_published=false`. No original game Save, world creation, RGD file read/write, process exit/restart or Unity/Android phone executed.

## Work and integration

Only T4 read-only experiment files changed:
- `android-port/Experiments/T4/OriginalRgdInitContext/Program.cs` commit `56febeb463799881dc561c609f3b55a59faf825a`.
- `scripts/t4_validate_original_rgd_init_context.py` commits `a7366262b312bbfb2b92934fbd82c61a944871f9` and `961e637a5236ed900c179fe41b96e5f65a26084b` (source-free declaration ordering fix).
- `tests/test_t4_validate_original_rgd_init_context.py` commit `c4b0a987a7c367d31ca6f23766d34dd18b1d6353`; 17 additional original-free controls (50 → **67**).
- Existing, path-scoped `.github/workflows/raft-t4-original-rgd-init-context.yml` auto-tested source changes, no changes to native game workflow, original Unity/assets, serialization/GUID/.meta, audio, Settings or touch.
- Intermediate [CI42076168719](https://github.com/alwansan/raf/actions/runs/42076168719), [CI42076257372](https://github.com/alwansan/raf/actions/runs/42076257372) and [CI42076369962](https://github.com/alwansan/raf/actions/runs/42076369962) failed as modifications were published in stages. The final intermediate failure was source-free validator import `NameError` (fields referenced before declaration), fixed without weakening any original-SHA or false-device claim guard. **Only matched CI42076494669 is final success; failures were not original-game or Android save failures.**

T4 scheduled 16:40Z work owns distinct source-free device JSONL queue-overflow verification; no overlap. T5 native Unity [CI42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) remained IN_PROGRESS at Editor Android import at previous verified checkpoint; no new signed APK/OBB/XAPK or actual phone completion can be inferred. No T4 Unity/native build dispatched/cancelled.

## Next acceptance

Use authentic original factory return-local provenance to direct Android runtime instrumentation only if the actual new candidate and device logs show missing initialization. Otherwise avoid modifying a path that is structurally valid. Accept LOCAL-005 only from **playable offline world → real world/user `.rgd` written durably → complete process exit → same-world playable reopen** on the actual APK/OBB/XAPK, preserving B50 Steam guards, original `.rgd` compatibility, GUIDs/.meta and local-host behavior. **LOCAL-005 OPEN; NOT_READY 0/3.**
