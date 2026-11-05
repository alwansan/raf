# T4 LOCAL-005 — original world producer / user derived-RGD initializer context (5 Nov 2026)

This experiment inspects only exact original compiled CIL with immutable ZIP2 `Assembly-CSharp.dll` 3,211,776B SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`. It does NOT execute game source, load original .rgd, publish proprietary class/member identifiers, rebuild Unity or prove Android correctness.

Prior authenticated [CI42062124798](https://github.com/alwansan/raf/actions/runs/42062124798) SUCCESS 36/36: `SaveWorld`'s derived-RGD local has exactly one lexical store directly preceded by a call returning a derived-RGD type; `SaveUser` has a derived-RGD field declared by `SaveAndLoad` with exactly three original direct store sites. This proves neither the value's identity nor executed control flow.

New independent experiment: classify the direct call's owner as SaveAndLoad / another original compiled type / external-unresolved, its invocation kind and arity and whether the specific callee has a compiled original method body. Partition the three direct SaveAndLoad-owned SaveUser field store sites by containing method categories and by immediately preceding instruction's data type (null literal, derived-RGD typed, or unknown). No private IL, source, type or method names, bytecode, binaries, RGD content, saved world/player fields or log paths in public report. These are static lexical classifications only. No source changes to actual gameplay or serializer.

Source-free negative controls and an isolated, path-scoped `.github/workflows/raft-t4-original-rgd-init-context.yml` check report schema, impossible counts, false game/device claims, exact original SHA, and altered-source rejection. Other T4 scheduled JSONL overflow check remains separate. T5 native build #42058825739 continues its own Unity import; T4 does not interfere.

## CI result

Pending matched original-source CI. On success, record categories only; retain `LOCAL-005 OPEN`, `NOT_READY 0/3`, and actual user acceptance: playable offline world, genuine world .rgd durable save, full process quit, same world reopen.
