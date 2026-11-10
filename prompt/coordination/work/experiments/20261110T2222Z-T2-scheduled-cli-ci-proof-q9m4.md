# T2 WATER-001 — verified CLI UTF-8 regression
session_id: 20261110T2222Z-T2-scheduled-cli-ci-proof-q9m4
origin: scheduled
baseline_sha: 897904d2c2e1de9cdb938ac48a6995d27e9410f7
experiment_key: T2-FOAM-CLI-UTF8-CI-20261110
scope: evidence-only verification of tests/test_t2_foam_evidence_cli_integration.py and .github/workflows/raft-t2-foam-evidence-cli-gate.yml; no changes to shared files or original game assets.
hypothesis: The corrected invalid-octet fixture in ce6e0d55456daa57b9b3bcc3907c91b6d062d53b executes successfully in its dedicated CI gate.
result: CONFIRMED source-only gate success at https://github.com/alwansan/raf/actions/runs/42904487022 ; head_sha ce6e0d55456daa57b9b3bcc3907c91b6d062d53b; completed success; created 2026-11-10T21:22:56Z. Prior run 42884997890 success on 849ee582; new result covers changed fixture.
producer_integration: UNKNOWN. Workflow explicitly prints publisher_integration=UNKNOWN. No verified invocation of sanitizer from real report producer or artifact uploader; CLI acceptance does not certify report provenance.
shared_resource: none; no CI launched; no workflow edited.
next: identify actual report producer/upload step; add a fail-closed sanitizer call at that boundary and prove end-to-end output isolation, then resume Foam pass1 source RenderTexture identity, CB0 and ShaderLab. Preserve T3/T4/T5 scope and 42058825739 device evidence.
