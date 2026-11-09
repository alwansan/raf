# GFX-LAB session 20261110-GFX-chat-shears-textures-42707671345

Identity GFX-LAB. Origin chat. Resumed from 20261110-GFX-chat-avatar-001-42702078254. Branch experiment/android-graphics-rootcause. No changes to T1-T5 feature branch.

## Owner's real device feedback
GFX-AVATAR-001 succeeded on Xiaomi 23013PC75G, Adreno 730, OpenGL ES3.2, Unity2021.3.45f2, Linear, 375 vertices, 420 triangles, 1 renderer, 0 errors. White displayed geometry is visually **Shears**, NOT player character. The prior classifier original_player_like_skinned was misleading: it inherited the label from an ancestor, but the actual 375/420 geometry is a skinned scissors attachment. Source screenshot confirms bluish metal blades and brown grip/hand. User supplied images in chat; no proprietary screenshot reuploaded to repo.

## Authenticated source findings
- GFX-SHEARS-002 CI42705610994 SUCCESS: same exact source 375/420 Mesh -> SkinnedMeshRenderer -> one original Material21 -> one original Shader48, both SHA verified. Original Shader contains two SubShaders and seven Passes. Material has two color slots and nine TexEnv slots, three valid source Texture2D28 refs and six original nulls. Mesh has 375 UVs and 375 normals; renderer has three bones and valid root bone.
- GFX-SHEARS-003 CI42706123513 SUCCESS: one original albedo/basecolor, one normal, one metallic texture; all three are streamed externally via resS; 3,145,728 pixels total. No inline images, so initial white output was intentional white Standard material, not evidence of corrupt source textures.
- GFX-SHEARS-004 CI42707235695 SUCCESS: exact three original texture ranges span THREE immutable Git chunks, 141,557,760 selected bytes, one source stream provider, rather than complete sharedassets0.assets.resS 1.779GB. Verified each Git blob identity; private sparse resource offsets, decoded all three actual PNGs inside runner; exact original albedo tint also found. No loose original PNGs published.
- Version 0.1 white game-independent mini APK source GFX-AVATAR-001 device PASS; geometry success does NOT imply original shader restored or full character.
- New GFX-SHEARS-005 CI https://github.com/alwansan/raf/actions/runs/42707671345 is IN_PROGRESS (real Unity 2021 Editor build step at checkpoint). Do not claim new APK until completed success.

## Code and acceptance
GFX-LAB scripts: gfxlab/tools/shears_provenance_probe.py; shears_texture_readiness.py; shears_stream_transport.py; all unit tests. Standalone build uses exact original 375/420 Mesh, three original Texture2D images, original albedo tint in temporary Unity project, Android ARM64 IL2CPP OpenGLES3. Viewer modes WHITE_LIT, WHITE_UNLIT, SOURCE_ALBEDO_STANDARD_DIAGNOSTIC and SOURCE_TEXTURE_PBR_STANDARD_APPROX. New separate package: com.alwansan.raft.graphicslab.shears; original Shader seven passes are NOT restored, so Standard fallback is NOT final parity.

Next check CI42707671345, verify signed APK/shas and deliver private test APK if successful. Owner tests screenshots and COPY LOG across modes, focusing albedo blue/brown, normal and metallic approximations. Actual original shader pass/keyword/bindings translation later and separate from albedo. This session checkpoint is source-backed and all original payloads remain private and purged. 

## GFX-SHEARS-005 verified completion and delivery
- [CI42707671345](https://github.com/alwansan/raf/actions/runs/42707671345) **COMPLETED SUCCESS**. Actual Unity2021.3.45f2 Android Editor import + IL2CPP ARM64 APK BuildPipeline **PASS**, original 3 source PNG and original tint private stage verified, Android APK structure and signature **PASS**.
- [Signed APK artifact 13714487772](https://github.com/alwansan/raf/actions/runs/42707671345/artifacts/13714487772), expiration 2026-11-16T22:06:20Z. Exactly **10,887,469 bytes**, SHA256 **f50f59f547a9d1dcdd934f0993df825a1df57e0312aa20f8a63e3bba1f0b1af2**, separate package com.alwansan.raft.graphicslab.shears.
- GitHub artifact ZIP downloaded and APK extracted to a direct current-chat attachment **Raft-GFX-Shears-Source-Textures-v0.2.apk**, independently verified byte-size SHA and lib/arm64-v8a/libunity.so; no OBB.
- Four visual modes: white lit, white unlit, source albedo plus exact original tint on **Unity Standard**, original albedo+normal+metallic on **Unity Standard approximation**. Actual original Shader48 2 SubShaders / 7 Passes remains unported; does not prove shader or lighting fidelity in Raft game.
- **Owner device evaluation v0.2 pending.** Ask for screenshots in modes SOURCE_ALBEDO_STANDARD_DIAGNOSTIC and SOURCE_TEXTURE_PBR_STANDARD_APPROX, two COPY LOG JSON reports, visual blue blade/brown handle comparison, and any exception.
- Source artifacts (three loose PNGs, stream bytes, private colors, original metadata) were purged after CI, not uploaded separately.
