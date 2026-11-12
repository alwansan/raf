# T3 20261112T0028Z-T3-scheduled-parser-guard-m8q2
origin: scheduled
base_sha: 5690818e3b8f245aedd2eeaac04704ac3121d225
resumed_from_session: 20261111T1731Z-T3-scheduled-texenv-parser-r6m2; subsequent T3 commits reviewed via live script and tests
issue_id: RENDER-002
work: work/T3-20261112T0028Z-T3-scheduled-parser-guard-m8q2.md
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md (world enter/save/reopen is device-confirmed only for 42058825739, not shader success)
CL: 520c4cf409aa20a4db54ff80ed87d8807d9cba57; white hand/raft and square smoke remain unresolved
scope: material pair audit; T4 mouse, T5 resolution/buttons/build, T1/T2 water unchanged
changes:
- e46c684e527e34e3b128ba2dffbf629d74fd80a7: preserve explicit missing m_Texture slot in serialized reference comparison
- d9fc909b8d31bd6670d60058ef4465111395f03c: add synthetic missing-vs-removed slot regression
- 41078f20fd3114c494ad8e75ad4b682923e918e2: correct test newline literals
verification: source-level review only. Local runner failed DNS resolution to raw.githubusercontent.com; no tests executed. Do not claim CI PASS.
live_actions: 43127227979 and 43127227972 completed success for other scoped CI; not device evidence.
limitations: no ZIP2/export matched pair staged; no visual root-cause proof; no original assets changed.
next: run python -m unittest tests.test_t3_material_dependency_pair_audit -v, then original-vs-export pair audit on pinned verified trees. Trace renderer->material->shader->texture and particle blend/alpha before gameplay shader edits.
