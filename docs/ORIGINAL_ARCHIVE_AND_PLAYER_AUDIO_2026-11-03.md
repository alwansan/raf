# Original six-part archive and early player audio guards — 3 November 2026

Only feature/android-native-port is writable. No Unity import/build, package or release was started.

## Original archive evidence

All six owner-supplied Raft-SteamRIP.com.zip.001–006 parts were identified and materialized successfully. Their combined length is 2,636,697,605 bytes. A seekable multipart reader opened the outer ZIP without changing its parts; streaming the sole stored entry verified its ZIP CRC32 267f9c77.

The contained Raft-SteamRIP.com.rar is 2,636,697,429 bytes, SHA256 324baa386a060344026e148c4d8eacfd8cb55c1dbec2a719a702c4ad5ec03511. Read-only libarchive inspection listed 394 entries totaling 7,829,882,559 uncompressed bytes. No Windows executable was run. No loose .shader/.compute/.hlsl/.cginc/.unitypackage source entry was found. Compiled Unity assets and original game binaries are present; this is not evidence of restored shader source.

Selected entries were streamed through libarchive and hashed without publishing their proprietary bytes:

| Entry | Bytes | SHA256 |
|---|---:|---|
| Assembly-CSharp.dll | 3211776 | 0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e |
| MasterBank.bank | 101600960 | 10d310416b9f104a38b4ead8877e114142e154efb33105fcddbb2024a81af339 |
| MasterBank.strings.bank | 29530 | 72cd8d60b0cd84b28359dd06dd1a73f2e00cb77f9d9e9b572e4d87db0cf01896 |
| VO_logs_english.bank | 11455008 | 60783fd0c9f935313732ab253e604091674b4e8d0c06a3ac92ba09a1aa1e51cb |
| VO_npc_english.bank | 8180896 | 3e5c01e25feab18183b6ae90d39fb703800fc40a5580bf59f8af83538978f028 |
| VO_olof_english.bank | 2551104 | 9eaa50efd40309443a4c704353fdff185b8262466abf676b723a8c753f36b230 |

Assembly-CSharp matches the tracked original Git object. MasterBank matches the already pinned Git LFS object exactly. The archive therefore supplies an independently checked copy of those original files, not a different audio-bank fix. Existing bank staging/path restoration remains necessary. Avoid downloading duplicate LFS bytes just to obtain the same object.

## Functional repair

Original SHA-pinned PersonController.Start calls one of two fall StudioEventEmitter.Play methods before creating jump/land instances and restoring settings/actionMove. Earlier protection covered only the two CreateInstance assignments. A missing fall event could therefore still abort control initialization.

Commit c22ebf30125f9754b178a3f3d412ae886572b3fc adds Android-only guards around each original early Play statement. Only FMODUnity.EventNotFoundException is caught and critically logged as audio.player_fall_emitter_missing_fmod_event. Original local/remote branching, settings, movement setup, host state and real FMOD loading are preserved. Other exception types remain visible. No event/host success is fabricated.

Thirty-eight relevant local Python adapter/offline/source-probe tests passed, including exact desktop-source preservation and fail-closed count/type/order checks. Transformation also passed against the authenticated original PersonController source. An executable C# harness uses the emitted adapter guards with test-owned doubles to cover local/remote paths, each missing-event stage and propagation of an unrelated exception. Original-source integration CI: https://github.com/alwansan/raf/actions/runs/41551991560 completed SUCCESS, job125641592177. The C# guard harness passed all10 cases; adapted original gameplay compilation exited0 with no compiler error codes. This is managed compilation, not Unity/device validation.

## FFT evidence and limits

Resource-binding CI https://github.com/alwansan/raf/actions/runs/41551173277 succeeded on 1307e1e42eb27802268d1b7861da1cfc4dda19ce. All 20 original compiled resource metadata slots match original C# source/butterfly/output name hashes and t0/t1/u0 roles. Pass-zero output feeds pass-one input; both use the same butterfly image. This is structural provenance, not numerical equivalence, Android storage-image format compatibility or runtime kernel-index proof.

Previous VKD3D/SPIRV-Cross CPU translation results remain documented separately. DXVK/VKD3D are useful inspection/translation tools; their Windows compatibility libraries do not by themselves restore native Unity shader sources. Keep the strict water gate closed until the missing semantic/runtime evidence is resolved.

APK80 remains the last published device binary. None of these later source changes establishes phone audio, rendering, Settings aspect, touch or world acceptance. Ignore unavailable الجلسة1.txt and text.txt as instructed.
