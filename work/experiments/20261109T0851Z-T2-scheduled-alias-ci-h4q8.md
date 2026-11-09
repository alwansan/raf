# T2 independent scope — Foam alias regression execution
session_id: 20261109T0851Z-T2-scheduled-alias-ci-h4q8
origin: scheduled
baseline_sha: bbb454fbb81e70f7e3f8476daddad0b5b1deecf3
issue: WATER-001 OPEN
hypothesis: The existing source-free alias fixture was never executed by the successful platform-tests workflow; a dedicated lightweight CI gate is needed before treating its eight cases as CI-verified.
files: .github/workflows/t2-foam-alias-reference.yml; work/experiments/20261109T0851Z-T2-scheduled-alias-ci-h4q8.md; clients/T2/sessions/20261109T0851Z-T2-scheduled-alias-ci-h4q8.md
experiment_key: T2-FOAM-ALIAS-CI-20261109
shared_resource: none; ubuntu lightweight, no Unity/ZIP2/CL/game assets.
Evidence: 42579832093 succeeded on cc85cb65, but platform-tests steps do not invoke alias_identity_reference_test.py. This is a coverage gap, not a failed test.
Owner device feedback: 42058825739 world entry/save/re-entry confirmed; water errors remain. T3 effects, T4 mouse, T5 resolution untouched.
Acceptance: CI explicitly runs python3 -m unittest android-port/Experiments/T2/alias_identity_reference_test.py; fail on nonzero; source-free gate only. No claim of original Foam alias, shader integration or device validation.
