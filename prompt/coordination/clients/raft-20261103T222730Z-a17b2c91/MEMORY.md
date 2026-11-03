# A1 ZIP2 original FFT source migration

Identity raft-20261103T222730Z-a17b2c91; session a1-20261103T222730Z-cf5e711a; previous raft-20261103T145000Z-a1c92f74; registered 2026-11-03T22:29:03.060Z at HEAD f604848e7efdc146de64ec2b8569bc35ad9e2689.

User uploaded original game to zip2 without LFS; validated upstream root manifest and pinned read-only SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385.

The 115978112 byte sharedassets0.assets is split across three Git blobs of 47185920,47185920,21606272 bytes; its manifest SHA256 exactly equals existing A1 original FFT source pin.

Goal: migrate *only* existing isolated A1 authenticated software-Vulkan FFT workflow from LFS hydration to sparse blobless ZIP2 checkout and SHA-verified atomic assembly into runner temp; use same existing numerical probe and negative controls.

Other agents already updated common owner docs, so no repeated broad inventory. zip2 and protected branches READ ONLY; feature/android-native-port ONLY writable. No native Unity/APK or new automations. WATER-001/RENDER-002/FFT-FORMAT-009 OPEN, NOT_READY 0/3.
