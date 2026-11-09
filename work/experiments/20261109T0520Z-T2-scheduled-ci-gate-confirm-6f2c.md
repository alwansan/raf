# T2 WATER-001 — CI evidence checkpoint
session_id: 20261109T0520Z-T2-scheduled-ci-gate-confirm-6f2c
origin: scheduled
baseline_sha: d2c209a98fbb9f41b5f4e466274fba6be1d04265
issue: WATER-001 OPEN
experiment_key: T2-CASE03-POSTPUSH-CI-VERIFY-20261109
files_in_scope: work/experiments/20261109T0520Z-T2-scheduled-ci-gate-confirm-6f2c.md; clients/T2/sessions/20261109T0520Z-T2-scheduled-ci-gate-confirm-6f2c.md
shared_resource: none; no CI dispatch; no Unity build

## Hypothesis
The preceding T2 CASE03 status contradiction regression was published but had not been executed. Check its existing automatic source-only workflow rather than request a duplicate.

## Observed
GitHub Actions [42561294739](https://github.com/alwansan/raf/actions/runs/42561294739), source commit 8fc590191fd8f553d62e36de2c608776d5b6566d, workflow raft-t2-gles-cl-evidence-gate.yml, started 2026-11-09 04:20:37Z, completed 04:20:49Z, conclusion SUCCESS. This closes the prior 'tests not executed' uncertainty for the CI job, but a successful job alone does not demonstrate GPU pixels or original Foam instance alias. Previous original Foam source workflow [42549568993](https://github.com/alwansan/raf/actions/runs/42549568993) reported value_mixed_or_joined.

## Device baseline
Owner run 42058825739 confirmed world enter/save/reopen from artifact; water pass and FFT errors persist. Phone screenshot/log evidence in docs/DEVICE_FEEDBACK_42058825739_AR.md. No inference about shader recovery from this CI.

## Next discriminating work
Implement path-specific source-free return/receiver lineage in android-port/Experiments/T2/FoamBlitOriginalProducers/Program.cs, with synthetic Cecil branch tests, before original SHA-pinned private workflow. Compare pass0 destination vs pass1 source producer identity only inside private scan, fail closed for unknown/alias joins. Then CB0/sampler/render states/ShaderLab and actual device water. T3 effects and T4/T5 mouse/resolution remain distinct scopes. No game/CL/other worker files touched.
