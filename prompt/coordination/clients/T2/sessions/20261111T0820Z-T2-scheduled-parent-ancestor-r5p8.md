# T2 scheduled session — 20261111T0820Z-T2-scheduled-parent-ancestor-r5p8
origin=scheduled
baseline_sha=f04814ee0403470bebb4c42cdf5df0c82f8cb17a
scope=prompt/coordination/T_TEAM/work/20261111T0820Z-T2-scheduled-parent-ancestor-r5p8.md
source_of_truth=docs/DEVICE_FEEDBACK_42058825739_AR.md; owner confirms world load/save/reopen on artifact from run 42058825739; water pass/FFT errors remain.
previous=T2 session 20261111T0724Z parent-symlink and commit 607a4b77; independent next step.
finding=Immediate parent is_symlink check did not cover an ancestor alias (alias/nested/aggregate.json). This could route output outside the intended directory.
changes=Added _has_symlink_ancestor() in scripts/t2_foam_publish_aggregate.py; added tests/test_t2_foam_parent_ancestor_symlink.py and wired into .github/workflows/raft-t2-foam-evidence-cli-gate.yml.
commits=498a3e71319803a4ad1e20884dfb517c7a739417; f4b8c818a14f2eaaa96eee3b202c89d47fee657e; 801d40b50755cf3b2fa57cf0562a89c14509a24d; 0a2520e1dd1705676b781a65acb7c5332455b3e7
validation=waiting_ci; code and test committed, no claim of passing CI or Android rendering. No full Unity build triggered.
limits=This is a point-in-time symlink check, not a directory-fd atomic defense against concurrent path replacement; the legacy producer integration is still UNKNOWN.
next=Verify workflow result; prioritize authenticated Foam pass0/pass1 RenderTexture identity, CB0 and original ShaderLab binding with T1/T3. Keep mouse/resolution owned by T4/T5 and no touch layout work. WATER-001 OPEN NOT_READY 0/3.
