# B04 Mesh source path integrity — ASSET-RESTORE-001 (2026-11-04)

## Engineering scope
Scoped hardening of `scripts/repair_exported_mesh_vertices.py`, a
vertex-only restoration helper for generated Mesh YAML sourced from
authenticated original data. No original Mesh geometry or serialized bytes
are uploaded or changed. The owner asked to preserve .meta/GUID fidelity.
Earlier code validated vertex layout and original material but followed
filesystem symlinks in exported/source mesh paths: this could read a different
provider or write outside the intended temporary Mesh project.

## Change and proof
- [B04 source change f0afb59](https://github.com/alwansan/raf/commit/f0afb5983694cec91a61bcd6f9825ca1cf658f7e)
  rejects linked `project`, `Assets`, `Assets/Mesh` directories and
  per-file `*.asset` / `*.asset.meta` symbolic or multi-link files
  **before** any YAML parse, snapshot or mutation. Missing .meta fails closed.
- Reject dangling `snapshot` directory symlink even if `Path.exists()` is
  false. Existing source snapshot preservation, same-schema vertex-only
  replacement and meta byte comparison are otherwise unchanged.
- [B04 adversarial test changes ed378a1](https://github.com/alwansan/raf/commit/ed378a19b76e365bb19f74436680b3346de0d5de)
  verify target Mesh link, target .meta link, provider Mesh symlink,
  hardlinked payload and .meta, Mesh directory link and dangling snapshot
  symlink. The prior valid vertex-restoration, GUID/meta preservation,
  wrong-layout rejection and nonfinite position controls remain enabled.
- Isolated `raft-b04-mesh-source-safety.yml` runner Ubuntu24.04, timeout
  6min, `PyYAML==6.0.2`; no Unity Editor, LFS, private data or full APK.
  See [Actions B04 mesh source safety](https://github.com/alwansan/raf/actions/workflows/raft-b04-mesh-source-safety.yml).

## Correct limits
These checks enforce filesystem provenance/safety, **not** proof that
all original meshes, vertex payloads, texture imports, shader links or
the device's white materials are repaired. The main Unity delivery
currently runs a separate verified Mesh-stream inline stage; this
isolated mesh YAML helper is not newly inserted into that pipeline.
Do not claim ASSET-RESTORE-001 closed. Original source ZIP2 owner
SHA15964ea8f246b6e076ce26b60931ee2e1a9a2385 unchanged.

## Next
Record actual B04 isolated CI conclusion; if successful, retain as a
precondition for future Mesh restoration where this helper is used.
For real geometry, check original stream SHA/size, source/target Mesh
identity, exported GUID and device mesh rendering independently.
