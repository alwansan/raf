# B03 — Exported Renderer → Material reference authenticity boundary

Date 2026-11-04, issue RENDER-002; owner B03.

## Why this matters

The existing source-linked original Material → Shader and newer texture-link/value experiments do not alone prove the MeshRenderer/SkinnedMeshRenderer inside the actual exported scene is assigned the correct Material. White meshes could arise from a null, incorrect or missing `Renderer.m_Materials` pointer even if Material assets are complete. This is one hypothesis, not yet proved by device logs.

## Implemented guard

`scripts/b03_verify_renderer_material_links.py` performs a read-only aggregate Unity YAML audit under `Assets` in an isolated exported Unity project. It resolves non-null external GUID/fileID and local embedded Material anchors to actual `!u!21` YAML documents with matching `.meta` GUIDs; validates representative Renderer types (MeshRenderer, SkinnedMeshRenderer, ParticleSystemRenderer, TrailRenderer, LineRenderer, SpriteRenderer), malformed pointers, wrong class labels, missing/duplicate IDs/GUIDs, symlinks, and oversized YAML. Missing targets are reported as errors. Null and Unity built-in Material references are counted separately as **unverified**, not upgraded to proven source matches. Only counts/booleans leave the export; no original names, GUIDs, source or materials are printed. Reports must be outside the game project.

Example (after independent original export staging):

```bash
python3 scripts/b03_verify_renderer_material_links.py \
  --project /private/isolated-unity-export \
  --out /private/outside-export/b03-renderer-material-aggregate.json
```

## Evidence and limitations

17 local synthetic tests pass, including a valid external Material, local embedded identity, invalid GUID/fileID/type, duplicate field/anchor/meta, null/builtin distinction, non-Renderer decoy, symlink, binary Material rejection, immutable source and aggregate-only report. Isolated workflow `raft-b03-renderer-material-links.yml` runs the tests without original game content or Unity. **No actual full exported Raft project has been run through this check yet**. This does not establish original Renderer→Material parity (requires original source and same-instance export mapping), correct shader programs/variants, textures/color/pixels, GPU runtime or owner device acceptance. Keep RENDER-002 OPEN until those checks plus on-phone evidence.

Next: run on an authentic complete Unity export and correlate any non-null missing Material IDs to source/export lineage before a repair. Do not remap GUIDs by name, drop slots or substitute white/dummy materials to satisfy a gate.

## CI verification

[41914562432](https://github.com/alwansan/raf/actions/runs/41914562432) completed SUCCESS (17 synthetic tests, syntax, report artifact). This is not an original full-game render test.
