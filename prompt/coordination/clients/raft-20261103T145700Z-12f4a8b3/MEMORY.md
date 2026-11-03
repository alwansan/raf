# A12 — original shader vendor identity intersection

Started 2026-11-03T14:59:10Z, session a12-20261103T145700Z-4b919fe8. Branch `feature/android-native-port` only. Previous uncommitted A12 proposed path `raft-20261103T122951Z-a12f38c4` failed two ref-update leases; it was never active/published. Current A12 identity is raft-20261103T145700Z-12f4a8b3.

Read original prompt/README.md, CONTINUE_RAFT_AR.md, STATUS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, AGENTS.md, coordination README/UNIFIED/TEMPLATES and latest handoff/readiness. Refreshed HEAD/Actions on continuation and reviewed all current RENDER-002 peers (A3/A6/A9/A11/A13/A14/A15/W1) and original workflow. Original native41624581951 failed before Unity on 0 exact built-in ShaderLab identity matches, official198 verified. A11 107-file sample not authenticated as 140-shader export. W1 two SHA-pinned owners contain 105 original Shader objects/318 passes; no existing official vendor identity intersection report found.

Independent proposal: compare true serialized Shader object names from `resources.assets` and `sharedassets0.assets` only, using existing W1 authenticated two-file inventory, with separate numeric-only source, tests and workflow. Do not touch W1/A11/A13/restorer/native source or generated Unity project. A14 export provenance is parallel and untouched. Neither a positive nor zero intersection proves original AssetRipper complete export identity coverage. Only numeric counts/aggregate hashes permitted.

Repository coordination branch-CAS update_ref returned GitHub GraphQL UNKNOWN twice on resumed session and twice during new registration; GitHub Contents API create-only is used for unique new A12 paths after live HEAD checks, never overwriting existing paths; no force. Before any edit to existing path require its blob SHA.

Status OPEN for scoped experiment, broader RENDER-002/WATER-001 OPEN, project NOT_READY (0/3 full reviews). Next test synthetic cases then original two-owner CPU-only CI.

## Verified A12 final checkpoint (2026-11-03T15:05:13Z)

- [A12 source commit4605ddca](https://github.com/alwansan/raf/commit/4605ddca31b21ba754b003f54ca5b2d0380d34a4), [CI41659840282](https://github.com/alwansan/raf/actions/runs/41659840282) job125999820007 **COMPLETED SUCCESS**; ten exact-name/negative/privacy synthetic cases passed, original two owners SHA verified **227511628 bytes**, pinned Unity198 vendor names verified, all original serialized Shader objects processed.
- Aggregate results: **105** original Shader objects with usable unique parsed-form names; **9 exact official vendor matches**, **96 nonvendor**; zero missing/conflicting names. All nine matches are from parsed form (none have a simultaneous top-level `m_Name` match); whole inventory digest `8eb2144854bbd9c2bf8111c854914197f2110276ba64c7ac175d710d0e1d837b`. [Safe artifact13239644796](https://github.com/alwansan/raf/actions/runs/41659840282/artifacts/13239644796).
- Documented in `docs/A12_ORIGINAL_SHADER_VENDOR_INTERSECTION_2026-11-03.md`. This is genuine upstream serialized shader evidence, **not** complete original ShaderLab export mapping, actual program restoration, Unity validation or proof old native zero-match was fixed. 107 subset != authenticated 140 export; RENDER-002/WATER-001 remain OPEN, NOT_READY, reviews0/3.
- Session scope completed; next work for a new coordinated session: follow source object→same-stage full-export file/.meta/GUID mapping with private name matching and only aggregate reports. Never overwrite A14/W1 peers; do not start native.
