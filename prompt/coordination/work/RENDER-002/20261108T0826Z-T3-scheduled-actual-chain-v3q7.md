# T3 RENDER-002 — actual-chain checkpoint
session_id: 20261108T0826Z-T3-scheduled-v3q7
origin: scheduled
status: active_read_only_diagnostic
base_head: 1ff89759b73d7e0f51111d2ceb5630182cfc07e2
experiment_key: T3-RENDER-002-actual-particle-material-chain-v3q7
shared_resource: none (no CI, Unity, native build, source asset mutation)
owned_files: this work file and matching clients/T3/sessions entry only

## Hypothesis and evidence
Owner's 2026-11-05 artifact 42058825739 is confirmed playable for world enter/save/exit/re-enter, but packaging failed. Device feedback lists four immutable CL screenshots and three log sessions; white hand/raft and square smoke have not been mapped to actual prefab/ParticleSystemRenderer/Material/Shader/texture. Real same-export 41-material checks at runs 41939404454 (227 TexEnv) and 41940350604 (150 RGBA slots) ruled out selected internal pointer/UV and color export loss, not external texture dependencies or GPU shader variants. Water FFT errors are separate evidence, not proof of square-smoke root cause.

## Next decisive experiment (not yet executed)
Use SHA-pinned ZIP2 input, identify the actual prefab/renderer for square smoke and white hand/raft from authenticated exported scene/component references; follow Material PPtr to Shader source/variant and texture import alpha, then inspect Blend Src/Dst, ZWrite, AlphaClip and particle vertex color. Compare original and Android material/shader bindings on same exact objects; report aggregate identities without publishing proprietary assets. Reject dummy and missing-source shaders. Do not change game assets before exact chain and evidence. Coordinate with T1/T2 for shader, T4 mouse, T5 resolution and buttons. Run published Python audit tests before using their counts as evidence.

## Blocker
Current tool runtime cannot resolve github.com from container (git ls-remote DNS failure); GitHub connector can read and write, but not execute Python against repo checkout. No authentic original export or CL pixel image was locally processed in this checkpoint. RENDER-002 OPEN / NOT_READY.
