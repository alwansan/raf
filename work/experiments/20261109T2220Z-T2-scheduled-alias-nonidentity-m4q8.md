# T2 WATER-001 independent scope
session_id: 20261109T2220Z-T2-scheduled-alias-nonidentity-m4q8
origin: scheduled
baseline_sha: bdae2ce33a3088c9e5e32333d46829807dfec8be
experiment_key: T2-FOAM-SSA-NONALIAS-SOUNDNESS-20261109
files: scripts/t2_foam_alias_dataflow.py; tests/test_t2_foam_alias_dataflow.py; work/experiments/20261109T2220Z-T2-scheduled-alias-nonidentity-m4q8.md; clients/T2/sessions/20261109T2220Z-T2-scheduled-alias-nonidentity-m4q8.md
hypothesis: disjoint SSA value tokens do NOT prove distinct runtime object instances because two different SSA values may alias one RenderTexture. Current different_instance_proven() is unsound. Change conservative gate to reject unsupported nonalias claims; adjust regression, add explicit distinct-SSA-but-same-object test.
shared_resources: none; no Unity or CI requested; no T1/T3/T4/T5 files touched.
source_evidence: original Foam crosspass runtime identity remains unknown; device 42058825739 shows world load/save/re-entry but rendering errors.
