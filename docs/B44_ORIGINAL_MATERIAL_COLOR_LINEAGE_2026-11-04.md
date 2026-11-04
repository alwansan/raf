# B44 — Source-authenticated Material color lineage guard (2026-11-04)

## Scope and question
For RENDER-002, an original Material->Shader reference can stay correct while `m_SavedProperties.m_Colors` silently changes to an identity/white tint during YAML export. Existing W1 same-instance Material Shader PPtr audit verifies shader association, not original per-slot color values. B44 implemented an independent fail-closed comparison, without changing original resource bytes, GUIDs or production shaders.

## Delivered source
- [Comparator](../scripts/b44_verify_material_colors.py) authenticates fourteen original Shader-bearing asset owners by independent source SHA/size from `scripts.a12_probe_original_blur_passes.SHADER_OWNERS`, uses the private same-process trace in `RaftExportLineage.cs`, joins source Material identity to actual exported YAML by `fileID`/container meta GUID, includes loose and embedded Material documents, and compares original and exported RGBA per saved slot.
- [Regression tests](../tests/test_b44_verify_material_colors.py) reject wrong/missing/extra colors, swapped GUID, duplicate source, malformed and duplicate YAML keys, NaN/non-finite components and symlinked outputs. The duplicate-key hardening closes PyYAML's default silent overwrite case.
- [Independent bounded workflow](../.github/workflows/raft-b44-material-colors.yml) runs on Ubuntu 24.04 with Python 3.11, pinned PyYAML 6.0.3, no ZIP2/LFS/Unity/Android build.

The output contains only integer aggregate mismatches, never private original object identifiers or exact color values. Distinct engine material redirects and font importer materials are excluded from this comparison, not falsely asserted equivalent.

## Evidence and limitations
- Initial 10/10 synthetic positive/negative tests: [CI 41912783093](https://github.com/alwansan/raf/actions/runs/41912783093) **SUCCESS**, source `f1dd7fccb7607264d7ec9fee6a67cb73cbbd7eb7`.
- Hardened 11/11 synthetic tests: [CI 41913494314](https://github.com/alwansan/raf/actions/runs/41913494314) **SUCCESS**, source `dda05b1638480f4a2d9ab37149ac792500cfec5b`.
- Demonstrated counterexample: unchanged shader pointer plus modified or dropped RGBA slot => guard fails. Therefore shader association cannot alone attest color fidelity.
- **No real Raft original/export comparison run.** An authentic same-instance exporter trial is still needed to determine if any original material tint actually changed. This is source QA instrumentation, **not an original-game visual fix**, Unity compilation result, or Adreno/device evidence. RENDER-002 remains OPEN; NOT_READY, readiness 0/3. No new APK or phone testing.

## Exact next integration experiment
On the **next already coordinated** original export using pinned ZIP2 original SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, after the exporter has generated the private trace and unmodified Material YAML:

```bash
python3 -m pip install --disable-pip-version-check PyYAML==6.0.3
python3 -m scripts.b44_verify_material_colors \
  --source "$RUNNER_TEMP/w1-original" \
  --private-export-trace "$RUNNER_TEMP/private-export-lineage.json" \
  --project "$RUNNER_TEMP/project/ExportedProject" \
  --out "$RUNNER_TEMP/b44-material-colors-aggregate.json"
```

Keep original files and the private trace inside the authorized runner/staging; only the aggregate safe summary may be retained publicly. A mismatch requires isolating the exact Material serializer/render path and fixing it with original-source evidence; if all values match, do not repeat the same census and concentrate on custom shader/texture/sRGB/lighting. Do not start another equivalent full Unity build solely for this diagnostic.

Coordination record: [B44's independent peer discussion](../prompt/coordination/discussions/RENDER-002/20261104T2107Z-B44-material-colors-next-export.md) and [session memory](../prompt/coordination/clients/B44/MEMORY.md).
