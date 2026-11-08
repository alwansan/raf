# T2 — real Adreno 730 shared Mini GLES evidence, 8 Nov 2026

**Worker:** T2 / `origin=chat` / session `20261108T1956Z-T2-chat-pass1-source-kind-4d6a` · **Scope:** T2-01..04 synthetic GPU device acceptance ONLY, not original Raft water, ShaderLab or Unity.

## Immutable source and build identities

- Owner-provided GitHub `alwansan/CL`, branch main, examined at commit **`f401b7ffe3b6ead9038f3b35273599dcf8286e68`**; exact session directory `test/shared-20261108-230157-466487336/`.
- Summary `summary-20261108-230157-466487336.json`, session `20261108-230157-466487336`, `app_source=93e32950c521d9890ce845eb8213cd6704cd7f98` (T5 Arabic portrait r2 source parent), `pack_id=raft-shared-t1-t5-v1`, pack SHA256 **`6e19b05c697334be6ee7740846f2817f29fdcb185a118c8f5d36bbd06b04066f`**, same as embedded shared pack and build request.
- `T5-01` observed from same summary: `package=com.alwansan.raft.lab.shared version=0.2.10-shared versionCode=10`, Android API **35**, abi arm64-v8a. The actual r2 shared Mini APK build [CI42517104924](https://github.com/alwansan/raf/actions/runs/42517104924) SUCCESS, SHA256 **`0f469cc650182370b570d96c8e92e3f9c686f6b4417ae10e22d3c35b0084fd42`** in ZIP Artifact `13631588625`; summary's source+version+pack match this build. **A device APK file's own SHA was not obtained from owner phone**, and package identity alone does not prove binary hash.
- T2 per-case exported MediaStore JSONL files present separately; their `startup` says `api=35 model=23013PC75G abi=arm64-v8a`, `gl_context` reports `Qualcomm Adreno (TM) 730`, `OpenGL ES 3.2 V@0615.95`. These files' `gl_observed` exactly match `shared_auto_result` and the four summary `observed` strings.

## Owner's actual T2 device results (no synthetic CI substitution)

| Shared case | Real device result and concrete observation | Data |
|---|---|---|
| `T2-01` | **PASS** GLES vendor/renderer Adreno 730, ES3.2, maxTexture=**16384** | `t2-gles-20261108-230235-466525434.jsonl` |
| `T2-02` | **PASS** 8×8 RGBA8 two-pass spatial FBO: sourceLeft **[32,96,159,255]** and sourceRight **[223,32,64,255]**; finalBaseline **[32,96,159,255]** and finalContrast **[223,32,64,255]**; tolerance ±2. Two distinct spatial regions survived source and sampled destination readbacks; not a flat constant single-pixel proxy. | `t2-gles-20261108-230235-466525675.jsonl` |
| `T2-03` | **PASS** GL driver returned `0x8cd7` for unattached/incomplete FBO (expected negative) | `t2-gles-20261108-230235-466525949.jsonl` |
| `T2-04` | **PASS** deliberately invalid fragment GLSL rejected by compiler (expected negative) | `t2-gles-20261108-230236-466526243.jsonl` |

All four `case_id` rows are `PASS` in **the one shared summary**, and all four corresponding GL JSONL contain `case_start`, `gl_observed`, `shared_auto_result`, matching the summary. Older standalone T2 phone `test/t2-gles-pass-20261108-191036-452606737/` also passed an **older flat-color FBO CASE02** but does *not* establish the new spatial contrast; rely on the shared r2 case for spatial proof.

## Acceptance boundary and impact

**Confirmed on owned Android device:** this synthetic two-pass GLES3 FBO spatial pixel roundtrip and two negative controls work on Adreno 730. Therefore a claim that *all* GLES3 FBOs on this phone are categorically unsupported is falsified by direct phone evidence. This **does not** prove performance or correctness of real Ultimate Water original shaders, `Graphics.Blit` material binding, CB0/samplers/texture-format equivalence, Unity2021 compute FFT, or water pixels in the full Raft Android game.

Separate authentic original-water CIL evidence [CI42518334396](https://github.com/alwansan/raf/actions/runs/42518334396) 17/17 source checks and [CI42518726576](https://github.com/alwansan/raf/actions/runs/42518726576) confirms Pass1 static `Texture` producer through 21-instruction stack trace (one void call); original callee still has complex control flow. Original crosspass **actual RenderTexture instance identity UNVERIFIED**. WATER-001 remains OPEN and full game NOT_READY. T2 vote on shared Mini r3 remains **NO_BUILD**: tested r2 driver already exists, no new T2 compiled driver delta. No XAPK requested.

**Source links:** [Owner shared session](https://github.com/alwansan/CL/tree/f401b7ffe3b6ead9038f3b35273599dcf8286e68/test/shared-20261108-230157-466487336), [summary](https://github.com/alwansan/CL/blob/f401b7ffe3b6ead9038f3b35273599dcf8286e68/test/shared-20261108-230157-466487336/summary-20261108-230157-466487336.json).
