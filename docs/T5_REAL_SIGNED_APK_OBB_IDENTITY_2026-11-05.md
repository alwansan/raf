# T5 — actual signed APK/OBB identity on immutable native run 42058825739

## Source and decision

Native source `e9c358eda01785b65e4eb14f18723da426635628`, actual native [run 42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) versionCode **89**, created signed APK, original OBB and XAPK and an audited delivery artifact. The owner's Poco F5 Pro world/save/relaunch report applies to that actual artifact, but CL summaries still show 1 and 2 OBB GUID warnings on separate 2026-11-05 sessions. These warnings do not by themselves prove OBB corruption or package mismatch. Original Release creation failed HTTP403 while package build succeeded.

T5 retained the fully byte-verified native delivery in [run42110297871](https://github.com/alwansan/raf/actions/runs/42110297871), artifact `13454900880`, expires 2026-11-08 21:12:40 UTC. Previous checks authenticated original full ZIP SHA256 and **all 7 real transport parts plus 3 assembled logical APK/OBB/XAPK digests**, but did not independently run `aapt` or `apksigner` on the real APK/OBB pair.

## Added integration evidence path

New `scripts/t5_extract_actual_signed_pair.py` reads original ZIP only after checking full archive size/SHA, checks every planned APK/OBB transport part name, size, package and version, and writes only two actual completed signed files to an exclusively created private staging directory. It streams and hashes selected parts and whole files, verifies ZIP CRC during reads, refuses unsafe/archive-part paths or pre-existing output and cleans interrupted staging on ordinary errors. The script does not extract game payload entries or publicize their data.

New `tests/test_t5_extract_actual_signed_pair.py` uses 17 source-free positive/negative fixtures (wrong original ZIP SHA/size, OBB part loss/mutation, package/version drift, wrong hashes, traversal/duplicate ZIP entry, symlink and no-clobber). Existing `scripts/t5_verify_apk_obb_pair.py` and its 17 controls are reused rather than copied.

One-shot isolated `.github/workflows/raft-t5-real-apk-obb-identity.yml` pins the source run, retained archive IDs, original/nested ZIP bytes and hashes. It checks available disk before a second 6GB download, then checks outer and inner ZIP SHA256, materializes only original APK+OBB in private CI staging and runs Android Build Tools `aapt dump badging` and `apksigner verify --verbose` on the actual APK. The existing pair verifier checks both completed file hashes, package/versionCode, OBB file name and ZIP structure. This is a **source/packaging identity experiment only**, not Unity or phone execution. Original game bytes and signing materials are never uploaded as artifacts or printed to logs.

- One-shot [CI42117471172](https://github.com/alwansan/raf/actions/runs/42117471172) is the testing gate; its exact result must be read before treating any APK signing/version or OBB ZIP claim as established.
- Immutable original ZIP: 5,948,243,524B, SHA256 `29d967c5f1868a10aa0f8f3b9f0306e828c1d32ef3cda2909f7482b5d111eef6`.
- Retained Actions artifact outer ZIP: 5,948,243,834B, SHA256 `41bf01f9991521fac876c591b75adc19b493ad47882687846e5aae1c2af6a3ef`.

## Boundaries

Passing APK signing and file pairing does not by itself prove correct Unity GUID references *inside* OBB, Android 15 OBB mount permissions, screen rendering, FFT, graphics, audio, gameplay, frame performance or durable relaunch (the owner's earlier observation remains a separate limited device result). It also cannot fix GitHub Release HTTP403 or replace effective maintainer permissions. A real paired-file hash result helps distinguish local mismatched transport from internal Unity resource mapping.

This cycle did not change `AndroidTouchUiPanel.cs`, T5's concurrently scheduled Resolution code, W1/T1 water, T2 Foam, T3 ShaderLab/ColorMask or T4 mouse. No native Unity/APK rebuild, LFS, or new Release published. INTEGRATION-001/WATER-001/RENDER-002 remain open and NOT_READY 0/3.

Session: `prompt/coordination/clients/T5/sessions/20261105T2153Z-T5-chat-signed-pair-4e91.md`.
