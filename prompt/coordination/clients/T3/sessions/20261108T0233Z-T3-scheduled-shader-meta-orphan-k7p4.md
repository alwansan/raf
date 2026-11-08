# T3 scheduled session 20261108T0233Z-T3-scheduled-shader-meta-orphan-k7p4
origin=scheduled; status=completed_source_unverified; track=RENDER-002; experiment=T3-META-ORPHAN-20261108

## Evidence and provenance
Owner feedback docs/DEVICE_FEEDBACK_42058825739_AR.md reviewed first; world/save/reopen is owner-confirmed for artifact 42058825739 only. Latest branch HEAD at start 2943340bc784c0358e123c7c2b8e7c75733eb4be. Prior T3 20261108T0133Z-T3-scheduled-material-chain-h7m2 created the read-only Material Shader GUID scanner. Previous authenticated same-instance original/export 41 Material 227 TexEnv/150 colors parity CI41939404454/41940350604 excludes a limited set of losses, not Android rendering.

## Work
Scope first published in commit 990b9a4d1aa9cb3629df274db230206dfa88cbb6. Identified concrete scanner false-positive: orphan .shader.meta GUID alone was counted as a resolved Material Shader even if .shader file did not exist. Updated scripts/t3_material_shader_link_audit.py in commit 1097c94e1eab3c2503c19f72cf51a4913b3f823c to require paired non-symlink .shader source; introduced aggregate shader_meta_without_source count. Added synthetic orphan-versus-paired regression tests/test_t3_material_shader_meta_orphan.py in commit 3582b37347e542607680779ee04c0cb8b8219da5. No proprietary assets or device binaries changed.

## Validation boundary
GitHub connector writes succeeded. Local direct curl/pytest of published source blocked by DNS: raw.githubusercontent.com could not resolve; regression test is written but **not executed**, CI not launched. No Unity, Android, source ZIP2, actual Material tree, screenshots or CL pixels tested this cycle. A paired .shader file is necessary but not sufficient proof of a valid compiled Android variant. No claim of root cause or graphics repair. No other agents' work touched; no build duplicated. RENDER-002 OPEN NOT_READY.

## Resume
Run python -m unittest discover -s tests -p 'test_t3_material_shader_meta_orphan.py' on published source; inspect current HEAD and team work scopes first. Then run read-only scanner on authenticated complete exported Assets+Packages tree and investigate unresolved/orphan categories with renderer/material identity in private logs, especially hand/raft/particle smoke; compare shader keywords/alpha/blend against Android runtime evidence. Do not confuse water FFT floods with proven white hand cause. Keep T4 physical mouse and T5 buttons/Resolution scopes separate.
