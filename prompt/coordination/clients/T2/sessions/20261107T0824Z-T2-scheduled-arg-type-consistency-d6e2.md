# T2 — bounded IL typed argument consistency

- session_id: 20261107T0824Z-T2-scheduled-arg-type-consistency-d6e2
- origin: scheduled
- base_sha: 46a591e780e3ff97f16503052637ecee0bb6f2a9
- owner baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md; owner confirmed world entry/save/re-entry from 42058825739 artifact; water FFT errors remain, publishing failed.
- resumed_from_sessions: 20261107T0716Z-T2-scheduled-stack-hardening-f2a8; 20261107T2227Z-T2-chat-blit-texture-role-6c52 (read as independent original evidence).
- work: prompt/coordination/work/WATER-001/20261107T0824Z-T2-scheduled-arg-type-consistency-d6e2.json registered first in commit b1323a9f509700f1cdf6b872e6658b2934d0cfd9.
- finding: bounded synthetic trace previously allowed the same ldarg index to appear as Texture and RenderTexture in one straight-line block, giving inconsistent typed origin. This is a synthetic model defect, not evidence of such IL in the original game.
- source: scripts/t2_pass1_stack_provenance.py commit 992310903a8e382a48e3ece2206f168ad762bec5; reject contradictory repeated arg typing.
- regression: tests/test_t2_pass1_stack_provenance.py commit e8d0b8932a2ce94d9263843808dc9a986923598c; two cases for conflicting vs consistent repeated typed arguments.
- local test: 2 focused tests PASS in Python 3 using manually reconstructed source; not exact repository checkout, not full unittest suite or CI. No original Mono.Cecil input tested. No Unity or device validation.
- actions snapshot: 42333961072 T3 SUCCESS; 42308935364 evidence summary FAILED (previous known gate). No equivalent native build dispatched.
- status: completed for this narrow source hardening; WATER-001 remains OPEN, NOT_READY. No ShaderLab, game assets, .meta, .rgd, Settings, audio, or deferred touch changed.
- next: run exact repository tests in an isolated checkout/CI; connect the bounded trace to authenticated Mono.Cecil pass1 producers without claiming runtime resource identity; coordinate with T1/T3 on FFT and particle FX.
