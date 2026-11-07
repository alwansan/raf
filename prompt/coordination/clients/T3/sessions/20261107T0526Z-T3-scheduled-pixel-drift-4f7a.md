# T3 independent scheduled source-evidence checkpoint

session_id: 20261107T0526Z-T3-scheduled-pixel-drift-4f7a
origin: scheduled
identity: T3
issue: RENDER-002 OPEN / NOT_READY
base_sha: 08bb6820bfa327ab60cf1a9bdb443890b30c5f6a
work_scope_commit: dce13e67a9536ac223745dbdbdc83a5c5eb03691

## Recovery and evidence
Read owner phone feedback first: artifact 42058825739 on POCO F5 Pro confirms enter/save/exit/re-enter only; original square smoke, white hand/raft and lighting defects remain. CL pinned snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57. Do not conflate 23,884 water pass and 3,850 FFT errors (session 220911) with missing textures; their source/phase correlation remains unproven. HUD 18.27 FPS and p95 82.82ms are not GPU timing.

Read AGENTS.md, CURRENT_OWNER_REQUIREMENTS, prompt/STATUS and T_TEAM operating/chat/schedule documents; T3 state/MEMORY are stale relative to independent sessions. Resume both T3 scheduled 20261107T0427Z-T3-scheduled-ci-guard-q6n8 and chat 20261106T2252Z-T3-chat-keyword-routed-61e9. Current branch HEAD at intake 08bb6820bfa327ab60cf1a9bdb443890b30c5f6a. Latest T3 synthetic contract CI 42333961072 succeeded on older source 0e0d02dd. No repeat requested.

## Distinguishing real original-data result (not new run)
T3 real original/export same-instance pixel parity [41968665857](https://github.com/alwansan/raf/actions/runs/41968665857) reached the authentic pixel stage after SHA validation, export, GUID closure and sampler checks: 106 original Texture2D/export PNG pairs; 76 exact; 30 RGB_DRIFT; 0 alpha-only, dimension, orientation, unsupported, unverified-identity categories. This is the strongest **measured unresolved texture fidelity difference**, rather than another synthetic schema edge case. Separate real [41942377246](https://github.com/alwansan/raf/actions/runs/41942377246) verified 25 external + 89 internal selected Material texture pointer occurrences; [41939404454](https://github.com/alwansan/raf/actions/runs/41939404454) verified 227 TexEnv UV slots. Thus blanket claims that white objects prove absent mesh or missing Material PPtrs are unsupported on this bounded scope. Pixel drift may arise from decode/colorspace/premultiply; it is NOT yet a proven cause of any photographed white object.

## Scope and next decisive experiment
Registered distinct scope in work/RENDER-002/20261107T0526Z-T3-scheduled-pixel-drift-4f7a.json before this checkpoint. Do not rerun 41968665857 unchanged. Next compare the **same 30** RGB drift pairs privately by authenticated original Texture2D format, sRGB and alpha flags, exported importer metadata and per-channel difference bins, with 76 exact pairs as negative controls. Verify transformation across all 30 without harming exact 76; publish counts only. If importer metadata is unavailable, report exact absent categories and do not fabricate them. Then link affected exported Texture GUID to original Material→Renderer/ParticleRenderer and screenshot object. Do not change gamma, blend, shaders or textures without original mapping and Unity/phone evidence.

No CI or Unity build launched in this checkpoint; no source asset/scene/.meta/GUID/.rgd/audio/Settings/touch changes. T4 physical mouse and T5 UI/Resolution stay separate. Native owner build and 5/5 vote not altered. No claims of new phone result, visual fix, READY, or Shader48 original RDEF/SPV contract.
