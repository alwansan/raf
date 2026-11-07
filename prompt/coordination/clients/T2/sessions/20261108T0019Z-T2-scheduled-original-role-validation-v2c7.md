# T2 — verified per-pass original Foam evidence reconciliation

- session_id: 20261108T0019Z-T2-scheduled-original-role-validation-v2c7
- origin: scheduled
- base_sha: 5fa3fc5f3deb5d13d71573df2aee365b70afa615
- resumed_from_sessions: 20261107T2227Z-T2-chat-blit-texture-role-6c52; 20261107T2221Z-T2-scheduled-original-pass-role-reconcile-m8q4
- issue_id: WATER-001; status: completed (evidence reconciliation only)

## Owner/device baseline
Owner's 2026-11-05 phone test on native run 42058825739 succeeded in entering, saving, exiting and re-entering the world from Artifact. Package publishing failed. CL session 220911-559 had 23,884 water pass and 3,850 FFT kernel errors; 230108-327 had 39,132 and 6,026 respectively. No claim of water pixels fixed. New physical mouse/three buttons/resolution instructions are live; touch layout remains deferred.

## Live evidence reconciliation
- HEAD before scope: 5fa3fc5f3deb5d13d71573df2aee365b70afa615 (T1 scheduled FFT budget). Scope committed as aed1abc158294e69b466632ec22a93048b5c7b85.
- The report docs/T2_ORIGINAL_FOAM_BLIT_RENDER_TEXTURE_ROLES_2026-11-07.md contains an **appended later verified same-site correlation** absent from its initial aggregate section. CI 42308583977 SUCCESS at code 4e5f4d24; 65/65 report tests, 6/6 source-name tests and Mono.Cecil selftest. Authentic source rehashed in ephemeral CI.
- **Pass 0:** direct source RenderTexture and direct destination RenderTexture, same exact original field-read site. **Pass 1:** direct source unknown and direct destination unknown, same-site correlation. This supersedes the older aggregate-only limitation and must not be relabelled as unresolved per-pass association.
- Unknown Pass 1 producers are not proof of null/missing textures or a failed draw. Pass 0 type is not proof of object identity, allocation, CB0 upload, shader import, or Android rendering. Source report was previously published; no need to rerun equivalent CI.
- Checked Actions live at this checkpoint: zero in_progress and zero queued on feature/android-native-port. Latest observed source CI 42423764756 T1 success. Recent releases include LogRaft builds; do not treat them as Raft Android native releases. CL fixed report links are the owner baseline; no new phone observation.

## Non-overlap and next step
No source, shader, meta, game assets, workflow or T3 files edited; no CI dispatched. Current chat T2 already owns Program.cs and the Foam shaderfind reporter. This scheduled cycle resolved contradictory historical summary wording by checking the appended original report. Next independent useful scope: inspect original pass-1 IL producer chain in a bounded source-authenticated private experiment, preserve unknown on computed calls and publish sanitized classification only; compare CB0 stage lengths before ShaderLab patch. Coordinate with T1 FFT and T3 effects/materials. Preserve Settings/audio and all input behavior. WATER-001 OPEN, NOT_READY; no trial build vote change.
