# 20261111T1230Z-T3-scheduled-shader-owner-p6x8
origin=scheduled
Issue RENDER-002; branch feature/android-native-port.
Owner device baseline: 42058825739 world/save/reopen passed; rendering defects remain (white hand/raft, square smoke). This is not a new device result.
Read: docs/DEVICE_FEEDBACK_42058825739_AR.md, AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md and T_TEAM protocol. Coordinated: no T4/T5 or T1/T2 files touched.
Scope: prompt/coordination/clients/T3/work/20261111T1230Z-T3-scheduled-shader-owner-p6x8.md; experiment T3-SHADER-OWNER-TYPE-20261111.
Commits: scope 2d212c06d47f9f657b399e697fbf66623438a34d; implementation 1affe37fb4595cb1128ffe80364c23a95d5c3490, duplicate-preservation fix a95acf211954b4de0a42c52df3594afd47df8ba8; synthetic tests 881caf128055ffd7f4b96374d33fbaa4f88c5415.
Finding: existing material-to-shader audit counted ANY unique GUID owner .meta as a shader. Now classifies unique non-.shader owner separately; keeps distinct path entries for duplicate GUID detection. Extension is heuristic, not proof of actual Unity shader import (ShaderGraph may differ).
Verification: source reviewed; tests committed but NOT executed. Local curl could not resolve raw.githubusercontent.com; no successful CI claimed. No ZIP2 comparison, shader reconstruction, Android test, or visual fix.
Next: run python -m unittest discover -s tests -p 'test_t3_shader_owner_type.py' -v on checked out branch; inspect live CI and authentic original/export GUID chains and shader/texture bindings; extend ShaderGraph recognition after evidence. Do not treat static counts as pixels. No shared workflow dispatched.
