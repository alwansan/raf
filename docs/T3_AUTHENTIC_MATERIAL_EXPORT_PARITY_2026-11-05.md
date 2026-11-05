# T3 — actual original-to-export Material texture/UV and color fidelity (2026-11-05)

## Exact input and evidence boundary
T3 identity: `20261104T2354Z-T3-render-harness`, issue `RENDER-002` OPEN; writable branch `feature/android-native-port`.
Original source: immutable ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. Selected Material owner `Raft_Data/sharedassets6.assets`, **6,607,272 bytes**, SHA256 `0476792cfeffac19d16e920011ed8d2fb2da62973c2f09a8689bc59e1ac4b632`. The bounded reproducible pipeline stages nine source providers, each size/SHA-verified, and uses pinned public AssetRipperCLI source `nowl-it/AssetRipperCLI@036098ab525a3f9f693dc101edeb21faad4d32d8`, W1 Material21/Shader48 + B02 Texture2D28 lineage instrumentation (through B21's SHA-checked source composer). Only traces from **one** exporter invocation with the same random `export_instance` can be compared; raw original data, GUID/pathID/material names, and private traces remain on the temporary runner. Public artifact contains **only aggregate numerical evidence**. No LFS, Android game build, GPU run, or .meta/GUID edits.

## Proven selected source-to-real-export results

| Property | Genuine same-export observed |
| --- | --- |
| Material identities selected and compared | **41/41** |
| Texture property slots, source vs actual exported YAML | **227/227** |
| Authenticated internal Texture2D pointer identity matches | **89/89**, zero incorrect or untraced |
| Original external-owner Texture bindings | **25** — unresolved by this bounded source graph, NOT claimed preserved |
| Legitimate original null Texture slots | **113** |
| Texture slots newly null, newly bound, dropped or invented | **0** |
| Source/export UV scales and offsets compared | **227/227**, zero drifts |
| Original/export Material color/tint (m_Colors) slots | **150**, zero missing/extra/changed RGBA values |
| Materials with original nonidentity RGBA values | **40** out of 41 |
| Android shader execution, full project pixels, GPU/FFT success | **NOT TESTED** |

**[Texture/UV actual source/export CI 41939404454](https://github.com/alwansan/raf/actions/runs/41939404454) — SUCCESS** on commit `4bd56a47c4836f84ecd02093bd9c5eafdc7c4c1a`. Original 41/227, 89 internal target exact, 25 external unproven; zero wrong, missing, UV drift. Exported YAML `m_TexEnvs` is dictionary-form, unlike original serialized typetree array; fixed the *verification parser*, **not** the graphics asset, in [B05 production verifier commit 77d312f5](https://github.com/alwansan/raf/commit/77d312f546f1fc80c72f57a57de5d90699d66302), with strict negative controls [2f1807bd](https://github.com/alwansan/raf/commit/2f1807bd0f5d47065d307f6d773409e017da6916).

**[Color RGBA actual source/export CI 41940350604](https://github.com/alwansan/raf/actions/runs/41940350604) — SUCCESS** using separate fresh SHA-authenticated private export and existing B44 original m_Colors comparator extended to the same 41-material source scope. 41 source/export material identity matches, 150 color slots, 40 original materials nonidentity; zero color drift, missing/extra slots. Original `m_Colors` typetree stays strict, exported YAML mapping supported. Relevant commits: [B44 verified-source/YAML parser 33ae0f76](https://github.com/alwansan/raf/commit/33ae0f760ea9f82a792b04419de1ba7df34d6e5), [preflight fix 64a780b4](https://github.com/alwansan/raf/commit/64a780b44677426603d5ebc6f0659bd88f217891). T3 helper `scripts/t3_same_export_material_colors.py` and tests in `tests/test_t3_same_export_material_colors.py`; isolated workflow `.github/workflows/raft-t3-real-material-colors-export.yml`.

## Recorded rejected hypotheses and failures
- Original source-only census is not a substitute for same-export Material/Texture/UV fidelity: B05/B03 prior owner work was source-only and remains credited.
- Runs [41938229887](https://github.com/alwansan/raf/actions/runs/41938229887), [41938711186](https://github.com/alwansan/raf/actions/runs/41938711186), [41939065539](https://github.com/alwansan/raf/actions/runs/41939065539) failed on **B05 verifier exported YAML parser** (eventually safely classified `texenv_wrong_container`). The subsequent same-source fourth run passed after a dictionary-only exported YAML adjustment; original source stays array-only.
- [Color first CI 41940116028](https://github.com/alwansan/raf/actions/runs/41940116028) failed in synthetic fake test fixture before acquiring original source: literal escaped newlines and optional `UnityPy` import before allowlist rejection. Corrected in B44 tests `8264b10a`, B05 tests `ef5dfae9` and production pin validation `64a780b4`; rerun with real original data `41940350604` succeeded.
- **Rejected within this exact bounded set:** 41 original materials lost or altered their internal Texture pointers, UV scale/offset or m_Colors values in this actual AssetRipper export. This does NOT establish their runtime shader behavior, nonselected Material parity, or every external texture pointer.
- Original B12 renderer diagnostics synthetic C# fixture repaired separately, [CI 41937719270](https://github.com/alwansan/raf/actions/runs/41937719270), after earlier 41933025319 failed because newer production ComputeShader/Resources/Encoding read-only snapshot was absent in tests. No game runtime change.

## Next engineering blocker and acceptance
Investigate **original Shader→Material linkage, pass/subprogram/keyword fidelity, sRGB/importer and 25 cross-owner texture pointers**, working with T1/T2 shader/water and T5 graphics resource tracks without repeated source-only scans. Once original export comparison identifies a defect, patch only exact actual project/export loss with GUID/.meta preserved. Build/test on Poco Adreno using current runtime diagnostics (material shader unsupported/zero pass/InternalErrorShader counts, missing mesh filters) and visual screenshots; only device evidence can show color restoration. Preserve offline world, .rgd saves, audio and Settings; deferred touch/layout untouched. Issue remains `RENDER-002 OPEN`; no APK built by T3. The latest delivered owner-tested game APK is still APK86, not these source checkpoints.
