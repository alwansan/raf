# B04 — original Linear color-space parity in transient Unity export (2026-11-04)

## Scope and sources
Independent RENDER-002 contribution. The source-authenticated original
`Raft_Data/globalgamemanagers` file has **1,914,356 bytes** and SHA-256
`6d1288cd08b91d8c321ed2526503404b64b978819985b9b7fa5a9a146c29a8f5`.
Previous W2 typed probe [documents](W2_COLOR_SPACE_SETTINGS_2026-11-03.md)
`PlayerSettings.m_ActiveColorSpace = 1` (Linear), `m_ColorGamuts = [0]`,
and engine 2021.3.45f2. This B04 change independently verifies the
size/SHA and executes W2's typed reader. The separate original ZIP2 provider
is pinned at `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.

Original Android screenshots and CL logs reviewed in
[B_TEAM review](../prompt/coordination/B_TEAM/REVIEW_2026-11-04.md)
show pale/white surfaces; this does NOT prove color-space misconfiguration.
Other RENDER-002 lanes already cover original material values (B44),
texture links (B46), and sRGB importer provenance (B02).
This scope concerns only global project color-space parity.

## Engineering result
- New `scripts/b04_restore_original_color_settings.py` verifies the pinned
  original owner before trusting its PlayerSettings fields; rejects size/SHA,
  Unity version, color space and gamut mismatches.
- In the transient Unity exported `ProjectSettings/ProjectSettings.asset`,
  demands exactly one PlayerSettings YAML document and exactly one scalar
  `m_ActiveColorSpace` in valid `0/1` format. Detects ambiguous/malformed
  inputs and symlink/hardlink, and refuses non-UTF8, excessive or binary input.
- If Gamma is observed, changes ONLY the scalar digit `0` to `1` by
  atomic staged replace with source-change check. If already Linear, no
  write occurs. Dry-run returns status 2 on mismatch.
- This does not touch original assets, exported `.meta` or GUIDs,
  materials, shader code, textures, runtime Settings UI, FMOD or touch.
- Native pipeline integration in
  `.github/workflows/raft-unity-editor-android-import.yml` checks and
  conditionally restores exact color space immediately after AssetRipper
  export. A second read-only guard verifies parity in the copied
  `unity-candidate` before Unity Editor import.

## Reproduction, proof and limits
- 9/9 synthetic tests passed in isolated CI (no local run claimed); exercised a one-byte edit,
  idempotence, no-write preview, malformed/duplicate YAML, CRLF/UTF-8,
  symlink/hardlink and size/SHA/enum fail-closed controls.
- Isolated actual-original-source CI
  [41913026554](https://github.com/alwansan/raf/actions/runs/41913026554)
  **SUCCESS** from
  [7536e2a](https://github.com/alwansan/raf/commit/7536e2afb58bafc938f0cc0381a8d60e1e2c142e);
  it authenticated the original owner, ran the typed W2 reader, restored
  a synthetic exported Gamma project, verified exact Linear parity and
  a preserved unrelated setting.
- Source implementation
  [cce0abd](https://github.com/alwansan/raf/commit/cce0abdac052dd694338f36fad87aa2412d51067);
  native-stage integration
  [e52c07c](https://github.com/alwansan/raf/commit/e52c07c808d6bf7a2eeb90ebcb4b48f71ea98f23).
- **Not established:** whether latest actual exported
  `ProjectSettings.asset` was Gamma, whether the real native pipeline
  reaches this new guard and how the device colors change. No Unity
  compilation, GPU pixels or new APK were produced by B04. The current
  device evidence is APK86 from run41812889049, older than this patch.
  Original `m_ColorGamuts` is authenticated but not edited in the exported
  project because its YAML representation has not been verified.
- **Do not claim RENDER-002 resolved**. WATER-001 programs, per-texture
  sRGB import parity, Material Shader paths and device screenshot comparison
  remain independent acceptance items. Readiness NOT_READY, 0/3.

## Next evidence
On a next *owner-coordinated* native pipeline run, capture only aggregate
`RAFT_B04_SOURCE_COLOR_SPACE` lines (pre/post) and the real exported
setting. Verify that the step ran and the exact source SHA was accepted;
if no change was required, reject the hypothesis that export globally
defaulted to Gamma. Then compare same-scene images from the new signed
APK to versionCode86 and independently inspect water/material regressions.
Do not duplicate an identical full build for this guard alone.
