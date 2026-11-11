# T3 paired material dependency checkpoint — 2026-11-11 20:26 UTC

- session_id: 20261111T2026Z-T3-scheduled-pair-audit-q8n4
- origin: scheduled
- issue_id: RENDER-002
- resumed_from_session: 20261111T1930Z-T3-scheduled-shader-orphan-g7q2
- work: prompt/coordination/work/RENDER-002/20261111T2026Z-T3-scheduled-pair-audit-q8n4.json
- experiment_key: t3-paired-material-shader-texenv-reference-diff-v1
- source commit: a4ad7091636fcda4752119c100c205c068b80123

## New independent implementation
Added scripts/t3_material_dependency_pair_audit.py. It compares the serialized shader reference and multiset of m_TexEnvs texture GUIDs in same-relative-path .mat files from two independently verified trees. It emits aggregate counts only, skips symlinks/oversize files and does not publish raw paths, GUIDs, or assets. This is an additional diagnostic to the previous per-tree shader and texture meta owner audits, not a replacement.

Invocation after obtaining two authentic, same-scope material trees:
`python scripts/t3_material_dependency_pair_audit.py --original <verified-original-material-root> --exported <verified-export-material-root>`

## Owner evidence and boundaries
Read docs/DEVICE_FEEDBACK_42058825739_AR.md. Phone run 42058825739 source e9c358eda01785b65e4eb14f18723da426635628 confirmed world/save/reentry, not rendering. CL screenshots show white hand/raft and square particle, while 220911-559 reports 23884 water-pass errors, 3850 FFT kernel errors; not a proven material cause. The earlier export CI 41939404454 had 41 materials, 227 UV transforms, 89 internal texture references and 25 external unresolved; scope-specific only.

## Verification status
SOURCE_ADDED_NOT_EXECUTED. GitHub connector could write source but no runner execution was performed, and neither original ZIP2 nor actual export was materialized. The comparison is not a Unity/GPU/device test. In particular, it does not compare texture slot names, color properties, blend, alpha or shader keywords, so identical references cannot close RENDER-002. No original .meta, GUID, .rgd, game scenes or build pipelines modified.

## Next
1. Execute a synthetic fixture against this script and fix any parsing issues before claiming PASS.
2. Verify ZIP2 and export provenance, then run on identical material scope; follow mismatches to shader/texture .meta owners, particle renderer and shader alpha/blend.
3. If zero differences, investigate import, variants, color space, lighting and particle atlas rather than guessing missing textures.
4. Preserve T4 mouse and T5 resolution/delivery ownership; do not duplicate full XAPK or shared Mini build.
