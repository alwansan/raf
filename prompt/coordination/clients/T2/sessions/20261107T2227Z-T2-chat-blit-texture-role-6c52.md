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

## CI checkpoint 2026-11-06T22:33:50.966Z
- Source commit [681c239c](https://github.com/alwansan/raf/commit/681c239c29959e420829b48ba24c4ab203ce9ca5): three reserved T2-owned checker, reporter and synthetic test files only. Source producer categories exactly one Texture / RenderTexture / unknown per public explicit Blit site; destination RenderTexture / null / unknown. Unknown is required on noncanonical IL, as tested with synthetic compiler instructions.
- [CI42305522855](https://github.com/alwansan/raf/actions/runs/42305522855) auto-triggered on exact code SHA, original DOTNET synthetic control step had completed SUCCESS, original pin checkout in_progress at checkpoint; do not dispatch duplicate. Work `prompt/coordination/work/WATER-001/20261107T2227Z-T2-chat-blit-texture-role-6c52.json` waiting_ci; experiment `prompt/coordination/experiments/T2/20261107T2227Z-T2-chat-blit-texture-role-6c52.json`.
- No Unity game resource altered or native run requested. Native [42296450023](https://github.com/alwansan/raf/actions/runs/42296450023) still running import at last probe; do not cancel.

## Verified original completion — 2026-11-06T22:35:50.847Z
- [CI42305522855](https://github.com/alwansan/raf/actions/runs/42305522855) **SUCCESS** on [source commit 681c239c](https://github.com/alwansan/raf/commit/681c239c29959e420829b48ba24c4ab203ce9ca5), job 128193753398. 63/63 Python report tests + 6/6 original-name tests + C# Mono.Cecil synthetic selftest; original SHA source reauthenticated in ephemeral CI.
- Exact two original authenticated `Graphics.Blit(Texture,RenderTexture,Material,int)` sites retain pass0=1 and pass1=1. New source-only immediate direct IL producers: source Texture=0, source RenderTexture=1, source unknown=1; destination RenderTexture=1, destination null=0, destination unknown=1. **Aggregates do not associate known source and known destination with each other or with pass=0/1.** Unknown is intentional on noncanonical IL; no fake resource identity.
- Safe aggregate artifact id `13545388075`, 1,376B, SHA256 `b9358da551f1977e71ada7ea2bc84361229719c825070b234167b488b086ab4b`; original code/IL/field identities excluded. No native/editor build requested or game file/GUID edited.
- Detailed report: `docs/T2_ORIGINAL_FOAM_BLIT_RENDER_TEXTURE_ROLES_2026-11-07.md`; collaboration handoff: `prompt/coordination/discussions/WATER-001/20261107T2234Z-T2-chat-blit-rendertexture-roles-to-T1-T5-6c52.md`.
- The direct typed RenderTexture role does not imply actual allocation/RenderTexture content, CB0 layout, Unity ShaderLab import, runtime pass selection, or Android pixels. WATER-001 OPEN, NOT_READY; T2 vote remains `لا يحتاج` (no integrated material/runtime patch).
- status: completed; next_step: Correlate exact direct Texture/RenderTexture source and destination producer categories with original Blit pass literal 0 vs 1 (per-site), without publishing original names/IL. Then investigate unknown producer privately; T5 authorised Unity runtime only.
