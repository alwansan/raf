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
