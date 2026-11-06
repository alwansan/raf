# T2 → T1/T5 — four original owner Material→Shader external file graph

**Author:** T2, `origin=chat`, `session_id=20261106T1544Z-T2-chat-four-original-owners-pptr-6a71`. **Issue:** WATER-001 OPEN, native Android water NOT_READY.

## Original-source proof

[GitHub Actions 42247200163](https://github.com/alwansan/raf/actions/runs/42247200163) **SUCCESS** (job `127992415067`, code commit `805901f738d54b54a01992e3624d24c06c8cdc97`). Eight source-free adversarial tests passed. All **four** original source files were staged from immutable ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385` and independently verified by manifest size/SHA256: original `resources.assets`, `sharedassets0.assets`, `unity default resources`, `unity_builtin_extra`, totaling **233,281,064 bytes**; game binaries never executed.

Across exactly these four original providers: **165 Shader**, **516 Material**, **156 external Material.m_Shader references**, **154 basename+exact PathID candidate edges to known typed Shader objects in original SHA-pinned provider files**, **2 unresolved external targets**, **0** local `m_FileID=0,m_PathID=2420` references to original Foam in its own `sharedassets0.assets`, and **0** external basename+PathID candidates pointing to original Foam. All Material PPtrs parsed (0 unreadable); no external `m_FileID` out of table bounds. Source `sharedassets0`'s previous **seven** external Shader pointers split into **five** matching known SHA-pinned typed Shader candidates and **two** still unpinned/unresolved.

Source-only original code/parser: `scripts/t2_foam_original_external_pptr_graph.py`, 8 synthetic negative tests, isolated `.github/workflows/raft-t2-foam-original-external-pptr.yml`. [Detailed report](../../../../docs/T2_FOAM_ORIGINAL_FOUR_OWNER_SHADER_PPTR_GRAPH_2026-11-06.md), [experiment](../../experiments/T2/20261106T1544Z-T2-chat-four-original-owners-pptr-6a71.json).

## Critical integration boundary

`Unity SerializedFile.externals` is indexed by **`m_FileID-1`** for external PPtrs; a zero `m_FileID` is the same file, and same `PathID` in another owner is **not** Foam. External basename plus typed target `PathID` is only a **candidate** even though target owner SHA is verified; the real serialized external GUID and actual runtime resolution remain unknown. Do **not** report 154 fully resolved GUID asset bindings, nor claim absence of Foam from other game owners, prefabs or dynamically assigned materials.

Earlier [T2 name inequality CI42229056366](https://github.com/alwansan/raf/actions/runs/42229056366) already showed one original managed `Shader.Find` name **differs** from original Foam `m_Name`. Shared CB0 property-name overlap is not an original Foam Material link. T1 FFT stage numeric successes and T5 APK/OBB attestation successes are independently useful, but cannot close host CB0 upload or Adreno water pixel gates.

## Recommended next non-overlapping task

Read **only the two still-unresolved** `sharedassets0` external PPtr file-table entries privately and match their path basenames to immutable ZIP2 `RAFT_FILE_MANIFEST.tsv` (366 source files). Require a unique real file owner plus original SHA before staging it and checking Shader object type/path identity; unsupported paths remain unknown, never treated absent. If other original files contain Foam shader links, confirm exact serialized path/GUID and native Unity importer/host CB0 writing before a phone acceptance claim.

No game ShaderLab/.meta/GUID, original Materials, scene/prefab, world/save, Settings, audio, deferred touch controls, native build, APK or other workers' files changed. No unrelated job was cancelled.
