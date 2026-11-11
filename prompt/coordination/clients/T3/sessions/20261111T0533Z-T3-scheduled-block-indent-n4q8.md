# T3 scheduled session — 20261111T0533Z-T3-scheduled-block-indent-n4q8
origin=scheduled
identity=T3
issue=RENDER-002 OPEN; NOT_READY 0/3
baseline_sha=d2d4691a890caa08576d1087c5d73d7720f13f39
scope_commit=6455961bf5cb0301f6529a05cae19217dedf9cc8
code_commit=d21427e88983b313d1d035c3d2d18600759d243d
test_commit=fd59b18bc6919a92d059f21f3dbf8aa012d0521c
experiment_key=T3-PARTICLE-BLOCK-INDENT-004
resumed_from=20261111T0434Z-T3-scheduled-flow-separator-p8r2
owner_report=docs/DEVICE_FEEDBACK_42058825739_AR.md
cl_source=alwansan/CL@520c4cf409aa20a4db54ff80ed87d8807d9cba57
work=prompt/coordination/clients/T3/work/20261111T0533Z-T3-scheduled-block-indent-n4q8.md

## Finding
The block-style YAML parser in scripts/t3_particle_material_chain_audit.py counted any subsequent dash-prefixed line, even if belonging to a sibling field rather than m_Materials. This could inflate the particle renderer material census and misdirect smoke investigation. Added indentation boundary to stop at sibling lists, preserving nested material entries. Added two synthetic regression tests for sibling exclusion and nested material inclusion.

## Verification limits
Source changes published and fetched back; regression tests not executed (container network cannot resolve github.com). No original ZIP2/export pair inspected, no phone test, no actual visual restoration. No CI or Unity build requested. Existing successful world save/re-entry is only established for 42058825739; 2026-11-05 screenshots show unresolved square smoke and white materials.

## Next
Run: python3 -m unittest discover -s scripts/tests -p 'test_t3_particle_material_chain_audit.py' -v. Then run audit on pinned ZIP2 and verified export and correlate material GUID hashes with ParticleSystemRenderer/Shader/Texture/blend states. Review current HEAD before any further edits. Keep T4 mouse and T5 Resolution scope untouched.
