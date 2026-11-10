# T3 scheduled session 20261110T0730Z-T3-scheduled-render-json-integrity-k4m8
origin: scheduled
baseline_sha: f83a40622ce585a0c4fd4ea31431fbbc146f2bba
scope: prompt/coordination/work/RENDER-002/20261110T0730Z-T3-scheduled-render-json-integrity-k4m8.md

## Source and evidence
Read docs/DEVICE_FEEDBACK_42058825739_AR.md, AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md, T_TEAM CHAT_AND_SCHEDULE/PROMPT/OPERATING_MODEL; T3 MEMORY/state and latest earlier known-mismatch sessions. Owner confirms 42058825739 world/save/reentry only; smoke squares, white materials, lighting remain open. Authentic 41 Material/227 TexEnv and 150 RGBA same-export parity from runs 41939404454 and 41940350604 does not prove Android pixel fidelity. Earlier smoke provenance synthetic CI 42728727179 passed 14 tests, not original shader linkage. T4 owns pointer clicks; T5 owns safe-area and resolution.

## Implemented
- Work scope commit 3175d90a92c34d4794b7cc205c36ab27d8dca868.
- Script commit 1828a307695e607a108c80a351d0b217fbceb2d: json.loads object_pairs_hook rejects duplicate fields, parse_constant rejects nonfinite tokens. Prevents silent last-key-wins corruption of original/export render-state summaries.
- Tests commit b54f601bcacb309849bca5a0d41b57c871bcf8cc: duplicate, NaN, and valid summary regression controls.
- Local minimal Python proof: duplicate rejected, NaN rejected, valid singleton accepted. Full repository unittest and CI not run in this session; no claim of passing them.

## Boundaries and next
No proprietary assets published; no Unity/game shader/material modification; no device screenshot test; RENDER-002 OPEN, NOT_READY 0/3. Next: run python -m unittest tests.test_t3_render_state_pair_diff (or discovery) against current branch, then feed SHA-authenticated same-instance original/export state summaries for Particle Renderer smoke into comparator. Check CL new image/log stage and real material/shader pass mapping. Do not repeat prior synthetic CI or full build.
