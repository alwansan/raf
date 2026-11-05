# T4 LOCAL-005 — exact original ILSpy reference-context A/B/C proof (2026-11-05)

## Finding
Original ILSpy outputs for `Raft_Network` were **context dependent** even though the exact `Assembly-CSharp.dll` bytes, ILSpy version and syntax level were fixed. The older B07 production class/body SHA pair reappears when its 151 managed siblings are present; the T4 read-only alternative pair reappears when the same binary is isolated. This explains the prior apparent conflicting authenticated SHA findings and identifies the missing original assembly-reference context as the supported cause. **The experiment also changes the directory path together with sibling presence**, so it does not identify a particular assembly or completely exclude path-related behavior.

## Source and test boundaries
- Original source pin: `alwansan/raf@15964ea8f246b6e076ce26b60931ee2e1a9a2385`, `Raft/Raft_Data/Managed/Assembly-CSharp.dll`, 3,211,776B SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`.
- Companion reference context: **151 DLL files** from read-only pinned feature commit `02e9fba7fb42b83579595885391be636ee3b56e8`, `Raft/Raft_Data/Managed`. The original ZIP2 DLL, not a modified or reconstructed one, was explicitly **copied into each of three independent private input directories**, then its original 3,211,776B and SHA256 verified in all three. LFS and Unity were not used.
- Tool: `ilspycmd` version **11.2.0.10050**, `-p -lv CSharp9_0`, same .NET 10 GitHub-hosted ubuntu-24.04 job.
- Inputs: `solo-a` and `solo-b` each contain *only* the exact DLL (two independent isolated controls). `with-refs` contains the *same* DLL and 151 exact pinned companion names/files. Three independent whole-project source decompilations wrote only to temporary private runner directories. No raw original C#, DLLs or decompiler logs were published.

## Verified result
[Actions CI42011353849](https://github.com/alwansan/raf/actions/runs/42011353849) **COMPLETED SUCCESS** on source [57d24bc](https://github.com/alwansan/raf/commit/57d24bc676e3d99edc81e1454302b90c3b12b34c):
- `10/10` source-free negative/positive tests passed.
- Exact original DLL size/SHA verified **three times** and 151 sibling assemblies staged privately.
- Isolated controls agreed class SHA `d16c36336a6aec4e23781c135820692a233130a3f1c1d9ab9052d432d76eedef`, coroutine body SHA `2bf76a189a69d23444c5ede9f00a5444a48f819c64d87ec298ebeedbf5d9088c` — exact T4 alternate pair from [41944365772](https://github.com/alwansan/raf/actions/runs/41944365772).
- With companion DLLs, class SHA `080035c137e446828226ed84a23190656b6f235d274436cafb477feaf93caa03`, coroutine body SHA `cbd74c24f1c6a86dd50e8d320f4f4142f5b3f3fc5bf8f64ded04710c30c3a140` — **exact** independently B07-pinned pair from [41929041686](https://github.com/alwansan/raf/actions/runs/41929041686).
- Masked executable body SHA changed as well; this was not just comment or string whitespace variation. The exact difference in decompiled code semantics is **not published or yet characterized**.
- `scripts/t4_probe_ilspy_reference_context.py` + `tests/test_t4_probe_ilspy_reference_context.py` refuse unknown pairs, absent scene broadcast, duplicate ready assignments, unrecognized return type, changed isolated control and incomplete input. All output is SHA/count metadata only.

## Integration implications
The production local-world adapter `scripts/adapt_android_offline_startup.py` and `config/runtime-operation-traces.json` rightly retain the original **B07 SHA pin**; T4 did not change them or add alternate wildcard acceptance. A future private original-source stage must supply authenticated companion managed assembly reference context, or explicitly fail closed when the isolated decompile produces a different source hash. Removing or relaxing the source-pin gate would be the **wrong remediation**. Prior [offline real adapted managed CI41942118067](https://github.com/alwansan/raf/actions/runs/41942118067) already **PASSED** on the marker commit `ea98fb0`: 14 actual original adapted C# sources prepared, local RPC harness tested, original managed compile `exit=0`. The current A/B/C original-context experiment does **not** compile Unity or verify actual phone behavior.

Remaining limitations: no signed native game after APK86 (source `d181ee7...`), no phone proof of `WorldHasBeenLoaded.originalCompletionAssigned`, playable offline world, persistent .rgd create-save-close-reopen, or GPU/FFT. `LOCAL-005` remains **OPEN** and project **NOT_READY, 0/3** independent full reviews. T4 FileManager separate source investigation and T1/T2/T3/T5 runs must remain attributed and unaffected. Sound and Settings owner-confirmed working; touch/layout deferred.

## Reproduction
One isolated workflow [`.github/workflows/raft-t4-ilspy-reference-context.yml`](../.github/workflows/raft-t4-ilspy-reference-context.yml) pins both original and companion provider SHAs, checks size/SHA and available runner disk, and never uploads original private payload. The public script returns bounded original class/body comparisons only. The same-run three-way result is enough to establish a meaningful missing context; it is not a general ILSpy theorem or license to modify original C#.
