# B45 — Real original two-pass Subsurface Blur ShaderLab recovery

Date: 2026-11-04 UTC. Scope: **WATER-001 original shader recovery**, source fidelity, only `feature/android-native-port`. **Not Unity/Android device acceptance.** Preserve owner-confirmed Audio and Settings, touch/layout deferred.

## Origin, failure and differential

- SHA-pinned read-only ZIP2 source commit: `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; 14 original Shader-bearing owner files, SHA-checked, 165 original Shader objects. Private original Blur object SHA `c9341848367eaedb12e551ce9061b1eea728f54f2069ef1a3c12c4a4a2e9bb52`; parsed SHA `865e5529986469f18fd3158612f925647599e8b5126187be0c87d490ff6d2aa3`.
- Earlier original W5 [41821419074](https://github.com/alwansan/raf/actions/runs/41821419074) recovered real DXBC programs and passed the two-pass pixel/raster guards but failed with `ValueError` after raster, before generating a ShaderLab candidate.
- B45 source diagnosis [41912390029](https://github.com/alwansan/raf/actions/runs/41912390029) reproduced the failure without outputting private names or code: authentic original Blur has **one serialized Texture property**, `m_Type=4`, zero flags and attributes, four numeric defaults plus `m_DefTexture`. The old A12 wrapper rejected all non-empty `m_Props` despite both real-pass render states serializing. Original property definition commitment `a8ee7ea1663c61c62b3cf6bd99b303f0f62434223cf285462dfc599c97bdc59c`. No hypothesized missing passes or fabricated texture defaults.
- Fix: narrow strict original-property serializer `scripts/b45_blur_properties.py`, used by `scripts/a12_build_original_blur_wrapper.py`. It emits original serialized texture identifier, description, dimension and default verbatim; it rejects unknown property types, attributes, flags, missing/defaulted entries, unsafe/unbounded identifiers, unrecognized texture defaults, nonzero floating defaults and schema mutations. Synthetic A12 + B45 tests and authenticated source shape PASS [41913062003](https://github.com/alwansan/raf/actions/runs/41913062003).

## Verified original graphics result

[GitHub Actions 41913273839](https://github.com/alwansan/raf/actions/runs/41913273839) completed from authentic ZIP2 source:

- Original pass count **2**, original vertex+fragment programs translated and rebound; generated a private complete ShaderLab candidate of **23,068 bytes**, SHA-256 `5886dc362fc1a4a237aa05f6b4244ec30af4daad4089edea008f95d760945e14`.
- CPU software Vulkan raster: **3 positive comparison seeds per pass (6 total)**, `max_color_abs=0`, `max_depth_abs=0`, coverage mismatch `0` and no validation warnings/errors.
- **12 negative mutation checks** (6 per pass) were detected; one independent color/depth canary passed. No statement about Unity/Adreno render equivalence.
- Candidate and original DXBC/HLSL/stage bytes stayed runner-private. Only sanitized aggregate JSON, counts and hashes were published. No original exported `.meta`, GUID or game source modified by this isolated test.

## Safe native integration plumbing (not a proven native import)

- `scripts/b45_stage_original_blur.py` re-verifies the original two-pass Vulkan raster and the **independent fixed candidate SHA/byte commitment** before creating a candidate *only in the private CI scratch directory*. Isolated authentic [41914205988](https://github.com/alwansan/raf/actions/runs/41914205988) **SUCCESS**, no candidate artifact or publication.
- `scripts/b45_install_original_blur.py` refuses SHA mismatch, a missing/duplicated exported target, a malformed or changing shader `.meta` GUID, symlinks, in-project backups and overwrites; it saves original exported shader and `.meta` outside project, replaces atomically and rolls back on failure. Isolated synthetic [41914193733](https://github.com/alwansan/raf/actions/runs/41914193733) **9 PASS** tests covering rollback, uniqueness, SHA and source isolation.
- Strictly additive step wired to the **already explicitly gated** workflow `.github/workflows/raft-unity-editor-android-import.yml` at commit [348990da](https://github.com/alwansan/raf/commit/348990da5c7864bfbbc39e2f4fbe3e4969795d81), near W1 Depth Copy export restoration. It is **not independently triggered** by source updates and does not bypass the existing water/FFT authenticity or documented owner build gates. Only aggregate JSON may be retained in artifact `raft-b45-original-blur-native-staging-<sha>`; never include private `.shader` or backups.
- Unity editor compile/import, actual exported original target existence/uniqueness/GUID, texture/sampler uniform uploads, real Material links, Adreno colors and owner playability are **unverified**. Original shaders other than Blur and FFT/compute kernel issues remain open. Do not claim water pass/kernels complete or game ready; WATER-001 remains **OPEN**.

## Follow-on

On the next *separately owner-requested* native experimental build, check `raft-b45-original-blur-native-staging-<sha>` for both source and install aggregate, verify original exported Shader identity and `.meta` unchanged, then require Unity shader import report and phone comparison. If native installation fails, retain original backup and record failure phase; do not swap in a dummy or disable water-contract gates. Investigate sampler state/uniform delivery separately from pixel-equivalence proof. Latest phone build reviewed: APK86 [41812889049](https://github.com/alwansan/raf/actions/runs/41812889049), not changed by this source session. B50/B07 own local-world/save sources; this B45 work does not touch them.

[Worker state](../prompt/coordination/clients/B45/state.json) · [Worker memory](../prompt/coordination/clients/B45/MEMORY.md) · [Resource record](../prompt/coordination/B_TEAM/resources/B45-blur-original-property.json) · [Water issue](../prompt/coordination/B_TEAM/issues/WATER-001.json).
