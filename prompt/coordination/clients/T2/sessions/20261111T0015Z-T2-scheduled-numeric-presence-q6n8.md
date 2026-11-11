# T2 scheduled checkpoint 20261111T0015Z-T2-scheduled-numeric-presence-q6n8
origin: scheduled
base_sha: f241710f070baba0a40a8e58177a34f5e1e70f9e
scope_sha: 42014094e26a49c48325767e70a5b7b3ed4b80b7
source_sha: ea6b818b30bb027eda93c0b78e768a354da86b41
resumed_from: prior T2 scheduled producer-contract b4ad216; T2 state 20261108T1956Z-T2-chat-pass1-source-kind-4d6a; previous CI42904487022.
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md, pinned CL 520c4cf; run 42058825739 owner world save/reopen succeeded; delivery publication failed; water/FFT errors persist.
issue: WATER-001 OPEN NOT_READY 0/3.
experiment_key: t2-foam-producer-private-numeric-pair-presence-consistency-v1
files: scripts/t2_foam_texture_identity.py; tests/test_t2_foam_json_product_guard.py; independent work and session files.
result: actual producer compare_private_names now rejects numeric tuple values contradicting m_Index/m_SamplerIndex field_presence, invalid bool, missing, negative or out-of-domain integers. Three synthetic regression tests added for forged presence, malformed numeric domains, and legitimate absent fields. Preserves -1 sampler sentinel as unknown, not a complete pair.
verification: published source with expected_sha no force; source-only tests NOT YET CONFIRMED by CI. Workflow path filters include both changed files. No local full repo checkout due DNS; no CI rerun dispatched.
limits: synthetic test addition is not original asset identity, ShaderLab/CB0 integration, Unity compile, Adreno pixels, or water restoration. Did not touch T3 effects, T4 mouse or T5 resolution.
next: check workflow for source SHA ea6b818; resolve failures without weakening gates. Then trace authentic original Foam RenderTexture pass0/pass1 instance and CB0 material upload; coordinate T3 effects.
