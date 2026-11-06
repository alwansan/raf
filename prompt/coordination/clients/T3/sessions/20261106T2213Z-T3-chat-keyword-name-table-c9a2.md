# T3 chat — Source-original Shader48 authored keyword name/flag table provenance

- session_id: `20261106T2213Z-T3-chat-keyword-name-table-c9a2`; origin=chat; issue RENDER-002 OPEN/NOT_READY; branch feature/android-native-port only.
- resumed_from_sessions: 20261106T2158Z-T3-chat-keyword-lattice-e6d4 and 20261106T2150Z-T3-chat-stagewrapper-19e4; scheduled 20261106T2133Z-T3-scheduled-contract-schema-9a2f.
- Read live RESTORE_AR.md, CHAT_AND_SCHEDULE_AR.md, PROMPT_AR.md, latest T3 sessions/CI and active native builder. Scope registered BEFORE code changes in `prompt/coordination/work/RENDER-002/20261106T2213Z-T3-chat-keyword-name-table-c9a2.json` at commit 4e12e5957054b992d90a3c362fea5288ec5609c7. Initial base 201e14caf01c4cbc47a798055830235eebbcbdb8.

## Question
Original 4/4 VSFS KeywordIndex combinations form exact two-switch set lattice with no explicit hardware tier (CI42301977939). Determine whether original Shader48 `m_ParsedForm` has Unity2021.2+ `m_KeywordNames`/`m_KeywordFlags`, whether the two anonymous changing numeric indices point to two legal/distinct authored keyword names, or whether both table fields are absent as in an older serialized engine. Do NOT publish any source names, indices, flags, paths, shader code or GUID. Even successful lookup is not Unity #pragma semantics or material binding.
- Referenced public format provenance: AssetStudio Shader.cs SerializedShader declares fields for Unity2021.2+ only (https://github.com/Perfare/AssetStudio/blob/master/AssetStudio/Classes/Shader.cs). Raft PC source version not assumed same as project Unity2021.3.

## Changes and CI
- Original implementation commit 1b868a64fc1ffdb8e9ba0ceb5e4ba1dcb4f307aa: `scripts/t3_particle108_original_keyword_names.py`, `tests/test_t3_particle108_original_keyword_names.py` (13 synthetic cases), one bounded step in existing T3-only private ShaderLab CI workflow. Reuse exact SHA-pinned ZIP2 4 owners/six scenes and verified four original 16-D3D11-record pairs. No native build/editor launch; scratch private and cleanup.
- First [CI42303344912](https://github.com/alwansan/raf/actions/runs/42303344912): failed one **synthetic test** for error precedence (exact Vertex/Fragment metadata mismatch caught before expected index namespace), prior tests passed. Fixed expectation only at commit c2637f94aa71770caa34652e5a9e7442544e120a.
- Second [CI42303410851](https://github.com/alwansan/raf/actions/runs/42303410851): 13 new synthetic controls passed, previous baseline tests passed, four private ShaderLab source candidates/8 glslang macro branches passed, but **workflow CLI typo** added extra output path to previous keyword lattice command, so source name-table step never reached. Fixed isolated workflow arg+cleanup at commit 50790bac18dbee72159be818480f2e9165eda0d9.
- Third [CI42303585869](https://github.com/alwansan/raf/actions/runs/42303585869) **in_progress at checkpoint**, exact source SHA 50790bac18dbee72159be818480f2e9165eda0d9. Do NOT dispatch duplicate.

## Constraints and next
- Native builder [42296450023](https://github.com/alwansan/raf/actions/runs/42296450023) still in_progress at initial check; no duplicate or interruption. Other T workers' files untouched. Audio/Settings/touch and original Unity game shader GUID/meta untouched.
- T3 trial vote remains لا يحتاج; no new phone-installable shader repair, no Unity compiler/runtime/adreno pixel proof. RENDER-002 stays OPEN.
- Next: inspect terminal CI42303585869, document exact source table presence/absence/mappability. If both fields missing, investigate authentic separate historical keyword table provenance; do not fabricate a name-based multi_compile. If mapped, validate flags semantics and material runtime keyword evidence before any game shader import.
