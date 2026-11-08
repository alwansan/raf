# T2 — source-original Foam Pass1 value producer + owner Android GLS synthetic evidence
session_id: 20261108T1956Z-T2-chat-pass1-source-kind-4d6a
origin: chat
branch: feature/android-native-port
base_sha: 41bda606b7f7c7fc0b397e7e5d07dd66807ea707
resumed_from: clients/T2/sessions/20261108T1925Z-T2-chat-original-blit-cecil-v2.md
experiment_key: T2-FOAM-PASS1-CIL-SOURCE-HEAD-20261108
resource_key: WATER-001
status: COMPLETED_AUTHENTIC_STATIC_SOURCE_TYPE_AND_DEVICE_SYNTHETIC_PASS; BLOCKED_ON_ORIGINAL_RETURN_CFG_AND_TEXTURE_IDENTITY
scope: SHA-original original managed CIL trace on pinned zip2 + independent owner CL/test synthetic GPU evidence; no private game assets/IL in repository or artifact

## Live CI and original SHA evidence
- Source C# scanner `android-port/Experiments/T2/FoamBlitOriginalProducers/Program.cs` original SHA DLL and Foam name private. Source has bounded CIL reverse stack def-use for Blit source (max 96 opcodes / 32 stack depth, branch/EH fail closed, no source byte export), static classifications cannot prove instance identity. Synthetic Cecil selftest: handles literal pass + material/destination typed field, void call consuming parameters, return typed Texture, negative branch and non-Texture stack value. SHA-original real call source checked.
- [CI42517639783](https://github.com/alwansan/raf/actions/runs/42517639783): PASS bounded source head opcode family; Pass1 preceding call returns other than direct Texture/RT.
- [CI42517790825](https://github.com/alwansan/raf/actions/runs/42517790825): PASS original source-adjacent call returns `System.Void`, cannot produce Blit source value.
- [CI42518080217](https://github.com/alwansan/raf/actions/runs/42518080217): PASS backwards 21 steps with one void call to original Pass1 producer `Texture typed_call_result`; Pass0 source `RenderTexture typed_field` in 6 steps.
- [CI42518334396](https://github.com/alwansan/raf/actions/runs/42518334396): PASS 17/17 Python anti-spoof original-source safe-report tests, synthetic Cecil, authentic ZIP2 SHA stages and 2-case safe finite report JSON; atomic C#/Python/tests commit `897a3dc134afaad62e4195c2e032c89eedad86a9`. Bounded source in JSON **type Texture** with `pass1_source=unknown` retained in the narrower direct-adjacent typed gate by design.
- [CI42518579252](https://github.com/alwansan/raf/actions/runs/42518579252): PASS initial callvirt conservative check. [CI42518726576](https://github.com/alwansan/raf/actions/runs/42518726576): PASS original managed method resolved and body present; not assured single straight-line execution. [CI42519122764](https://github.com/alwansan/raf/actions/runs/42519122764): PASS 17/17 Python + Cecil selftest + original SHA; fixed redacted category `original_method_branch_flow` (branch/throw/conditional in conservative classifier). No arbitrary private method names or IL print.

## Real owner Android15 evidence discovered
- Read-only `alwansan/CL` main commit `f401b7ffe3b6ead9038f3b35273599dcf8286e68`. Unique user shared session `test/shared-20261108-230157-466487336`; summary pack SHA `6e19b05c697334be6ee7740846f2817f29fdcb185a118c8f5d36bbd06b04066f`, `app_source=93e32950c521d9890ce845eb8213cd6704cd7f98`, APK vCode10 identity matches T5 owner-requested Arabic Portrait unified Mini [CI42517104924](https://github.com/alwansan/raf/actions/runs/42517104924).
- 4 T2 case rows all `PASS` in one summary and 4 separate real GL per-case JSONLs with matching `gl_observed/shared_auto_result`. Adreno730 OpenGLES3.2/API35. T2-02 upgraded 2-region FBO source left [32,96,159,255] right [223,32,64,255], final baseline and contrast identical RGBA, tolerance ±2. T2-03 negative GL FBO returned 0x8cd7, T2-04 invalid GLSL rejected. Older separate T2 v0.1.0 phone CASE02 was single-color; use shared r2 proof for dual-region.
- Device report `docs/T2_GLES_DEVICE_EVIDENCE_2026-11-08.md`, commit `66df177a51f8e0ffb27788b9b393ebf4be1097da`. T2-only r3 shared Mini vote NO_BUILD `0d56972beb0729d6182d8a36a20ea61382d8b595`.
- **Boundary:** real phone PASS proves *synthetic GLES3 FBO and negative controls* only; does NOT prove original Raft water shader, FFT compute, crosspass RT identity, CB0 samplers/upload, Unity2021 shader binding or water pixel parity. WATER-001 OPEN / full game NOT_READY. Do not request Mini/XAPK duplicate.

## Next executable step
Private SHA-original Cecil CFG of the resolved Pass1 `Texture` method return: enumerate branch/throw successors with bounded basic-block effects, receiver types and return join, fail unknown on unresolved phi/alias; only then compare pass0 target and pass1 source actual RenderTexture *instance* lineage. No private IL/method names/field identifiers/asset bytes published, no pixel success inferred from type. Coordinate real Unity shader integration after original CB0 and sample bindings are proven.

## Output
Session: `clients/T2/sessions/20261108T1956Z-T2-chat-pass1-source-kind-4d6a.md`
Reports: `docs/T2_FOAM_SHA_ORIGINAL_BLIT_PRODUCER_2026-11-08.md`, `docs/T2_GLES_DEVICE_EVIDENCE_2026-11-08.md`.
