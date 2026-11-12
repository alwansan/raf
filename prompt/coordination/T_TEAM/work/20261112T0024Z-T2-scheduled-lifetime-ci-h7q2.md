# T2 work 20261112T0024Z-T2-scheduled-lifetime-ci-h7q2
origin: scheduled
baseline_sha: e58cf4ea3dccf3b2fbe390f768abe267a14da32b
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md
scope: .github/workflows/raft-t2-foam-runtime-rt-contract.yml; T2-only work/session files
hypothesis: The existing source-only CI contract runs the RT pair parser tests but omits the newer RT lifetime gate regressions. Extend the same lightweight T2 workflow, not a duplicate workflow.
experiment_key: T2-WATER001-RT-LIFETIME-CI-20261112
shared_resource: GitHub Actions Ubuntu 24.04, source-only, 5 minute timeout; no Unity/ZIP2/OBB
conflicts: No T3/T4/T5 code edited; no native build; no running equivalent lifetime CI found among latest runs inspected.
limits: This is Python validation only. Real Unity capture producer, original shader provenance, CB0/ShaderLab and device water pixels remain unverified.
