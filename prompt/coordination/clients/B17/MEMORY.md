# B17 — engineering memory

Session: `20261104T2140Z-B17-spc2` (joined 2026-11-04 UTC). Work: `B17-20261104T2140Z-B17-spc2-spectrum-descriptors`; issue WATER-001 (P0); status active.

## Live sources and evidence
- Read `AGENTS.md`, `docs/CURRENT_OWNER_REQUIREMENTS.md`, `prompt/README.md`, `prompt/CONTINUE_RAFT_AR.md`, `prompt/STATUS.md`, B_TEAM PROMPT_AR/README/OPERATING_MODEL/SOURCES/SUMMARY/REVIEW/TEMPLATES/RESTORE, and ZIP2 source provider.
- Branch live reference prior to registration: `5a977b3812cc597aaa790ae66bce54e85a965fc8` (recheck HEAD at every write). Only `feature/android-native-port` writable; CL read-only.
- Last released game: [APK86 / release 41812889049](https://github.com/alwansan/raf/releases/tag/android-early-test-41812889049-1); underlying source d181ee7152580f49ee0b41dfd05fa2bfdacfafe5. This predates B-team source fixes. LogRaft releases are not game builds.
- Live CL HEAD `5394407b5cd0a0ca1848ff0902f8d2133bf6ea29`; reviewed 4 Nov [B-team device evidence](../../B_TEAM/REVIEW_2026-11-04.md) and live screenshot filename inventory: pale materials and failed world load; counts 40327 invalid water passes and 5555 invalid compute kernels in final session summary (not independent samples). No new device testing.
- Active recent Actions: local startup and preflight for other B agents; do not cancel/duplicate. Existing original Spectrum pass/CB table is [W2 diagnostic](../../../scripts/probe_w2_water_shader_stage_bindings.py) (reference path from repository root is scripts/probe_w2_water_shader_stage_bindings.py); B24 handles Foam, B45 Blur, B08/B48 FFT program ambiguity, B49 pass structural gate.

## Separate engineering hypothesis
Original Spectrum Shader (serialized Shader object in `sharedassets0.assets`) contains original texture/sampler descriptor bindings per pass/stage that must be captured independently from W2's already proved pass/CB topology. Losing descriptor slot/type identities during Android reconstruction can produce wrong or white water and invalid passes. This is a *hypothesis*, not a cause demonstrated on phone. Do not infer runtime kernel IDs or publish private source/program bytes.

## Plan / constraints
1. Reuse SHA-pinned ZIP2 source `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, original owner 115978112 bytes SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`. Inspect existing Spectrum object stage schema before choosing parsing assertions; fail closed.
2. Implement bounded read-only Spectrum per-pass fragment/vertex texture/sampler binding table extractor and synthetic rejected-shape controls; source-only implementation contains no original bytes or names.
3. Run a discrete scoped, non-native no-LFS CI experiment with source provenance and aggregate safe counts; record true result, hypothesis rejections and limitations. Integrate verified table into future shader translation/validation only when original source evidence supports it.
4. Preserve audio/Settings, defer touch; no fake completion flags, no unauthorized Unity/APK request, no protected-branch write.

Current last checkpoint: joined; **no experiment result, no committed source fix, no native/device evidence**. Next: inspect serialized binding schema and write the bounded probe/tests.
