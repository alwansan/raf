# GT — Chat-10: مستقل بعد إيقاف الفريق، استعادة ZIP2، وتحضير بناء كامل

- session_id: GT-20261112-CHAT-10-INDEPENDENT-RESTORE
- origin: chat; assigned agent: GT
- repository: alwansan/raf; writable only feature/android-native-port
- owner directly stopped all T1–T5, granted GT permission to merge over their changes and trigger builds without waiting. Keep attributions/source safeguards.
- ZIP2 only: 15964ea8f246b6e076ce26b60931ee2e1a9a2385; manifest SHA256/size for split; no Git LFS, no zip2/main writing.

## Actual completed proof

[43153126679 PASS](https://github.com/alwansan/raf/actions/runs/43153126679): complete isolated 134 original ZIP2 files restored to AssetRipper; 9/9 true original Texture2DArray PNG importer layouts repaired, 0 GUID/PNG tampering; exact 28/28 Class187 original Material pointers; UnityPy independently decoded all eight pixel-bearing original BC3 arrays with source SHA-authenticated streamed bytes and Pillow compared 8/8 correct slice-major; ninth two-layer array original source is zero pixels, not fabricated. Full 82-owner original Material export parity 10,216 slots; 4,151 internal exact texture bindings; 416 external identities still unresolved. No Unity Editor/Adreno verified in this isolated test.

## Production native bug and corrected code

[43153893985 FAILED](https://github.com/alwansan/raf/actions/runs/43153893985): authenticated original 134 graphics files and 82 original owners; successfully passed GT native nine-array importer/28 Material refs, B04/B11. Then `restore_builtin_shaders` fell back to strict `verify_builtin_export_ownership.verify`; the underlying `verify_export_lineage.check` rejected extra private Texture classes (28/84/89/117/187) with `Unexpected trace class`, introduced by correct opt-in trace needed for array source identity. This is NOT proof that source shader file is missing. Fixed [57ce47df](https://github.com/alwansan/raf/commit/57ce47df7765e03d07a5ec70a7f91821a81091a8) with explicit allowlisted type handling, structural checks, material/shader strict invariants and negative tests. W1 source-only negative-test job first gate passed at run [43155762766](https://github.com/alwansan/raf/actions/runs/43155762766); full same-instance real run pending. Owner-authorized full APK/OBB/XAPK build relaunched by [request f89b58e](https://github.com/alwansan/raf/commit/f89b58e52ac6093bf1fdf907d9e86d5a60be8796), run [43155854860](https://github.com/alwansan/raf/actions/runs/43155854860).

## Additional actual restoration fidelity work

- New `scripts/gt_external_original_texture_links.py` authenticates each original owner external FileIdentifier table with SHA, joins m_FileID>0 to source Texture class identity, and compares same-export pointer/UV without rewriting materials or leaking data. Implemented [462b23f](https://github.com/alwansan/raf/commit/462b23f78250af8bbe94b5e1a248c6aeb38fad67), synthetic [43154841456 PASS](https://github.com/alwansan/raf/actions/runs/43154841456), real isolated [43154972647](https://github.com/alwansan/raf/actions/runs/43154972647) running.
- New `--all-original-layer-cells` in `scripts/gt_compare_original_bc3_to_flipbook_pixels.py` verifies every authentic pixel-bearing BC3 layer's entire top mip against actual AssetRipper PNG (50 source layers) rather than 24 sampled cells; preserves explicit no-full-mip-chain/GPU claim. [84b57bbb](https://github.com/alwansan/raf/commit/84b57bbb1609914c67c9887d8a33bada2aefe282), synthetic [43155325923 PASS](https://github.com/alwansan/raf/actions/runs/43155325923), real [43155325887](https://github.com/alwansan/raf/actions/runs/43155325887) queued.

## Follow-up and boundaries

Check newest real CI and GT reports, especially 43155854860 for next real native blocker, 43154972647 external 416 references, 43155325887 all 50 layers. Continue directly with true shader program restoration of remaining ~770 Dummy Material-backed shaders and proper renderer/GLSL/Adreno render proof. T1–T5 are stopped: do not block on their permission. Do not claim completed XAPK or original 11 mip chain/Adreno pixels until concrete run and device evidence. Never download Git LFS or modify ZIP2 source originals.
