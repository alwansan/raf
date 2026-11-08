# T3 scheduled session — 20261108T2228Z-T3-scheduled-empty-material-z8q3
origin: scheduled
base_sha: 1f61bfdc338cf11072f613593670508242078881
head_at_checkpoint: a4b93f53416437f50cf46251fd5763728caad3dc
scope: RENDER-002 zero-byte material validation
work: prompt/coordination/clients/T3/work/20261108T2228Z-T3-scheduled-empty-material-z8q3.md
resumed_from: 20261108T2131Z-T3-scheduled-orphan-material-m8q4.md; prior T3 chat shared-lab session.
owner_device_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; world/save/re-entry device-confirmed on artifact 42058825739 only.

## Evidence and change
The external particle GUID scanner previously accepted a real but zero-byte .mat when a .mat.meta GUID matched. A zero-byte payload cannot contain Unity Material serialization; this is a false-positive in source coverage, not proof of any device rendering cause.
Scope registered at d8652a7f38e7d632bec71b49625a830d562a1d97.
Source change a5034df9d4c4a9efa50b9edd57a608df81eb6aac adds empty_mat_source and guards material.stat() failures. Regression test a4b93f53416437f50cf46251fd5763728caad3dc verifies zero-byte .mat is not resolved by a matching .mat.meta.
No game assets, original GUID, .rgd, shared testpack or Unity shaders changed. No Unity or shared lab build dispatched. No Android device or image pixel validation claimed.

## Verification and limits
Read source and regression fixture; local GitHub DNS resolution unavailable (git ls-remote: Could not resolve host), so Python test execution is not established in this run. Check existing source-only CI rather than duplicating heavy workflows.
The audit remains an aggregate metadata coverage tool. An absent/empty material in a partial export does not establish absence from the original game; compare with authenticated ZIP2 before assigning a root cause.
Owner phone images show white hand/raft and square smoke per device report, but no material/texture GUID mapping proven this run.
Next: confirm source CI test; apply scanners to pinned authentic exported prefabs and material tree, follow shader/texture/keywords/alpha and compare specific screenshot regions. RENDER-002 OPEN NOT_READY; full XAPK 0/3.
