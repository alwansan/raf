# T4 LOCAL-005 — original ILSpy same-run repeatability, 2026-11-05

This **source-intake** experiment follows [T4 original completion marker](T4_WORLD_COMPLETION_TRACE_2026-11-05.md) and does **not** change the game, source digest pins, kernel/readiness flags or local-world behavior. Its purpose is to constrain the cause of two distinct authenticated `Raft_Network` ILSpy textual source hashes previously observed for the **same exact original binary**.

## Inputs and independent source provenance
- Immutable original ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.
- Original `Raft/Raft_Data/Managed/Assembly-CSharp.dll`, exactly **3,211,776 bytes**, SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`.
- `ilspycmd` NuGet tool pinned to version `11.2.0.10050`, full `-p -lv CSharp9_0` export, executed **twice** to **two separate private directories** inside one Ubuntu24.04 GitHub-hosted CI run; no original private source or decompiler log uploaded.
- Prior authentic B07 [CI41929041686](https://github.com/alwansan/raf/actions/runs/41929041686) class SHA `080035c137e446828226ed84a23190656b6f235d274436cafb477feaf93caa03`, coroutine-body SHA `cbd74c24f1c6a86dd50e8d320f4f4142f5b3f3fc5bf8f64ded04710c30c3a140`.
- Prior and current authenticated T4 class SHA `d16c36336a6aec4e23781c135820692a233130a3f1c1d9ab9052d432d76eedef`, coroutine body `2bf76a189a69d23444c5ede9f00a5444a48f819c64d87ec298ebeedbf5d9088c`. The difference in decompiled text is real at the SHA level; why it occurs between CI histories remains **unknown**.

## Implemented verification
[`scripts/t4_compare_private_ilspy_runs.py`](../scripts/t4_compare_private_ilspy_runs.py) reads only authenticated, private decompiled `Raft_Network` C# and emits class/body SHA and masked-executable body SHA plus bounded structural counts. Duplicate/missing files, wrong return type, missing original broadcast or genuine completion write, or class/body pair outside the two independently already observed pairs fail closed. The checker does not alter the SHA gate used by `adapt_android_offline_startup.py`. Ten source-free negative/positive unit tests in [`tests/test_t4_compare_private_ilspy_runs.py`](../tests/test_t4_compare_private_ilspy_runs.py) guard differences from comments, same-length string literals, actual executable differences, invalid hashes, duplicate files and false callsite decoys. A masking fixture initially compared different-length literals, then was corrected without weakening any source gate.

The existing isolated [T4 completion workflow](../.github/workflows/raft-t4-world-completion-trace.yml) now checks two genuine private exports **after** the original DLL SHA gate, 10/10 old marker controls, 10/10 new repeatability controls and the two CLR ready/not-ready semantic executions.

## Observed result
[Final CI41944365772](https://github.com/alwansan/raf/actions/runs/41944365772) **COMPLETED SUCCESS**:
- T4 marker controls **10/10**, new repeatability controls **10/10** and genuine .NET10 synthetic conditional coroutine `falseCompletion=0 trueCompletion=1 yieldsPreserved=true`.
- Both independently executed private full-project ILSpy exports of the **identical** SHA-verified original DLL yielded `Raft_Network` class digest `d16c36336a6aec4e23781c135820692a233130a3f1c1d9ab9052d432d76eedef`, body digest `2bf76a189a69d23444c5ede9f00a5444a48f819c64d87ec298ebeedbf5d9088c` and masked executable body digest `a0dcff37dc0aea1b76335f89e328decf446e12c01928646fea45d149c442c755`, **all equal** between the two same-run passes.
- Each class body has 1 genuine original completion assignment, 1 actual scene broadcast call and 3 actual `yield return` tokens. No source/binary published.
- The original T4 method observation was read-only, `production_adapter_exercised=false`. No actual production native Unity/IL2CPP build, Android phone or .rgd save/reopen proof.

[Initial CI41944283588](https://github.com/alwansan/raf/actions/runs/41944283588) FAILED before original extraction: synthetic comment-vs-literal negative control accidentally compared different-length strings. The production masking contract retains source positions by masking *every original character*, thus the fixture was invalid. Corrected to same-length decoy, final 20/20 control pass.

## What is and is not established
Within one current Actions runner, repeated same-DLL / same-ILSpy full-export outputs are **repeatable** for the inspected class/method. This narrows the problem: the B07-to-T4 cross-run difference was **not reproduced as nondeterminism between these two extractions on the same runner**. It does **not** establish why B07 obtained a different source body, whether another runner image/runtime version or input context contributed, or which body a future Unity native source-stage pipeline will generate. The runtime production SHA gates should remain untouched until exact source selection and build staging are independently verified by T5. Do not substitute SHA authenticity for semantic correctness, and do not use a decompiler text SHA to conclude Android host/readiness/.rgd functionality.

`LOCAL-005` remains **OPEN; NOT_READY; full immutable reviews 0/3**. In next real signed Android candidate, look for B07 original `WorldHasBeenLoaded.firstMoveNext`, T4 original completion marker, callbacks and real save/load file persistence. Working audio/Settings preserved and touch/layout deferred. No Actions cancelled.
