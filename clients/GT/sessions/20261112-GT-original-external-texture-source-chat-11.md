# GT — Chat-11: authentic external material texture source and font lineage

- session_id: GT-20261112-CHAT-11-EXTERNAL-TEXTURE-FONT-CLASSIFICATION
- origin: chat; identity GT; exclusive writable branch feature/android-native-port
- owner authorization: all T1–T5 stopped; GT can integrate and build independently
- ZIP2 source SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385; manifest SHA256/size; no Git LFS

## Real failure, not hidden

[43154972647](https://github.com/alwansan/raf/actions/runs/43154972647) has workflow conclusion SUCCESS because optional other checks pass. Exact job log shows `GT source-authenticate external Material Texture PPtrs` step failed in `scripts/gt_external_original_texture_links.py` with `original_exported_material_identity_missing`. The six synthetic tests passed, but source parser misclassified authentic font-bundled source Materials as ordinary exported loose YAML. **Do not count any of 416 original cross-owner external targets as newly accepted from this run.** Follow B05's `FONT_COLLECTION` classification, do not alter original scenes or substitute Texture2D identities.

## Fixes integrated

- [4d4ea214](https://github.com/alwansan/raf/commit/4d4ea2144f7a583cf548f331f1262982f4f351db): strict FontAssetExportCollection fingerprint/trace validation, no normal YAML expectation for authenticated imported font material; Unity built-in material redirect remains distinct; ordinary missing Material YAML still fails; duplicate source trace and malformed font source fail closed. Added negative tests, [43156702219 PASS](https://github.com/alwansan/raf/actions/runs/43156702219) synthetic.
- [6faee64e](https://github.com/alwansan/raf/commit/6faee64ea00e955e77e4462891982e83794c7d06): real external checker catches bounded errors and always writes safe aggregate `status=INCONCLUSIVE` receipt with allowlisted reason and phase; no private GUID/file ID/filename/trace copied into artifacts or logs. New synthetic [43156857328 PASS](https://github.com/alwansan/raf/actions/runs/43156857328). Full isolate [43156857287](https://github.com/alwansan/raf/actions/runs/43156857287) triggered, queued at this checkpoint.
- [84b57bbb](https://github.com/alwansan/raf/commit/84b57bbb1609914c67c9887d8a33bada2aefe282): full 50 source populated BC3 layer top-mip comparison against actual source-authentic AssetRipper PNG, synthetic [43155325923 PASS](https://github.com/alwansan/raf/actions/runs/43155325923), real isolate [43155325887](https://github.com/alwansan/raf/actions/runs/43155325887) in progress, not yet accepted.

## Native build independent

New owner-authorized full Android [43155854860](https://github.com/alwansan/raf/actions/runs/43155854860) in progress from f89b58e with mixed Shader/Texture private trace fix 57ce47df; earlier [43153893985](https://github.com/alwansan/raf/actions/runs/43153893985) passed nine array source and 28 refs but failed at builtin shader ownership because added texture trace rows were not allowlisted. Shader checker regression W1 real [43155762766 PASS](https://github.com/alwansan/raf/actions/runs/43155762766). **No XAPK/Unity Editor/Adreno GPU confirmed.** Watch next native fail gate and fix, do not fabricate shader data or bypass strict water authenticity.

## Resume

Inspect precise job step of new 43156857287, not only workflow conclusion; compare aggregate external links count against previous 416 unproven and distinguish original excluded font materials. Inspect source BC3 full 50 probe 43155325887 and full native 43155854860. Then update summary/state/RESTORE_AR with proven numbers and code fix. ZIP2-only and no modifications of source assets, .meta, GUID or other branches.
