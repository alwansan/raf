# B05 — authenticated Material texture binding / export lineage contract (4 Nov 2026)

## Scope, rationale and coordination
Agent: B05, session `20261104T2107Z-B05-9e24`, issue RENDER-002 (OPEN).
Observed installed game evidence is APK86, [delivery 41812889049](https://github.com/alwansan/raf/actions/runs/41812889049), source d181ee71. CL 2026-11-04 shows pale/white materials but color symptoms alone do not prove missing geometry or a particular texture link defect. B02 independently covers sRGB importer provenance; B44 original/export m_Colors; W1 actual shader pointers; W2 original m_TexEnvs aggregate. This B05 work isolates an additional material-to-texture fidelity boundary, without changing any shared game/runtime source.

## Implemented production-use verification
[Verifier code 8398553](https://github.com/alwansan/raf/commit/8398553c2e4d58863998bc329ecf332af08fa0b2):
`scripts/b05_verify_material_texenv_bindings.py`.
[11 synthetic regression cases 94f47ac](https://github.com/alwansan/raf/commit/94f47acffd185820445fbb9df1b2b52e0288c687).

Invocation after an **authenticated, same-instance export**:

```bash
python -m scripts.b05_verify_material_texenv_bindings \
  --original /absolute/verified-zip2/Raft \
  --project /absolute/same-instance-Unity-export \
  --trace /absolute/private/same-instance-export-trace.json \
  --out /absolute/outside-export/b05-material-texenv-summary.json
```

The original owners are validated by the existing 14-owner source-size/SHA fingerprint collection; the preferred upstream ZIP2 provider is immutable source `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, not the unvalidated private release transport wrapper. Material trace must retain unique original (owner, pathID) and export (fileID, GUID, type) identities and one exact export_instance. YAML material entities include loose .mat and embedded Material records.

Every original `m_SavedProperties.m_TexEnvs` slot is compared against the corresponding export Material m_TexEnvs; report counts missing/unexpected slots, null→bound, bound→null, and wrong exact internal texture target mapped through an explicit same-instance Texture object trace. If a target is external to its owner, it is counted as **not proven**, never matched by bare pathID, label or filename. Missing internal object trace fails scoped completion. Other original .meta/GUID/data are untouched, report contains only aggregate counters.

## Actual evidence
[Isolated GitHub Actions run 41914198631](https://github.com/alwansan/raf/actions/runs/41914198631) **COMPLETED SUCCESS** on SHA `5948d0d5041424bb175e007481b38bc0c9f19a18`; 11/11 synthetic source-free cases passed in Python 3.11, PyYAML 6.0.3 on Ubuntu 24.04. Positive: exact internal identity, null slot and deliberately unresolved external pointer. Negative controls reject wrong texture target, missing/extra slot, nullness change, missing/duplicate object trace, wrong export identity, malformed PPtr and linked export traversal. Workflow runs for B05 paths or explicit dispatch only, timeout 8 min, unique concurrency cancel-in-progress false; no LFS/private payload or original shaders in logs/artifacts.

**This is integration of a verification tool, not restoration of an original shader, Material or visible color.** No actual original Material/export pair has been compared in this result. No Unity/GPU/Android verification, no reported original mismatch, no modification to original game content, sound, Settings, touch or native request. It cannot close RENDER-002 or assert any whole-game readiness: NOT_READY, independent reviews 0/3.

## Rejected/unproven assumptions and next action
Rejected: treating a matching bare external `m_PathID` as the same texture, or inferring texture fidelity solely from correct m_Colors/sRGB; both can produce false positives. Not yet tested: UV scale/offset, sampling and format semantics, external-owner resolution via verified dependency tables, source/export execution on same immutable invocation. Next run this tool against source-size/SHA validated ZIP2 providers and a **single original→export trace generated with the exact Unity export** (a historic trace from another instance is invalid), audit unproven external references and then patch only a demonstrated export source defect. Keep source and candidate SHA in evidence, then use a real Unity/Adreno/pixel comparison to validate visual restoration.


## B05 follow-up: original UV transform drift guard (2026-11-04 21:25 UTC)
The initial bounded tool could report preserved texture pointers while silently overlooking the UV transform `m_Scale` and `m_Offset` attached to each m_TexEnvs slot. B05 extended the **same production-use checker** with 4 finite vector components, a partial-transform rejection, numeric tolerance comparison and separate counts `uv_transform_slots_compared`, `uv_transform_missing_or_unproven`, `uv_transform_value_mismatches`, and `all_uv_transforms_verified`. Source-free fixtures with no original UV metadata remain explicitly **unverified** rather than silently treated as restored.

- [B05 source change 834afd6](https://github.com/alwansan/raf/commit/834afd6dfe4e96bd02e427f75fbb403f382f5700), [synthetic pointer fixture recovery bf3b23d](https://github.com/alwansan/raf/commit/bf3b23dcb131d2607d03e9a7706e6b4fe004b4b8), [14 controls 93aaee8](https://github.com/alwansan/raf/commit/93aaee8df9d17f0a646e46d98a71d525f5e3c82b).
- [CI41915604221](https://github.com/alwansan/raf/actions/runs/41915604221) **COMPLETED SUCCESS**, 14/14; [final workflow-label source CI41915726289](https://github.com/alwansan/raf/actions/runs/41915726289) **COMPLETED SUCCESS** on source `dd7d20f236b5d2f4890e019b0d65cdeb74bdedd3`.
- Two earlier red runs [41915487156](https://github.com/alwansan/raf/actions/runs/41915487156) and [41915549118](https://github.com/alwansan/raf/actions/runs/41915549118) resulted from the test fixture migration from raw PPtr to `(PPtr, UV)`, not evidence of original game damage. Exact cause and successful fix are archived in [B05 incident](../prompt/coordination/incidents/B05/20261104T2122Z-uv-fixture-migration.md).

The new checker has still **not run on actual original ZIP2 Materials and same-instance Unity export**; there is no measured actual UV mismatch or visible color/game improvement. Texture transforms are now included in the planned acceptance, but external links, shader programs, lighting and device pixels remain unverified. RENDER-002 stays OPEN; NOT_READY 0/3. Preserve audio, Settings and deferred touch.

## Resumed B05: first REAL ZIP2 Material + UV source acceptance — 4 November 2026, 22:53 UTC

**New true-original input, not another synthetic-only result.** [CI41929077930](https://github.com/alwansan/raf/actions/runs/41929077930) COMPLETED SUCCESS at source [d6fa219c](https://github.com/alwansan/raf/commit/d6fa219c769e3c4d11f798f41bfc0cbd8451465b); job126921056144. It checked out immutable ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, read only `Raft/Raft_Data/sharedassets6.assets` (6,607,272 bytes, SHA256 `0476792cfeffac19d16e920011ed8d2fb2da62973c2f09a8689bc59e1ac4b632`), staged via manifest-verified no-LFS reader, rechecked SHA, and parsed *actual* UnityPy 1.25.4 `Material.m_SavedProperties.m_TexEnvs` fields. Output is counts only.

| Original source metric, this owner only | Observed |
|---|---:|
| Material objects | 41 |
| Texture slots | 227 |
| Bound same-owner PPtrs | 89 |
| Bound external-owner PPtrs | 25 |
| Legitimate null texture slots | 113 |
| Original scale+offset UV sets fully decoded | 227/227 |
| Materials with at least one bound Texture | 40 |

**New explicit integration proof:** The same CI read the file through B05's *production* `original_texenvs(root, owner_names={'sharedassets6.assets'})` source selector and independently reconciled 41 Material/227 slot counts with the direct original parsing. `pinned_scoped_accessor_verified=true`. Seven source-free failure controls passed before acquisition. [Previous authentic run41928076197](https://github.com/alwansan/raf/actions/runs/41928076197) gave the same 41/227/89/25/113 result. No original source file was committed or altered.

### Scoped source-to-full-export comparator

B05 added `--owner sharedassets6.assets` to the existing source-to-export verifier. It permits selecting the exact SHA-verified owner above while retaining every exported `.mat` / embedded Material document and every outside-owner traced Material; nonselected original material rows are **explicitly excluded**, not falsely flagged missing. Selected Materials still require a unique exact same-instance trace, no missing selected objects, no changed texture target/UV and no pointer collisions with excluded sources. Published summary includes `source_scope=selected-owner`, `outside_scope_export_materials`, `selected_original_owner_count` and `full_game_source_coverage_verified=false`. Global `all_texture_targets_proven` stays **false** for partial selection even if all selected pointers match. With no `--owner`, original full pinned-source strictness remains the default.

[B05 scoped source c6ae0cd](https://github.com/alwansan/raf/commit/c6ae0cd855ad2423f0e46e7ad598bcae00ef81c9), [18 original-vs-export synthetic controls fd35126](https://github.com/alwansan/raf/commit/fd351264810b805d31299ccc9cc8d2d26c39155e), [final green CI41928852363](https://github.com/alwansan/raf/actions/runs/41928852363) COMPLETED SUCCESS, **18/18**. Source owner allowlist independently pinned in [bd14417](https://github.com/alwansan/raf/commit/bd14417a7038180fe7f3f3ab2550fc0b26ca154c); original probe shares the pin in [15edb76](https://github.com/alwansan/raf/commit/15edb7662faa569dcff06d040ca5ea776e43614b). The selected original accessor is proven at source-input level in final authentic CI.

Two intermediate synthetic red runs [41928537671](https://github.com/alwansan/raf/actions/runs/41928537671) and [41928655703](https://github.com/alwansan/raf/actions/runs/41928655703) exposed optional import dependencies (`UnityPy` then heavyweight A12 inventory missing from sparse checkout) *before* the negative unknown-owner rejection. B05 moved authorization ahead of serializer import and pinned the selected genuine owner locally, retaining separate 14-owner default. [Incident record](../prompt/coordination/incidents/B05/20261104T2251Z-scoped-import-recovery.md). No game data was accessed by the red tests. Final 18/18 synthetic and 7/7 source-side tests succeeded.

**Critical limitation:** no actual SAME-INSTANCE exported Raft Unity project/object trace was supplied to this B05 test, so the original-vs-export comparison has **not** run on an authentic pair; no lost texture/UV, color repair or playable scene is proven. Scoped source acceptance is not global 82-owner coverage (known full-game 1,556 Materials); the 41/227 figures refer only to sharedassets6. The GitHub team [coordination message](../prompt/coordination/discussions/RENDER-002/20261104T2253Z-B05-authentic-scoped-export.md) requests this check in the next already-authorized shared export, not a duplicate Unity build. RENDER-002 OPEN; NOT_READY, three independent readiness reviews 0/3; sound/Settings owner-confirmed, touch deferred.
