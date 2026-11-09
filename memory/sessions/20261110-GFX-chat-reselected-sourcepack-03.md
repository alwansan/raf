# GFX-LAB — 20261110-GFX-chat-reselected-sourcepack-03
- session_id: 20261110-GFX-chat-reselected-sourcepack-03
- origin: chat
- resumed_from: 20261110-GFX-chat-multi-source-geometry-02
- base_sha: b21b16c6f9937060a64ce7b3835d867cd576b7bd
- experiment_key: gfx-multi-reselected-sourcepack-and-shader-audit
- scope: source-only GFX-MULTI-002/004 validations for new SHA-pinned float32-valid six model arrangement, no full game or T-Team edits.
- ZIP2 source: 15964ea8f246b6e076ce26b60931ee2e1a9a2385
- runs: historical 001=42711514279 success; old 002=42712118731 success; 003=42712833407,42714952065,42718266273 failures; old shader-only 004=42715492781 success; **new 001=42719663373 source-only SUCCESS**. GFX-MULTI-002 **42720399689 SUCCESS** (6 Mesh, 7 original materials, 21 images, 15 source stream parts /707,788,800 bytes). GFX-MULTI-004 **42720400057 SUCCESS** (one original Shader48 common across 7 material slots, 2 SubShaders /7 Passes; no real Android original shader restoration).
- evidence: SHA-original source locked; 1,973 renderer-mesh references and 824 material-shader chains; new filter rejects 12 source OBJ candidates with impossible real float32 spatial extent. Current M00 Shears375; M01 person5095/100bones; M02 tool1666/8bones; M03 multi_material2163/2slots; M04 skinned-unidentified2445/100bones; M05 skinned-generic4452/2bones.
- source pack: 7 materials, 21 texture roles expected, NOT yet verified by new source pack.
- negative_controls: no public OBJ/PNG/PPtr/GUID; no real original shader parity, no original rig animation, no Android six-model APK, no owner visual acceptance for these five.
- intended experiment: rerun GFX-MULTI-002 with exact 6/7/21 authenticated decode; rerun GFX-MULTI-004 topology for new selections; abort on mismatch. Only then consider full Unity Android.
- result: source selection PASS 42719663373; source pack/shader 004 CI outcomes **not yet known at authoring**.

- source_only_final: 001 new selector/002 decode/004 original shader topology all PASS; signed Android build and owner device remain NOT_PROVEN.
