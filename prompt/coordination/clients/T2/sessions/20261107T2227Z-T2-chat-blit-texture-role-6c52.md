# T2 — original Foam Blit Texture/RenderTexture producer roles

- session_id: 20261107T2227Z-T2-chat-blit-texture-role-6c52
- origin: chat; status: active; issue_id: WATER-001
- base_sha: ebc78f1c3f561433666d6355c45cc90edaad03fb; updated_at: 2026-11-06T22:27:17.820Z
- resumed_from_sessions: 20261106T2217Z-T2-chat-blit-pass-literal-2c9e, 20261106T2218Z-T2-scheduled-blit-pass-provenance-q8f3
- owner-native: https://github.com/alwansan/raf/actions/runs/42296450023 (in_progress Unity import; do not cancel/duplicate).
- prior source proof: https://github.com/alwansan/raf/actions/runs/42303756960 SUCCESS; 2 exact original `Graphics.Blit(Texture,RenderTexture,Material,int)`, pass0=1, pass1=1; no proof of original RenderTexture identities, CB0 host upload, real Unity assets or pixels.
- scheduled T2 `20261106T2218Z-T2-scheduled-blit-pass-provenance-q8f3` completed independent read-only reconciliation; no overlap with proposed code. Other workers' current GH Actions inspected.
- hypothesis: bounded backward immediate IL expression inspection before the exact Material field load can prove some source/dest typed producers without claiming runtime texture identity; complicated receiver/call chains must remain unknown.
- declared scope: `android-port/Experiments/T2/FoamShaderFindResultFlow/Program.cs`, `scripts/t2_foam_shaderfind_return_report.py`, `tests/test_t2_foam_shaderfind_return_report.py`; existing source-only workflow `.github/workflows/raft-t2-foam-original-shaderfind-resultflow.yml` path-trigger; no new native run.
- experiment_key: T2-ZIP2SHA-original-Foam-Blit0-1-immediate-srcdst-direct-expression-v1
- resource_key: T2 SHA-authentic original Mono.Cecil source-only workflow; no Unity native runner
- next_step: Implement strict no-branch direct IL operand producer classification for source and destination of exact authentic Foam Blit pass sites; source-free synthetic negative/positive tests, original pinned managed DLL workflow. Preserve unknown when not direct, no Unity/pixel claims.
