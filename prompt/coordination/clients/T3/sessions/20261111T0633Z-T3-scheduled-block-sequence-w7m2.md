# T3 scheduled session — 20261111T0633Z-T3-scheduled-block-sequence-w7m2
origin=scheduled
issue=RENDER-002
baseline=5fcddeb967dd2120b27eb0762af5f277c5819441
head_after_changes=d8e1fe1ccb9656f5ff123c119ecc5ffe51f9d975
work=prompt/coordination/work/RENDER-002/T3-20261111T0633Z-T3-scheduled-block-sequence-w7m2.md

## Findings and action
Read 5 Nov device report and owner instructions; device success is world/save/reopen only. Current T3 particle YAML audit wrongly excluded Unity indentless block sequence material entries with item indent equal to m_Materials key indent; existing test_block_array_still_supported would expose this bug. Fixed boundary from <= to < in scripts/t3_particle_material_chain_audit.py and added test_indentless_material_sequence_before_sibling_list to ensure later sibling m_SubEmitters slots do not leak into materials. Existing sibling-list negative fixture retained.

## Evidence
Work registration ac5a5cc1d5403cb6dfe2866437adbaf0cc7f3acb; code 5cf4eab1630d7b186e338757299564938fca48ef; test d8e1fe1ccb9656f5ff123c119ecc5ffe51f9d975. Latest initial HEAD 5fcddeb967dd2120b27eb0762af5f277c5819441. GitHub Actions recent offline integration run 42967944744 succeeded for T5 code, unrelated to this fix.

## Verification boundary
Source inspection confirms formerly excluded same-indent dash. New and preexisting regression tests written but full unittest NOT EXECUTED in this runtime (repository unavailable for local clone due DNS). No ZIP2 original-to-export comparison, no Android/GPU pixel proof, no APK built. RENDER-002 OPEN; NOT_READY 0/3. No changes to T4 mouse/T5 resolution or game assets.

## Next
Run python -m unittest discover -s scripts/tests -p 'test_t3_particle_material_chain_audit.py' on pinned current HEAD, then audit authenticated ZIP2 YAML and exported tree, compare hashed ParticleRenderer material bindings, trace Material->Shader->Texture and blend/alpha/zwrite; do not claim smoke fixed without device check. Check current HEAD and other T3 chat work before edits.
