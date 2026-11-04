# B45 — 20261104T2056Z-B45-f0c1

## Scope
WATER-001: authentic original two-pass UltimateWater Subsurface Blur restoration. Original ZIP2 pinned source 15964ea8f246b6e076ce26b60931ee2e1a9a2385; feature/android-native-port only. Preserve audio/Settings/LEFT Mouse0; no touch work, native request or full APK.

## Live source and evidence
Read B_TEAM/PROMPT_AR.md, README.md, OPERATING_MODEL_AR.md, SOURCES_AND_ACTIONS_AR.md, REVIEW_2026-11-04.md, TEMPLATES.md, SUMMARY.md, AGENTS.md, CURRENT_OWNER_REQUIREMENTS.md, prompt README/CONTINUE/STATUS and ZIP2_SOURCE_PROVIDER. Baseline HEAD f835f66c67fba9cf36fdbc9f49793b7b8f06b12a at first read; later concurrent B50 commits require refresh before mutation. Latest game APK86: https://github.com/alwansan/raf/actions/runs/41812889049 ; CL source 5394407b5cd0a0ca1848ff0902f8d2133bf6ea29 and 4 Nov screenshots, session-summary/segment3 reviewed through team review. Original W5 run 41821419074 at 7764fd7: both Blur passes (three seeds each) positive within tolerance, negative controls true; then ValueError, after raster phase, without private candidate or Unity import. B50 independently handles LOCAL-005 Steam source, so no shared modifications.

## Hypothesis
The W5 failure is after original stage recovery / per-pass numeric raster, likely original ShaderLab state or other wrapper serializer unsupported shape. Error phase not isolated. First isolate without releasing shader/source, then implement only a proven original state serialization repair with synthetic controls. No claim of authentic Android pixels.

## Test/limits
Known W5 tool stage checks do not imply Unity/adreno/device acceptance. Must maintain original SHA256 and original pass/state, property identities and meta/GUID. Workflow needs unique B45 group, timeout and safe aggregate output only.

## Next
Record B45 work/experiment and run bounded preflight, repair exact classification and check CI; sync state/issue/events/SUMMARY at checkpoint.

## Checkpoint — original Blur fixed and source-only private staging verified (2026-11-04T21:18:00Z)
- Rejected hypothesis that original DXBC translation or pass render state caused the post-raster failure. Original Shader m_Props contains precisely one Texture (type=4; flags=0; attributes=[]; property SHA a8ee7ea1663c61c62b3cf6bd99b303f0f62434223cf285462dfc599c97bdc59c). The old A12 wrapper incorrectly required Props {}.
- Implemented original property serializer (`scripts/b45_blur_properties.py`) and preserved original texture name/description/default/type (no dummy), integrated with `scripts/a12_build_original_blur_wrapper.py`. Synthetic A12 + B45 tests pass. Genuine original data SHA/object confirmed by CI [41913062003](https://github.com/alwansan/raf/actions/runs/41913062003).
- Exact original 2-pass ShaderLab SHA256 `5886dc362fc1a4a237aa05f6b4244ec30af4daad4089edea008f95d760945e14`, 23,068 bytes, privately generated from ZIP2 pinned. W5 [41913273839](https://github.com/alwansan/raf/actions/runs/41913273839) PASS: 6 original-vs-recovered CPU Vulkan positives (three per pass), max pixel color/depth abs 0, coverage 0, 12 mutation controls true, no validation errors. No original program or shader released.
- Added `scripts/b45_stage_original_blur.py` and `scripts/b45_install_original_blur.py`: private exact-SHA stage + outside-project preserved backup, byte-for-byte exported .meta GUID check, unique original ShaderLab identity, symlink-safe atomic replacement. [41914193733](https://github.com/alwansan/raf/actions/runs/41914193733) PASS 9 synthetic rollback/stage tests. [41914205988](https://github.com/alwansan/raf/actions/runs/41914205988) PASS private SHA-pinned stage from genuine original with all CPU Vulkan guards.
- Added strictly additive install step to explicitly gated native workflow, commit [348990da](https://github.com/alwansan/raf/commit/348990da5c7864bfbbc39e2f4fbe3e4969795d81). NO full native build/request was initiated by B45, existing WATER/FFT gates remain. Source recovery is verified; **actual exported target GUID and Unity compiler/Adreno still not tested**, so WATER-001 OPEN and NOT_READY.
- Original user APK86 source/test run: [41812889049](https://github.com/alwansan/raf/actions/runs/41812889049); no APK made/phone run by B45. B50/B07 separately handle LOCAL-005; no shared source edits. Audio/Settings untouched; touch deferred.
- Next: owner-requested native build only after coordination; inspect shader export identity and Unity compile results, add targeted source-authenticated material binding/sampler upload proof. Do not repeat W5 passed CPU comparison without a new failure or hypothesis. Adjacent FFT/other water kernels remain open.
