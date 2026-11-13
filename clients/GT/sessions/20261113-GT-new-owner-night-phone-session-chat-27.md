# GT Chat-27 — new CL phone screenshots + LogRaft graphics failure, and native release permission

**Date:** 2026-11-13 (Asia/Baghdad). Owner write branch `feature/android-native-port`; original resource source `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385` is read-only. No Git LFS or original GUID/.meta alterations.

## New phone experiment — confirmed source and scope

- CL commit [a320d5e](https://github.com/alwansan/CL/commit/a320d5e23962568b62bffec95399cf3e0cb1f579) (2026-11-12 22:52 UTC) added 4 screenshots at `raft log/img/Screenshot_٢٠٢٦-١١-١٢-٢٣-٥٥/٥٦/٥٧...` and session `raft log/lf/LogRaft-20261112-235351-196/session-summary.json` (blob f37371aa232bfd5220b2d0604fcf25c2117de549). The corresponding private source trace is a game running on Vulkan/Adreno 730; collector LogRaft 0.6.89.
- Final source totals: **36,828 invalid UltimateWater passes** (Spectrum 15,054 + Foam Global 21,774), **6,106 invalid compute kernel index6** (index number **does not establish FFT resource identity**), **2,844 cursor RGBA32**, **2 OBB GUID loads**, **1 missing Mono script**, **1 duplicate EventSystem**, **4 convex mesh polygon limit**. LogRaft observed 1,022,470 game-log lines. Zero reported game-process death events; one `World has been loaded` observation, not proof of stable gameplay.
- Collector: 4 raw log segments, 103,361,406 bytes reported, 3,390 batches received and written, 0 failed, 0 pending; local Logcat OS ring loss remains unknowable. 21 readable SurfaceFlinger FPS estimate samples of 78 telemetry samples, mean ~30.91 displayed FPS (not Unity internal FPS). This is a **failing graphics gate** despite game/world load.
- Four screenshots inspected: Raft main-menu scene almost entirely white, radio retains color; in game dark smooth blue sea and white hand while some tool/UI textures render; bright cyan underwater scene with shark, and white menu/raft with conspicuous grey noise-textured patch. Visual evidence is not a per-Material or Shader identity proof.
- Sanitized source receipt: [`../evidence/20261113_cl_night_device_graphics_and_build_receipt.json`](../evidence/20261113_cl_night_device_graphics_and_build_receipt.json); no screenshots, raw logs, or source object identifiers committed to GT evidence.

## Real native build + release failure

- [Full native 43299084397](https://github.com/alwansan/raf/actions/runs/43299084397) on **older head `2666622cbc93a4fde0dae22371cd3b157dc15ab7`**: `reconstruct=success`; `publish-early-test=failure` at `gh release create` due **HTTP 403 Resource not accessible by integration**. `publish-early-test` already requests `contents:write` and tries optional `RAFT_RELEASE_TOKEN` secret with GITHUB_TOKEN fallback, so a code-only permission flag is not demonstrated sufficient. Keep fail-red release acceptance; do not claim release was published.
- Signed checkpoint Artifact **13997201215**, full transport/delivery Artifact **13996908213**, both expire around **2026-11-16**. This build does not include all newer Chat25–26 Spectrum source-only work; it does not fix phone water pixels.

## Engineering performed and validation

- `scripts/gt_device_graphics_acceptance.py` checks optional final LogRaft writer counters (received, written, failed and pending) against final sink tally, blocking false-green device gates for unaccounted or pending batches. Earlier summaries without these fields retain the prior explicit sink-counter semantics.
- `tests/test_gt_device_graphics_acceptance.py` adds source-count-only reproduction of the new session and negative controls for malformed writer receipts.
- `.github/workflows/raft-gt-device-graphics-acceptance.yml` now pins BOTH earlier known-bad CL session `cffd3f7` and new `a320d5e` snapshot for real, safe, immutable CI regression. Check the **actual post-commit run result** before marking it verified; file edits alone are not CI proof.

## Next concrete priorities

1. Inspect the real CI for the new snapshot gate and correct any fixture/source mismatch without weakening source identity.
2. Recover the exact original consuming typed IL of the one Spectrum `Shader.Find` Shader local from Chat26. Trace dynamic Material/Graphics/Renderer/RT use and original CB0/Sampler binding before Native game mutation. The static 82-owner/1556-Material sweep found **zero** direct Spectrum PPtrs, so never invent a GUID.
3. Determine real `kernel6` compute owner, repair Spectrum/Foam pass count and program binding, then restore high-impact **770 post-vendor dummy shader Material documents** by source-backed families. Check new device pixels after a truly newer packaged run.
4. GitHub Release HTTP403 requires owner/administrator to enable Actions release permission or a valid fine-grained `RAFT_RELEASE_TOKEN` with repository Contents write. A signed Artifacts delivery is available; it is not a public Release.
5. Update `RESTORE_AR.md`, `state.json`, `SUMMARY_AR.md`, `MEMORY.md`, `RESTORATION_PLAN_AR.md` and machine plan with evidence, and preserve source/export/Unity/package/phone distinctions.
