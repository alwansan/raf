# GFX-LAB 20261110-GFX-chat-multi-bounds-source-01

- role: GFX-LAB
- session_id: 20261110-GFX-chat-multi-bounds-source-01
- origin: chat
- resumed_from: 20261110-GFX-chat-multi-six-42712833407
- base_sha: 64a35a88404b387868de081f0e14d1f204d6f4eb
- source_ref: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- experiment_key: gfx-multi-003-source-vertex-bounds
- scope: real source-vertex viewer normalization; write only experiment/android-graphics-rootcause; never edit T team/ZIP2/main.
- runs: GFX-MULTI-001=42711514279 SUCCESS; 002=42712118731 SUCCESS; 003 first=42712833407 FAILURE; 003 second=42714952065 FAILURE; source-only 004=42715492781 SUCCESS.
- evidence: both 003 runs pass original data preparation. First Unity importer M02 returned 0 vertices; second OBJ original fallback produced 1598 vertices/2095 triangles then bounds guard failed. Zero APK artifacts from either run.
- hypothesis: empty/stale Renderer.bounds or micro-unit mesh; test authentic source Mesh vertices, reject genuine degenerate data.
- negative_controls: no synthetic geometry, no Shader48 exact restoration, no animation/100-bone rig restoration, no Android device acceptance for the new M00–M05 package.
- outcome: bounded C# source-vertex fix and workflow preflight submitted; Unity build, signing and device are **not yet verified**.
- next_step: inspect newly triggered workflow; only deliver signed artifact after audit, otherwise diagnose exact first failing phase.
