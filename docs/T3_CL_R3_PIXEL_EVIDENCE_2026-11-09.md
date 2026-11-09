# T3 / RENDER-002 — verified pixel distribution in six real CL R3 captures (2026-11-09)

## Provenance and independent experiment
- Worker: **T3**, session `20261109T0142Z-T3-chat-cl-raw-png-ci-p8r4`, origin `chat`.
- Initial branch SHA: `6fe95344909bd919dc8bc08cc245bda640e1155e`; independent isolated workflow source commit: `e839d4e3e54b761a95a421f48e1ce70593751725`.
- Successful [Actions run 42547145230](https://github.com/alwansan/raf/actions/runs/42547145230) (2026-11-09 01:44–01:45 UTC), workflow `.github/workflows/raft-t3-cl-r3-png-evidence.yml`.
- Original **CL read-only** source commit `24a677fc8fa4749c0bcf8a3cac01fa80b1641c86`, path `test/shared-20261108-232759-468049775`; tested the **actual uploaded PNG bytes** in a hosted GitHub runner, not screenshots recreated from source.
- Verified six exact git blob SHA-1 identities and their lengths against GitHub's public metadata *before* executing the audit; PNG decoder then validated CRC/scanline structure and calculated spatial pixel statistics.
- Source-free regression `python3 -m unittest discover -s tests -p test_t3_cl_png_pixel_audit.py -v` **PASS**. The audit is the independent CI consumer of the T3 scheduled tool; the chat run **did not modify** `scripts/t3_cl_png_pixel_audit.py` or `tests/test_t3_cl_png_pixel_audit.py`.
- Artifact `13644076425` contains **aggregate JSON only**, no raw captures; 7-day retention: [result artifact](https://github.com/alwansan/raf/actions/runs/42547145230/artifacts/13644076425).

## Real PNG measurements
All six were **1080 × 2400** RGBA/RGB-decodable PNGs. `black_fraction` is the fraction of RGB pixels where all channels are <= 8. `center` is x in [W/4,3W/4) and y in [H/4,3H/4). Results are **pixels in stored image**, not semantic shader assertions.

| Test | PNG blob SHA-1 (Git object) | Bytes | Center RGB values | Center black fraction | Full black fraction |
|---|---|---:|---:|---:|---:|
| T3-01 | `4bed7a13b85667d1f51cd63acb4a08e75004053c` | 119360 | 3 | 0.000000 | 0.000162 |
| T3-02 | `114c2bc63ad1bd7d3a31684adeee64b593b8ea43` | 210904 | 81448 | 0.000043 | 0.000062 |
| T3-03 | `c5509b375762f7af7e3a83664a512816710444af` | 162232 | 332 | 0.000043 | 0.000062 |
| T3-04 | `715dfa8796ea9579a32ddfbdb55622f9f09001d0` | 149557 | 332 | 0.000043 | 0.000062 |
| T3-05 | `72ecc44a111e21c8889dd827da49896b085c979a` | 154489 | 331 | 0.000043 | 0.000062 |
| T3-06 | `796dc3198e15d34b99815936de69aedacb135728` | 158584 | 330 | 0.000043 | 0.000062 |

**Result:** The prior *fully black GLES capture region* symptom is not present in the middle of any of the six authenticated **R3** saved PNGs. T3-01 has three distinct colors there, consistent with a synthetic solid-bar scenario; T3-02 has high RGB diversity, consistent with a gradient. These are measured spatial statistics, **not** exact per-pixel assertions against the user's on-screen Android screenshot. The reported low black fractions by themselves do not verify alpha compositing, sRGB transfer, visual correctness of each case, or genuine Raft scenes.

## Key distinctions and limits
1. CL session reported Android15, unified mini **0.2.13-shared** with `verified_surface_pixels=true`, `gl_error=0x0` for T3-01..06. Such events are **EVIDENCE_READY**, **not device/human PASS**.
2. The old shared mini **0.2.10** had misleading black `PixelCopy(Window)` PNG regions despite colorful actual GPU tests. T5 later repaired SurfaceView PixelCopy. **This audit provides real stored-pixel evidence for R3**, a stronger check than source compilation or PNG presence; it does not establish that every future screenshot will be valid.
3. All observed colors belong to synthetic OpenGL ES lab tests; **no genuine Raft Unity scene/shader/material/particle rendering was exercised** by this CI. The original game's white hand/raft, missing water/fire effects and square smoke remain **RENDER-002 OPEN**, **NOT_READY (0/3)**.
4. The T3 real original/export scoped proof (41 Materials/227 TexEnv/150 RGBA color slots) continues to rule out those specific identity, UV and color-export losses, not shader variants/Unity import/texture sources/GPU pixels.
5. **Next separate substantive question:** use authenticated original ZIP2/Unity shader and prefab references to trace the specific smoke particle material + shader pass + texture/alpha and compare with actual in-game screenshot. Do not issue duplicate mini APK or alter shared activity during other workers' work.

## Reproduction
Run isolated `.github/workflows/raft-t3-cl-r3-png-evidence.yml` on the same source commit. Its download step pins **both** CL commit and six Git blob SHA-1 values. The workflow executes T3's scheduled Python tests and runs `scripts/t3_cl_png_pixel_audit.py` on each exact byte-verified CL image. Raw PNGs are read only in the ephemeral runner; the public artifact contains the aggregate JSON statistics. Any changed CL bytes are rejected rather than silently substituted.
