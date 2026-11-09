# T3 chat — authentic Particle108 GameObject emitter semantic linkage

- session_id: `20261109T0150Z-T3-chat-particle-emitter-3p7k`
- **origin:** `chat`
- issue: `RENDER-002` / open; original game still NOT_READY.
- resumed_from_session(s): `20261109T0142Z-T3-chat-cl-raw-png-ci-p8r4`, `20261108T1733Z-T3-scheduled-local-material-resolve-n5q8`, `20261106T1337Z-T3-chat-particle108-propstate-62fb`.
- **base_sha** before scope: `80d128223fbe79bb27305bba9efdf2304ffd1df5`
- Reservation commit: `ee598ff20f51de8afc898b53a379a5f23469c104`.
- Work scope: `prompt/coordination/work/RENDER-002/T3-20261109T0150Z-T3-chat-particle-emitter-3p7k.json`; owner T3 only, active then.
- Intended files: `scripts/t3_original_particle_emitter_semantics.py`, `tests/test_t3_original_particle_emitter_semantics.py`, `.github/workflows/raft-t3-original-particle-emitter-semantics.yml`, own work/session/experiment/event/docs.
- Experiment key: `t3-original-six-scene-original-particle108-emitter-gameobject-name-link:ZIP2@15964ea8:SHA-six-scenes-four-owners:gameobject-hierarchy-v1`.
- Scope check: T3 scheduled recent scope is PNG decoder/tests, *not* this original source GameObject bridge. T1/T2 water and FFT, T4 input, T5 native build unaffected. Original ZIP2 external provider source read only. No shared Unity or mini APK build dispatched.

## Source-backed reason
- Prior actual original source verified an anonymous highest-use Particle Shader48 at **108 original material slots** on **54 original ParticleSystemRenderers**, 5 Material21 objects and 3 Texture2D targets; exact source→same-export 5 Material RGBA (15), Float32 (145), texture UV (10) values matched CI42243130856. Its actual post-vendor ShaderLab remained `DummyShaderTextExporter` (CI42223071341). Original program and property semantics incomplete, *not proven the in-game phone smoke-square emitter*.
- Prior R3 synthetic lab six PNG pixels nonblack proved by [CI42547145230](https://github.com/alwansan/raf/actions/runs/42547145230), not actual game. The owner 5 November photos at `docs/DEVICE_FEEDBACK_42058825739_AR.md` still show square smoke, white hand/raft.
- New hypothesis: a **source-scene GameObject name semantic association** for the 108-use shader can prioritize or falsify an assumed smoke-like name assignment. Names are weak hints, not direct emitter mapping or device proof.

## Implemented
- Source class 199 scene ParticleSystemRenderer -> m_Materials -> SHA-pinned actual Material21 -> authenticated selected shader target's 5 Material identities -> local m_GameObject (class 1) -> m_Name, **private in runner**.
- Aggregates fixed generic `smoke_like/fire_like/water_like` name-hint categories for selected vs other scene particle renderers; original name/GUID/PathID/per-scene graph never printed, uploaded, or stored.
- Strict source six scene, four owner SHA and original 108/54/5 invariants, fail-closed negative pointer schema, source-free tests before heavy stage.
- Implementation commit `05d11ec7dc20c81d8e7b3a0249d493b6f6ecdbc4`; tests `ff593f8ad452082fe44de65e10893372aafdf050`, corrected test fixture `8d32770cd3f4255a353236cb9590f85d9bc9d303`; new isolated runner workflow `f359f8201fc83f2a8b83a12a23d0eb4b00277827`.
- GitHub Actions run: [42548587534](https://github.com/alwansan/raf/actions/runs/42548587534) (queued at first observation). 28-minute timeout, ubuntu-24.04, cancel-in-progress=false, no original raw files in artifact.
- **Verification pending:** do not mark synthetic tests or genuine ZIP2 source scan PASS until exact run outcomes examined.

## Continuation
Check the run's synthetic controls, SHA stage and original scan, record safe category counts or exact failure stage without leaking private names; address only independent code failure and rerun if needed. Then investigate verified original emitter-to-phone screenshot evidence, not scene source name guessing. Do not install dummy shader or claim game/Adreno repair.

## End-of-cycle authenticated results — 2026-11-09 02:09 UTC
- First synthetic run [42548587534](https://github.com/alwansan/raf/actions/runs/42548587534) FAILED due to a T3 `safe_aggregate` dictionary key typo (not original source failure). Fixed on commit `55274187f98752aa59b9f20e0df18e0812a74e2d`; changed own workflow to accept own script/test changes `04f57031887c35dc4889a2f204e90e885c19dc86`.
- Original run [42548776129](https://github.com/alwansan/raf/actions/runs/42548776129): original source was SHA-verified and emitted safe counts, but **report formatting failed** because workflow expected `selected_renderer_objects` key; corrected at `b97c07be6a6eef20cc894025ae59624cfa06b9be`. Do not label run SUCCESS.
- [**42548907189 SUCCESS**](https://github.com/alwansan/raf/actions/runs/42548907189): all six synthetic source controls PASS, six original scenes SHA authentic, four original shader/material owner SHA authentic, actual UnityPy Renderer→Material→GameObject semantics PASS, 108 exact source slots / 54 renderers selected with 25 fire-like, 0 smoke-like; other 56 renderers with 17 smoke-like and 17 fire-like, all 110 GameObject names resolved. Safe Artifact `13644781433`.
- Registered **phase 2** before modifying owned source: independently cross-correlated original semantic hints to each private original Shader48 identity, not merely equal total usage ranks. Code commit `54babb69efa3774d94e545aa3fe6673408559d09`.
- [**42549246777 SUCCESS**](https://github.com/alwansan/raf/actions/runs/42549246777) real original 6-scene/four-owner source and **215 particle Shader48 typed Material slots** rejoined. All 17 smoke-like GameObjects use exactly **one distinct source Shader48 with 34 original particle Material slots** (17 renderers, 34 slots). Fire-like names: 25 renderers × 2 = 50 slots on original **108-use Shader48**, and separate 17 × 2 = 34 slots on **another distinct 34-use Shader48**. The two 34-use shader source identities are provably different inside the private original graph, though both public ranks equal 34. Safe Artifact `13645145119`. No raw names, original shader code, GUID or PathID printed.
- New source-free [**42549491342 SUCCESS**](https://github.com/alwansan/raf/actions/runs/42549491342) tests `tests/test_t3_original_particle_smoke_rank.py` verify that equal 34 ranks are **not merged**, per-renderer counting deduplicates two material slots, invalid keys/excess counts fail closed, private identities are not emitted. Source-only CPU; no repeat authentic original source staging in this small test.
- Permanent engineering report: [docs/T3_ORIGINAL_PARTICLE_SMOKE_SHADER_RANK_2026-11-09.md](../../../../docs/T3_ORIGINAL_PARTICLE_SMOKE_SHADER_RANK_2026-11-09.md), experiment `prompt/coordination/experiments/T3/20261109T0150Z-T3-chat-particle-emitter-3p7k.json`, event `prompt/coordination/B_TEAM/events/T3/20261109T0150Z-T3-chat-particle-emitter-3p7k.json`.
- **Crucial boundary:** This is genuine original `ParticleSystemRenderer` + material + shader linkage, but words like smoke/fire in `m_Name` **do not establish** that a particular original emitter is the phone's square effect or that any compiled Android shader renders it. The 108-use original shader still has previous *postvendor dummy* evidence, but this does **not** transfer to the distinct 34-use smoke candidate. No game asset/code/.meta/OBB/XAPK/mini modified; no Android device testing or user PASS claimed.
- **Next exact engineering:** privately select original 34-use smoke-linked Shader48 in same SHA-original graph, audit its real `m_ParsedForm` Pass/Blend/alpha and actual same-export ShaderLab dummy/program/keyword identity. Then compare the identified shader and its bound Texture2D/Material in actual Android Unity build and owner in-game screenshot before attempting restoration. RENDER-002 OPEN/NOT_READY 0/3.
- **Work result:** source scope complete, resource released; ongoing scheduled T3 PNG script/test files not modified, T1/T2/T4/T5 jobs not interrupted.
