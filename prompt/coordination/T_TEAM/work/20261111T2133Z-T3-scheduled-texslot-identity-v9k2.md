# T3 scope 20261111T2133Z-T3-scheduled-texslot-identity-v9k2
origin=scheduled
issue_id=RENDER-002
status=source_change_pending_ci
baseline_sha=c670467b7516d875ca3270fdd38846f85550e602
intended_files=scripts/t3_material_dependency_pair_audit.py; tests/test_t3_material_dependency_pair_audit.py; prompt/coordination/T_TEAM/work/20261111T2133Z-T3-scheduled-texslot-identity-v9k2.md; prompt/coordination/clients/T3/sessions/20261111T2133Z-T3-scheduled-texslot-identity-v9k2.md
experiment_key=t3-pair-texenv-slot-identity-negative-control-v1
resource_key=none (source-only Python)
hypothesis=Comparing Counter(texture GUID) misses swapped texture bindings between different m_TexEnvs slots even though shader and texture inventory remain identical. Require slot-key-sensitive comparison with source-free regression.
taken_over_from=prompt/coordination/T_TEAM/work/20261110T1431Z-T3-scheduled-pair-ci-coverage-k8r2.md; scripts/t3_material_dependency_pair_audit.py
No Unity, APK, ZIP2 raw exports, shared build requests or T4/T5 edits. No device claim.

implemented_commits=d6524b1040b7bcbf835e3a756c16223a1f40dcf0; fb1366a3945a5fe80fbb5c61c90ec4794af30f72; c15a71a5496344bcba222e5c7842ea31da6ed579
session=prompt/coordination/clients/T3/sessions/20261111T2133Z-T3-scheduled-texslot-identity-v9k2.md
verification=static review only; synthetic unittest added but not run; no original ZIP2 pair or Android proof
next=execute unittest on checkout; authenticated same-export source/export comparison; investigate material slot swaps if any
