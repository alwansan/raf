# GT — imported PNG top-mip V8 candidate | 27 نوفمبر 2026

Starting HEAD adbfe7c2d50bbf81b3c765d509abe1fe20e5121c matched; V7 prior 45954999518 and 45954999455 success. No local checkout/diff. Added strict opt-in source oracle and route comparison; same authenticated source owner/explicit pinned flat stream, independently decode RGBA32 bottom-up to top-left, strict PNG RGBA8/TextureImporter identity, no lower-mip or native sampler promotion. V7 default preserved. Candidate only, no CI yet.

Next: Add actual public exporter PNG mode and independent unit/actual controls, run focused CI. A3 blocked until verified authorized original source; G0–G6 open; no unauthorized original data/LFS, phone or XAPK. CL/lab read-only, BLACK excluded, animation deferred; only feature/android-native-port; no force push.

Candidate adds C# second authored mode using public TextureAssetExporter.TryCreateCollection, SpriteInformationObject and file-backed provider, native mode unchanged. Separate gt_authored_imported_png_route_witness.py checks actual imported PNG and generated meta, independent T3 authored checks and 13 expected negative controls. 34 candidate regression tests; do not claim pass until actual CI.

CI [45957439789](https://github.com/alwansan/raf/actions/runs/45957439789) job 140367073873 head 0912ba8f6b541271b5dfb8f794327117c344e3ca; Python regression step success, guard 45957440880 success, native and imported PNG actual export pending. Previous 10004-byte V7 archive SHA/CRC verified again. No actual V8 PASS claim yet.
