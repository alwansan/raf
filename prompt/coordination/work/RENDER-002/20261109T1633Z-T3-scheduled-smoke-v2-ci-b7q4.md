# T3 independent scope — 20261109T1633Z-T3-scheduled-smoke-v2-ci-b7q4
origin=scheduled
baseline_head=e2140943fe54afa82d0e2431e97a8f488b48928e
track=RENDER-002
experiment_key=T3-SMOKE-PASS-V2-SOURCE-REGRESSION-20261109
shared_resource=none (small CPU source-only GitHub Actions)

## Hypothesis and evidence
The published smoke Pass/Blend metadata gate and 14 synthetic regressions have not been executed in previous scheduled sessions. Before extracting original ZIP2 smoke Shader48 metadata, validate the gate's executable contract in an isolated inexpensive workflow. The real 17 smoke-named renderers / 34 material slots do not prove shader program/alpha provenance. Previous source/export checks 41939404454 (41 Materials, 227 TexEnv) and 41940350604 (150 colors) disprove selected export texture/UV/tint loss only.

## File ownership and safety
Only new .github/workflows/raft-t3-smoke-pass-v2-regression.yml and this independent work file and new T3 session file. No changes to original assets, .meta/GUID/.rgd, CL, native APK, audio, Settings or other agents' scopes. Workflow trigger only its own file change or manual dispatch, no duplicate builds. Expected branch SHA rechecked before writes, no force.

## Acceptance
Workflow runs Python 3.11 source-only py_compile and unittest for scripts/t3_smoke_pass_state_gate_v2.py and tests/test_t3_smoke_pass_state_gate_v2.py with PYTHONPATH=scripts, with no ZIP2 data. Record run status honestly. Success means synthetic controls only, never authentic smoke/phone parity.
