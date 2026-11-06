# T2 — SHA-original Foam Graphics.Blit direct Texture / RenderTexture producer roles

**UTC:** 2026-11-06T22:35:16.721Z · **Owner:** T2 · **Issue:** WATER-001 · **Session:** 20261107T2227Z-T2-chat-blit-texture-role-6c52

## Evidence and exact source scope

The original Raft shader owner and managed DLL remain pinned to the immutable ZIP2 source `15964ea8f246b6e076ce26b60931ee2e1a9a2385` by the established source-only workflow; original `sharedassets0.assets` owner 115,978,112 bytes and managed `Assembly-CSharp.dll` 3,211,776 bytes are verified against manifest/SHA in private CI scratch. Shader identity, original method names, field names, raw IL and game bytes are **never published**.

- [Source code commit 681c239c](https://github.com/alwansan/raf/commit/681c239c29959e420829b48ba24c4ab203ce9ca5), modifying only three T2-owned source-only scanner/validator/test files.
- [Original source workflow 42305522855](https://github.com/alwansan/raf/actions/runs/42305522855), job 128193753398 **SUCCESS** on exact code SHA, with 63/63 source-free strict report tests, 6/6 name controls, Mono.Cecil synthetic selftest PASS, original source SHA reauthentication and private scratch cleanup.
- Safe aggregate artifact `13545388075` (1,376 bytes), SHA256 `b9358da551f1977e71ada7ea2bc84361229719c825070b234167b488b086ab4b`.

## Strict bounded static result

The *same two* original exact Foam Material field sites lead to public `Graphics.Blit(UnityEngine.Texture, UnityEngine.RenderTexture, UnityEngine.Material, System.Int32 pass)` (one has explicit pass literal 0, one has literal 1).

| Source-original direct IL category | Count |
|---|---:|
| Blit sites with directly proven source expression typed `UnityEngine.Texture` | 0 |
| Blit sites with directly proven source typed `UnityEngine.RenderTexture` | **1** |
| Blit sites with source producer not proved by direct expression parser | **1** |
| Blit sites with directly proven destination typed `UnityEngine.RenderTexture` | **1** |
| Blit sites with directly proven destination `null` | **0** |
| Blit sites with destination producer not proved by direct expression parser | **1** |

Each partition is exclusive and sums to two. The parser accepts only a direct adjacent straight-line IL pattern `source, destination, original Material field load, int pass, Graphics.Blit`, with simple typed field/local/explicit null source producers; computed producers, casts/calls, extra stack instructions and noncanonical IL remain `unknown`. It does NOT try to reconstruct private names, verify original allocation, or infer execution.

**Important limit:** Counts are separately aggregated per source and destination, so this report does *not* yet correlate the verified source/destination with `pass=0` or `pass=1`; do not attribute a specific render target to either pass. Also, a typed `RenderTexture` source or destination is *not* a proof of a live RenderTexture object, correct format/size, allocation, bindings, CB0 upload, Unity rendering or Android pixels.

## Required next step

In another isolated original-only scan, correlate each direct source/destination category with the already proven public pass literal 0/1 without releasing original field or method identities. Validate per-pass two-site partitions. Where source/destination remains unknown, trace exact producer through bounded IL/dataflow or compare Unity Resource ownership privately. Then coordinate with T5 on real Unity 2021 shader import, preserved `.meta` GUID, Material PPtr and actual two-pass Blit execution. Original CB0 stage-specific array-length mismatch from [CI42300107157](https://github.com/alwansan/raf/actions/runs/42300107157) remains open.

WATER-001 OPEN. Android water pixels and final game readiness are NOT verified. Older owner-native [42296450023](https://github.com/alwansan/raf/actions/runs/42296450023) is independent on an immutable older source and cannot include this source-only instrumentation.
