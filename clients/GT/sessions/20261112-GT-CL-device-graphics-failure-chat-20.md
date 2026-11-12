# GT — Chat-20 / real CL Android graphics-failure reproduction (12 Nov 2026)

- Identity: GT. Write only `feature/android-native-port`.
- Source original: `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`; Git LFS forbidden.
- Owner authorized independent work; T1–T5 stopped.
- Parent continuation: Chat-19 signed Native100 recovery, current full build 43247161671.

## New direct device evidence (not pixel acceptance)

Read the owner's `alwansan/CL` pinned commit `cffd3f7be2d0c47649da9b28eae17c36d031f0e8` at
`raft log/lf/LogRaft-20261112-183147-926/session-summary.json`. LogRaft 0.6.89,
package `com.alwansan.raft.androidtest`, versionCode 1089, 67 telemetry samples, 25
readable presented-FPS samples, 1,180,876 game log lines. Locally failed write batches: zero.

- 42,229 invalid UltimateWater Shader passes: 19,191 Spectrum, 23,038 Foam/Global.
- 7,263 invalid compute kernel index 6 root lines; numeric index **does not alone prove FFT water origin**.
- 4,668 repeated RGBA32 cursor warnings.
- 2 OBB GUID load failures; 1 missing MonoScript event.
- GPU busy mean 68.71%, max 99.49% (system KGSL busy, not per-object GPU).
- Screenshots dated 2026-11-12 (18:35, 18:41, 18:44) show a mostly white raft despite selected coloured items; one HUD frame reports FPS 0.29. These are user-device screenshots, not an original material binding proof.
- Collector reports a world-loaded message but zero game-death events in the observed session. Does not prove gameplay fully functional.

## Implemented / verified this cycle

- `scripts/gt_device_graphics_acceptance.py` read-only safe aggregate gate for LogRaft session-summary, fails strict mode for any observed invalid water pass/kernel, OBB GUID error or local lost batches. Cursor and missing MonoScript retained as warnings; zero observed counts **never** means all pixels restored.
- `tests/test_gt_device_graphics_acceptance.py` covers source-free negative controls, malformed inputs, source structure, counts, and real collector nested exit-info field shape.
- `.github/workflows/raft-gt-device-graphics-acceptance.yml` pins exact CL commit, reads *only* its session-summary JSON, verifies expected known-failing counters. Does not checkout CL raw logs or fetch LFS/assets.
- Original first CI [43262929604](https://github.com/alwansan/raf/actions/runs/43262929604) failed because reader expected counters at top-level; original LogRaft stores final counters under stop-time exit-info. Fixed this with exact no-disagreement alternative access.
- Follow-up real CI [43263151186](https://github.com/alwansan/raf/actions/runs/43263151186) **SUCCESS** for 8 tests and expected failing device snapshot.
- Final test-expanded real CI [43263197989](https://github.com/alwansan/raf/actions/runs/43263197989) **SUCCESS**; this success means regression reproduced, not that the game's rendering passed.
- Aggregate evidence `clients/GT/evidence/20261112_cl_device_graphics_failure_receipt.json`.
- All original game binary data/GUID/source ZIP2 untouched; no Git LFS.
- These changes do not alter the running full Unity build at snapshot `5b3ddd67`.

## Source-vs-phone separation

The source-authentic texture graph gate remains 9 original arrays / 28 array refs /
416 cross-owner references / 50 original BC3 top-mip layer pixel comparisons.
The 770 postvendor custom Material documents referencing Dummy ShaderLab are **not restored**.
The original private Shader48 compiler APK with approximate samplers is a diagnostic,
not original Material binding, and user Adreno pixel equivalence remains unverified.
Device failures independently confirm gameplay is **not visually accepted**.

## Next engineering action

1. Inspect [full 43247161671](https://github.com/alwansan/raf/actions/runs/43247161671); do not duplicate while active. If failed, fix first concrete blocker and rerun once.
2. Target high-impact `UltimateWater/Spectrum/Water Spectrum` and `UltimateWater/Foam/Global`: match original typed Shader48 pass index and original GUID, same-instance export Material bindings, real Unity 2021 Android Vulkan Shader import and pass count. Do not fabricate or bypass a missing pass.
3. Trace kernel index 6 to original compute identity using original source/private callsite provenance, not Logcat index alone.
4. Trace original Cursor.SetCursor callsite to the exact Texture2D import format, repair RGBA32 at verified identity without changing unrelated textures.
5. Review predominant white Materials by original renderer/material/shader graph (NOT texture count alone), restore source-faithful shader families in tested batches, compare device colours and performance to photos, and rerun strict LogRaft gate.
6. Update `state.json`, `MEMORY.md`, `SUMMARY_AR.md`, and session after each batch; do not claim original water/shaders complete before phone proof.

## Reproduction

```bash
python3 -m unittest discover -s tests -p test_gt_device_graphics_acceptance.py -v
python3 -m scripts.gt_device_graphics_acceptance --session-summary session-summary.json --strict
# exit 2 is the expected verdict for the owner's Nov 12 failing session
```
