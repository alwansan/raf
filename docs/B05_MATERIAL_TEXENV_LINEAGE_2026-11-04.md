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
