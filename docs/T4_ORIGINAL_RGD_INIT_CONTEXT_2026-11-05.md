# T4 LOCAL-005 — original world producer / user derived-RGD initializer context (5 Nov 2026)

This experiment inspects only exact original compiled CIL with immutable ZIP2 `Assembly-CSharp.dll` 3,211,776B SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`. It does NOT execute game source, load original .rgd, publish proprietary class/member identifiers, rebuild Unity or prove Android correctness.

Prior authenticated [CI42062124798](https://github.com/alwansan/raf/actions/runs/42062124798) SUCCESS 36/36: `SaveWorld`'s derived-RGD local has exactly one lexical store directly preceded by a call returning a derived-RGD type; `SaveUser` has a derived-RGD field declared by `SaveAndLoad` with exactly three original direct store sites. This proves neither the value's identity nor executed control flow.

New independent experiment: classify the direct call's owner as SaveAndLoad / another original compiled type / external-unresolved, its invocation kind and arity and whether the specific callee has a compiled original method body. Partition the three direct SaveAndLoad-owned SaveUser field store sites by containing method categories and by immediately preceding instruction's data type (null literal, derived-RGD typed, or unknown). No private IL, source, type or method names, bytecode, binaries, RGD content, saved world/player fields or log paths in public report. These are static lexical classifications only. No source changes to actual gameplay or serializer.

Source-free negative controls and an isolated, path-scoped `.github/workflows/raft-t4-original-rgd-init-context.yml` check report schema, impossible counts, false game/device claims, exact original SHA, and altered-source rejection. Other T4 scheduled JSONL overflow check remains separate. T5 native build #42058825739 continues its own Unity import; T4 does not interfere.

## CI result

[**CI42068520588 SUCCESS**](https://github.com/alwansan/raf/actions/runs/42068520588) at source commit `2e54986dbc7cbd8295c6bae5a03ef5851d24be35`: **32/32** original-free adversarial Python controls; .NET 8 / Mono.Cecil 0.11.5 probe compiled, read-only inspected authenticated original ZIP2 `Assembly-CSharp.dll` (3,211,776 bytes, SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`), and rejected a one-byte changed DLL before inspection. No original private output was uploaded.

**Original SaveWorld derived-RGD producer:**
- `world_producer_owner_scope=SAVEANDLOAD`: direct original method's declaring type is `SaveAndLoad`, not a different original class.
- `world_producer_arity=ZERO`, `world_producer_invocation=INSTANCE_CALL`: the unique lexical assignment to the world RGD-derived local is immediately preceded by a call to a **zero-argument instance method** on the original `SaveAndLoad` owner.
- `world_producer_original_method_body_exists=true`: original resolved compiled method body is present in the exact original owner DLL. This narrows where a future source instrumentation or guarded analysis should focus, without declaring that the method actually executed or its return value is non-null.

**Original SaveUser RGD-derived field's three direct lexical write sites:**
- `user_field_writes_in_saveuser=1`, `user_field_writes_in_other_saveandload_methods=2`. No direct write sites in any constructor, SaveWorld, or other type in this inspected module.
- Immediate prior instruction categories partition as `derived-RGD typed=2`, `null-literal=0`, `unknown-or-other=1`. Absence of *immediate* `ldnull` sites is not proof the field is non-null. The 3 counts are direct CIL field stores, not runtime branching or initialization success.
- The producer and store site results do **not** reveal actual original method/member names other than public known `SaveAndLoad`, `SaveWorld`, `SaveUser`, or raw private code/IL.

**Strict boundaries:** the output explicitly reports `same_world_saved_or_reopened_proven=false`, `derived_RGD_runtime_value_initialized_proven=false`, `Android_Unity_IL2CPP_phone_executed=false`, and `original_game_payload_published=false`. No original game Save method executed or RGD file read/written. These observations narrow authentic source provenance only; they cannot close LOCAL-005.

Source-only code: `android-port/Experiments/T4/OriginalRgdInitContext/Program.cs`, `scripts/t4_validate_original_rgd_init_context.py`, `tests/test_t4_validate_original_rgd_init_context.py`, `.github/workflows/raft-t4-original-rgd-init-context.yml`. Workflow path-isolated, no heavy Unity or private artifact. T4 scheduled JSONL overflow hint task separately active. T5 native [CI42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) was in progress in the Unity Editor import at this cycle's preflight, so T4 did not dispatch or cancel any game build.

**Next meaningful step:** inspect the authenticated zero-argument original method's bounded call dependencies and early-return/null checks, then instrument it only on the Android source adaptation path if evidence shows a missing diagnostic. Separately, accept real `LOCAL-005` only after owner demonstrates offline playable world → genuine user-generated `.rgd` durable save → complete exit and same-world playable reopen in a new signed APK/OBB/XAPK. **LOCAL-005 OPEN, NOT_READY 0/3.**
