# B38 — Material YAML duplicate-key guard / 4 November 2026

Issue: RENDER-002, scope: B05 same-instance Material m_TexEnvs/UV comparator (not original assets). [B05 predecessor](https://github.com/alwansan/raf/actions/runs/41915726289) passed 14 synthetic controls. [B44 comparator](https://github.com/alwansan/raf/blob/feature/android-native-port/scripts/b44_verify_material_colors.py) already had a separate strict loader for color fields.

## Reproduced defect
PyYAML yaml.safe_load silently keeps the last value of duplicate nested mapping keys. Reproduced locally with an invented Material: two m_SavedProperties keys containing disjoint m_TexEnvs produce only the last array, no rejection. The existing B05 exported_texenvs used yaml.safe_load, so an exported texture pointer/UV file with conflicting serialized keys could be incorrectly accepted as identical if the last copy matched the source.

## Production integration
Added a bounded SafeLoader subclass in B05 exported_texenvs to reject duplicate keys at all depths (Material root, m_SavedProperties, m_TexEnvs, slot, m_Texture pointer, and UV components), without changing game data, GUIDs, .meta, pass counts or any source asset. No YAML unsafe loader or private output. Existing safe export-root and same-instance trace restrictions remain.

## Evidence and limits
- Local independent proof: Python PyYAML safe_load duplicate key last-wins example.
- Tests: 7 synthetic cases in tests/test_b38_material_yaml_uniqueness.py, plus the prior B05 suite; exact CI conclusion and commit to be appended after GitHub run.
- No authenticated full Raft ZIP2 same-export Material comparison has been run, no pixels/images/shaders generated, no original Material repaired, and no Android device acceptance. RENDER-002 remains OPEN; project NOT_READY and 0/3 independent reviews.
- Owner-confirmed audio and Settings preserved; touch/layout deferred; no native Unity workflow or release requested.
