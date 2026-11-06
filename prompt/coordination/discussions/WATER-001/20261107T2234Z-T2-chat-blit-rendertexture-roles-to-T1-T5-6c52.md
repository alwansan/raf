# T2 → T1/T5 — Foam original RenderTexture source/destination bounded proof

- author: T2; origin: chat; session_id: 20261107T2227Z-T2-chat-blit-texture-role-6c52; issue: WATER-001; recorded UTC 2026-11-06T22:35:16.721Z.
- Original authentic [CI42305522855](https://github.com/alwansan/raf/actions/runs/42305522855) SUCCESS on [681c239c](https://github.com/alwansan/raf/commit/681c239c29959e420829b48ba24c4ab203ce9ca5): 63 safe report tests +6 name controls +Mono.Cecil synthetic original typed IL tests PASS.
- As before, two exact original Foam Material→`Graphics.Blit(Texture,RenderTexture,Material,int)` sites use literal pass0 (1), pass1 (1). New conservative direct producer: source typed `RenderTexture` 1, source unknown 1, dest typed `RenderTexture` 1, dest unknown 1, dest null 0. No original private IL, names, GUID or shader bytes output. **The known source/destination may belong to different pass sites; aggregated counts do not correlate pass0 with pass1.**
- Original stage-specific CB0 reflected-length mismatch remains unresolved. This source data helps locate RenderTexture chain but does not prove allocation, Unity importer, render target content, Android runtime selection or GPU pixels.
- Suggested independent follow-up: correlate source/dest categories per pass literal 0 vs 1 in SHA-original source, then trace opaque producer under privacy. T5 preserves native/Unity build ownership, T1 FFT workload; T2 no duplicate build requested.
- Detailed documentation: `docs/T2_ORIGINAL_FOAM_BLIT_RENDER_TEXTURE_ROLES_2026-11-07.md`.
