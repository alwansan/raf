# T3 work 20261112T0028Z-T3-scheduled-parser-guard-m8q2
origin: scheduled
issue_id: RENDER-002
base_sha: 5690818e3b8f245aedd2eeaac04704ac3121d225
status: completed_source_patch_unverified_runtime
intended_files: tests/test_t3_material_dependency_pair_audit.py (new isolated regression)
experiment_key: T3-pair-parser-mTexEnvs-slot-depth-fixture-v1
resource_key: none (pure Python)
hypothesis: the current material comparison can misattribute texture slots when a nested YAML field is mistaken for a sibling; a small fixture test should establish current behavior before any fix.
source: scripts/t3_material_dependency_pair_audit.py at baseline SHA; no ZIP2 source staged.
coordination: T4 mouse, T5 resolution/build, T1/T2 water; no shared workflow or Unity resource.
result: Missing m_Texture slot is now represented as a sentinel; missing slot versus removed slot should be distinguishable. Source commit e46c684e; regression d9fc909b; newline correction 41078f20.\nverification: not executed; local runner cannot resolve raw.githubusercontent.com, no duplicate CI launched.\nnext: execute python -m unittest tests.test_t3_material_dependency_pair_audit -v on repository checkout; compare pinned ZIP2 and exported materials only after verified acquisition; investigate shader/alpha for smoke.
