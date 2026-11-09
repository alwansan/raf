# Session 20261109-GFX-chat-bootstrap-9b89
- **role:** GFX-LAB
- **origin:** chat
- **session_id:** 20261109-GFX-chat-bootstrap-9b89
- **resumed_from:** none — first branch bootstrap
- **base_ref:** main@9b89f62772c2c61f6269fd2249f8560af1522892
- **branch:** experiment/android-graphics-rootcause
- **source_reviewed:** feature/android-native-port; HEAD observed 4afd9cc4d59a1119e9f10a2d46687b1a62bd0d08 (may advance)
- **issue_id:** RENDER-002 / WATER-001
- **scope:** Read-only source-backed triage of white models, fire, smoke, lighting and FFT; create isolated main-derived diagnostics branch, restore protocol, memory and experiment roadmap.
- **experiment_key:** gfx-lab-20261109-source-docs-phone89-dummyshader-postrestorer-triage-v1
- **resource_key:** none (no Unity or LFS resource reserved)
- **status:** completed_initial_evidence_synthesis
- **code/build:** no Raft shader, no APK/XAPK/OBB, no Unity import, no runner source download, no repair claim.

## Evidence
- 42058825739 reconstructed real Android export. Postrestorer T3 reported 110/142 Dummy ShaderLab and 770/1536 Material docs linked; materials' GUIDs were not broken. It completed game build despite `errors=11`, release 403.
- Owner APK89 world enter/save/reenter observed; images still white hand/raft, square effect. LogRaft 220911/230108 showed water passes 23884/39132 and FFT kernel errors 3850/6026.
- Original game contains 1556 Materials,165 Shader,4050 textures; original Linear; selected original/export 41 Materials color/UV values and 106 textures did not lose semantics in isolated checks.
- T3 smoke34 exact source-to-same-export result Dummy; alpha-dependent Blend, ColorMask RGB, ZWrite Off. DXBC stages can translate privately but semantic IO mapping and actual phone pixel remain unresolved.
- T1 compute/water traces and source-only tools cannot be promoted into full game water/Adreno acceptance.
- Bounded CL log OBB patch.89 warnings are not main.89 failure evidence.

## Rejected explanations / caution
- Not enough evidence that all colors are lost due to Gamma or universally corrupted textures.
- Not enough evidence that main OBB is corrupt; 3 actual warnings were patch.89.
- Successful compiled synthetic test/Unity OpenGLCore is not proof of shader fidelity or Android water.
- No link yet from exact native white raft/hand renderer to the 110 Dummy shader files.

## Artifacts of this lab
- `AGENTS.md`, `prompt/graphics-lab/RESTORE_AR.md`, `prompt/graphics-lab/PROTOCOL_AR.md`
- `docs/ROOT_CAUSE_REVIEW_AR.md`, `docs/EXPERIMENT_ROADMAP_AR.md`
- `memory/MEMORY.md`, `memory/STATE.json`, this session, `experiments/20261109-GFX-chat-bootstrap-9b89.json`

## Next
1. Read latest T3 native Shader authenticity tools and check for newer exact 921↔native GUID outcome.
2. Record scoped GFX-01 read-only cross-version comparison; no CI duplication. Ask T3/T5 to reuse next native already-authorized preimport scan if needed; no own full APK.
3. Where exact Shader identity is proven, compare original Pass variants+CB/sampler with Unity imported shader and only then candidate patch within this branch.
