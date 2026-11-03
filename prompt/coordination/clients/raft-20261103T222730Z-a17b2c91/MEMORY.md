# A1 ZIP2 original FFT source migration

Identity raft-20261103T222730Z-a17b2c91; session a1-20261103T222730Z-cf5e711a; previous raft-20261103T145000Z-a1c92f74; registered 2026-11-03T22:29:03.060Z at HEAD f604848e7efdc146de64ec2b8569bc35ad9e2689.

User uploaded original game to zip2 without LFS; validated upstream root manifest and pinned read-only SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385.

The 115978112 byte sharedassets0.assets is split across three Git blobs of 47185920,47185920,21606272 bytes; its manifest SHA256 exactly equals existing A1 original FFT source pin.

Goal: migrate *only* existing isolated A1 authenticated software-Vulkan FFT workflow from LFS hydration to sparse blobless ZIP2 checkout and SHA-verified atomic assembly into runner temp; use same existing numerical probe and negative controls.

Other agents already updated common owner docs, so no repeated broad inventory. zip2 and protected branches READ ONLY; feature/android-native-port ONLY writable. No native Unity/APK or new automations. WATER-001/RENDER-002/FFT-FORMAT-009 OPEN, NOT_READY 0/3.

## Verified final ZIP2 FFT source migration — 2026-11-03T22:35:56.722Z

- **Code:** scoped original chunk reassembler [eac1f62](https://github.com/alwansan/raf/commit/eac1f62caf7960357568535bbd91a84ca338a9a3); [10 negative/positive unit fixtures c1ff199](https://github.com/alwansan/raf/commit/c1ff199162eff751b94fc6eac2fae272123dc805); [workflow 14ba21e](https://github.com/alwansan/raf/commit/14ba21e93af3dac3623265a9230afeccea6986ce). Only A1 provider changed from LFS hydration to read-only ZIP2 partial sparse Git fetch, no full game clone, all source temporary.
- **Exact source:** ZIP2 pin 15964ea8f246b6e076ce26b60931ee2e1a9a2385, three chunks 47185920+47185920+21606272 bytes. Original FFT owner sharedassets0.assets 115978112 bytes SHA256 0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3. Original ComputeShader pathID2456 SHA256 9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247.
- **[Actions 41731607739](https://github.com/alwansan/raf/actions/runs/41731607739) completed SUCCESS** on same source14ba21e, job126250116759 synthetic (10/10 ZIP2 negative/positive +8/8 existing schema and actual positive+negative Vulkan canary), job126250329499 original (ZIP2 no-LFS SHA verified before import; authentic20 FFT program variants ×3 seeded/dispatch cases =60/60 matching real written output, maxAbs0, relativeL2=0, 0 inconclusive; 10+8 tests green). Never upload original proprietary shader/data or pixels.
- Real conclusion: ZIP2 **works as authenticated no-LFS provider for this A1 experiment**, not an empty Git LFS repo, nor entire 7.79GB reverified, nor proof of original Unity kernel matching or RGHalf/ARGBHalf formats, water rendering, Adreno or APK.
- Peer coordination record [final discussion](https://github.com/alwansan/raf/blob/feature/android-native-port/prompt/coordination/discussions/WATER-001/20261103T223500Z-raft-20261103T222730Z-a17b2c91-zip2-success.md); [technical report](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/A1_ZIP2_ORIGINAL_FFT_NO_LFS_2026-11-04.md); experiment JSON recorded. All protected branches/CL/tasks/native requests/assets/input unchanged. Scoped A1 source-provider work completed; state **paused**. WATER-001/FFT-FORMAT-009/RENDER-002 OPEN, overall NOT_READY 0/3.
