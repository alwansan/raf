# T3 — exported Renderer→Material→actual ShaderLab Dummy use diagnostic (2026-11-05)

**Owner: T3 (chat origin), RENDER-002 OPEN, device unverified.** This is a reusable **read-only source/export diagnostic**, not a game shader repair.

## Why this is distinct from the already successful source experiments

The authenticated 12-original-owner same-AssetRipper-export experiment [42033940194](https://github.com/alwansan/raf/actions/runs/42033940194) proved that TMP3.0.6, PostFXv1 and Volumetric vendor restorers reduced actual custom Material YAML documents linked to `DummyShaderTextExporter` from **511 to 495**, and referenced dummy Shader GUID targets from **54 to 50** in that disposable bounded export. Material documents are not renderer usage.

The separate original six-scene ZIP2 graph from another T3 chat [42042819113](https://github.com/alwansan/raf/actions/runs/42042819113) verified **1,495 original Renderers, 1,639 Renderer material slots, four null slots, 1,633 of 1,635 non-null slots linked to 21 typed original Shader48 objects** with two other-owner Shader identities not proven, and highest original per-Shader slot counts of **921, 219, 121, 108, 70...**. This is original-source usage, not a matching exported ShaderLab/GUID status. The two populations may have different representation, ownership and coverage. Do not silently equate 21 original Shader48 objects with 50 Dummy-marked exported GUIDs.

## New diagnostic and verified source-free controls

New `scripts/t3_exported_renderer_shader_impact.py` joins, within the **same exported Unity project**:

1. `.unity/.prefab/.asset/.mat` real YAML class 21 Material documents to their exact owner `.meta` GUID and object fileID.
2. Each Material's one strictly typed `m_Shader` PPtr to a unique real `.shader.meta` GUID and the *actual current* `.shader` text, retaining `DummyShaderTextExporter` as a diagnostic marker.
3. Exported Renderer classes 23/137/199/96/120/212 and each `m_Materials` slot to the exact Material owner/fileID and Shader classification.

The tool returns **only aggregate counters**: number of serialized Renderer objects and slots, links reaching dummy/non-dummy ShaderLab, builtin and null statuses, unresolved/unsupported references, distinct dummy Shader targets actually referenced by Renderer slots, and per-target **slot-frequency bands** 1, 2–4, 5–16 and >=17. It never emits GUIDs, names, source paths, object IDs, per-object hashes, shaders, original game bytes or per-target identifiable counts. It rejects duplicate/aliased Shader/YAML GUIDs, missing/ambiguous fields, symlinked export entries, oversized input, non-YAML standalone Materials and wrong/stale same-export Material summary. Null, builtin and unknown refs remain **unverified**.

The unit of frequency is an **exported serialized Renderer material slot**, *not* a render submission/draw call, on-screen instance, active quality tier, Adreno pixel or original source object identity.

**Green CI [42043678564](https://github.com/alwansan/raf/actions/runs/42043678564):** 11 new T3 tests + 17 inherited B03 Renderer PPtr controls + 16 T3 Material Shader quality tests = **44 synthetic tests**, including exact Material/Shader join, source-safe report, null/builtin/unresolved, bad type, wrong same-export counts, duplicate YAML anchor, symlink, output-in-source guard and cross-type GUID collision. Python syntax check passed. Earlier [42042789807](https://github.com/alwansan/raf/actions/runs/42042789807) passed 43 before the added GUID-collision regression.

## Integration path and concurrency protection

- `.github/workflows/raft-t3-renderer-shader-impact-tests.yml` runs independent lightweight controls on its own code/test changes. No LFS, ZIP2 or Unity execution.
- `.github/workflows/raft-t3-exported-renderer-shader-impact.yml` is **manual-only** after initial creation and reuses the exact twelve original ZIP2 owners, pinned AssetRipperCLI and three source-verifying vendor restorers from [42033940194](https://github.com/alwansan/raf/actions/runs/42033940194). It adds `python3 -m scripts.t3_exported_renderer_shader_impact --same-export-material-quality ...` and publishes only numeric JSON with existing safe aggregates.
- **The manual source-authentic renderer-impact workflow has NOT run.** No newly measured real exported Renderer slot counts exist from this tool. Do not infer them from original 1,639 slots, or the old 495 Material document links.
- T5 launched its separately owner-authorized full native build [42042902522](https://github.com/alwansan/raf/actions/runs/42042902522) while this tool was being verified. No second heavy original-source export or shared workflow mutation was initiated. A separate [T3→T5 handoff](../prompt/coordination/discussions/RENDER-002/20261105T1415Z-T3-exported-renderer-shader-impact-to-T5.md) gives the exact read-only insertion command for a future **authorized** native import after current active run and shared-resource reconciliation.

**Next step:** after current native or concurrent Vulkan work clears shared resources, choose **either** a scheduled manual bounded source export **or** add the read-only scan to a subsequently authorized native importer run, not both simultaneously. Validate actual linked dummy Renderer slot totals, compare original source-vs-export mapping without claiming identical GUIDs across source/export, and prioritize source-authentic Shader48 restoration using verified original reference concentration. Require Unity shader compilation, Android/Adreno pixels and user device acceptance. Keep `RENDER-002 OPEN`, preserve audio and Settings; touch/layout remains deferred.
