# T3 scheduled session — 20261111T0231Z-T3-scheduled-smoke-links-c9v2

- identity=T3; origin=scheduled; issue=RENDER-002 OPEN; NOT_READY 0/3.
- resumed_from_sessions=20261111T0127Z-T3-scheduled-guid-ambiguity-v6p4;20261111T0033Z-T3-scheduled-smoke-chain-m6q2.
- base_sha=ef8a01ff22bdc237ac1b885f59b3d1abf0b1f912; scope commit=4e1a7b6ee72cabab44e08ff67de2cb944fa95a32.
- Owner report read first: docs/DEVICE_FEEDBACK_42058825739_AR.md, CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57. Artifact 42058825739 confirms world entry/save/reentry, not graphics repair. Square smoke, white hand/raft and light defects remain open.
- AGENTS.md and owner requirements checked; T_TEAM CHAT_AND_SCHEDULE reviewed. Latest accessible Actions 42946063315 and 42946063270 both completed success, source SHA 5dd745975089b10bc02c18cb51636506c054b063; not a device validation.
- New isolated read-only script scripts/t3_particle_material_chain_audit.py identifies Unity YAML class 199 ParticleSystemRenderer and its m_Materials inline GUID references, classifies null/local/external slots and reports SHA256 prefixes, optionally salted. No game assets or GUIDs published.
- commits: e38b3803b5108ed53e0c370f80c486fec8b1449d initial; 9ef93311253d658b05944aab5f554bdf4fa5c167 regex escape correction; 247e5f6d9f61023247f6f59e15d4674a88e61ef0 documentation clarification.
- Validation: no execution of new script, no authentic ZIP2 export pair available in this connector run; diagnostic code is UNTESTED. No Unity/CI build launched, no phone GPU or material-shader chain proven. This is a structural audit instrument only. No .meta/GUID/.rgd/scenes touched.
- Next: run Python synthetic prefab test against script; inspect original ZIP2 pinned 15964ea8 and actual export tree, compare particle material hashes and inspect Material Shader/Texture/Blend/Alpha/ZWrite, then make evidence-driven fix. Coordinate T1/T2 fire, T4 mouse, T5 resolution separately.
- work file prompt/coordination/clients/T3/work/20261111T0231Z-T3-scheduled-smoke-links-c9v2.md; resource_key=none; experiment_key=T3-PARTICLE-MATERIAL-LINK-STATIC-001.
