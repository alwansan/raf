# T2 WATER-001 — isolate synthetic report mutation

session_id: 20261109T1818Z-T2-scheduled-r7q2
origin: scheduled
baseline_sha: ae9b5c5be4e5c0001ab47575807dd599ee6e3d26
experiment_key: T2-FOAM-REPORT-MUTATION-ISOLATION
scope: tests/test_t2_foam_resource_abi.py; this work record and clients/T2/sessions/20261109T1818Z-T2-scheduled-r7q2.md
shared_resource: none; no Unity/CI manual dispatch

## Evidence and hypothesis
Owner device run 42058825739 proves local world save/reentry, not water. WATER-001 remains NOT_READY. Latest CI run 42664209077 failed four subtests of test_tampered_source_table_types_and_extra_fields_fail_closed, all with ValueError from combine() before expected verify() check. The test's combine() returns the same original table_rows dict, and a prior subtest mutates it in place; later iterations start with contaminated profile. Isolate each report table dict before mutation, preserving the production fail-closed validation. This is a test fixture defect, not a reason to weaken source metadata guards.

## Acceptance
Source-free unittest passes; original resource verification stays fail-closed; no private assets or shader changes. Avoid duplicate native/Unity runs. Next: verify workflow and continue authentic Foam texture identity.
