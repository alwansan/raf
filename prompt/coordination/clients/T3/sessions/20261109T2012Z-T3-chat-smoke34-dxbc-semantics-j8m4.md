# T3 chat — authenticated genuine smoke34 original DXBC semantic/mask VS↔FS join

session_id: `20261109T2012Z-T3-chat-smoke34-dxbc-semantics-j8m4`
origin: `chat`
base_sha: `08cd6040feed177d972502a98523c294249822de`
branch: `feature/android-native-port`
resumed_from_sessions: `20261109T2003Z-T3-chat-smoke34-name-anchors-n7c2`, `20261109T1943Z-T3-chat-smoke34-dxbc-translation-c4m8`
issue_id: `RENDER-002` OPEN / NOT_READY 0/3
work record: `prompt/coordination/work/RENDER-002/20261109T2012Z-T3-chat-smoke34-dxbc-semantics-j8m4.md`; reserved ahead of code at [186adb8](https://github.com/alwansan/raf/commit/186adb8d57cd63a0a530ad22f92fefbbbe7894cf).
experiment_key: `t3-original-sha15964-smoke34-private-2keyword-dxbc-isgn-osgn-semantic-index-register-mask-join-only-v1`
resource_key: `original-zip2-6scenes4owners-T3-DXBC-signatures-only`

## Verified baseline and non-overlap
T3 name-anchor [CI42689814110](https://github.com/alwansan/raf/actions/runs/42689814110) SUCCESS shows 0/13 source-to-roundtrip compiler reflected input names preserved and 0/9 output names preserved (all names changed), despite SPIR-V CPU-valid 4/4 and same-version VS/FS interface compatibility 2/2. This is not an original DXBC semantic/register map. Earlier [CI42683328646](https://github.com/alwansan/raf/actions/runs/42683328646) verified genuine source: 17 smoke-name ParticleSystemRenderers / 34 Material slots / one private Shader48 distinct from equal-34 fire; two exact keyword-matched D3D11 VS/FS pairs. T1/T2/T4/T5 on different files; no source/Unity build overlap. No APK/OBB/device game/source edits.

## Engineering implemented
1. [script](../../../../../../scripts/t3_original_smoke34_dxbc_semantic_join.py) `scripts/t3_original_smoke34_dxbc_semantic_join.py` commit [2e8d173](https://github.com/alwansan/raf/commit/2e8d173d1c68de7e94b9d065bd8ec80841f9518a): genuine original SHA source graph and owner authentication, immutable ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, strictly original 8-record D3D11 table and two matched keyword/player-bucket VS/FS pairs. Reuses prior robust T3 original-921 DXBC ISGN/OSGN chunk signature parser and 2-stage semantic-index/mask join, but ONLY on smoke34 private Shader48 identity, not 921 Shader48. Program/semantic data remains in CI private memory; only allowlisted numeric aggregates.
2. `tests/test_t3_original_smoke34_dxbc_semantic_join.py` commit [ea2aa93](https://github.com/alwansan/raf/commit/ea2aa935a75d15bfc6cb8edddcf9f62cf8999f51), with correction [6d58cae](https://github.com/alwansan/raf/commit/6d58cae5c9a3e545c05ea990f15c84ec136d8da2): 10 synthetic source-free tests for true semantic join, unmatched names, missing mask lanes, duplicate/missing data, malicious comparator labels/counters, private name/program non-disclosure, false readiness flags.
3. Isolated SHA-original source-only workflow `.github/workflows/raft-t3-original-smoke34-dxbc-semantic-join.yml` commit [f46f792](https://github.com/alwansan/raf/commit/f46f792b5bb7cc17228d52a67b1ff950870aa831), Ubuntu24.04 with 28-min timeout, exclusive concurrency cancel:false, only JSON safe artifact. Never uploads compiled DXBC, original shader/scene files, semantic names, GUID/PathIDs, per-program hashes or stage reflection.

## Final verified authentic result — 2026-11-09 20:16 UTC

- [GitHub Actions CI42691211652](https://github.com/alwansan/raf/actions/runs/42691211652) **COMPLETED SUCCESS**; 10 new +21 previously hardened DXBC semantic parser +7 source stage-inventory Python tests PASS (38 total). Verified SHA6 scenes and SHA4 owners from same immutable original zip2.
- 2 exact source DXBC keyword VS/FS pairs / 4 compiled original DXBC programs. ISGN signature headers 4 and OSGN headers 4 (input+output for each program).
- Aggregate original source **7 user Fragment Input semantic records**, **7 Vertex Output records**, **7 matched semantic/index pairs**, **0 unmatched fragment semantic records**, **0 fragment unmatched lanes**, **0 missing output lanes on matched semantic**, **0 source VS/FS semantic type mismatches**, **0 unused vertex semantic records**.
- Original user Fragment Input mask lanes 28, Vertex Output mask lanes 28, both original source register component counts also 28. 2 input and 2 output system-value records in original four-program total.
- Safe artifact [13707545897](https://github.com/alwansan/raf/actions/runs/42691211652/artifacts/13707545897) 798 bytes, expires 2026-11-16T20:15:53Z, aggregate counters only. Negative tests prohibit original semantic names/program bytes/registers in public JSON.
- **Boundary:** genuine original DXBC-to-DXBC VS/FS semantic-link source PASS. There is still NO proof of which SPIR-V Location/Component corresponds to which original semantic/index/register, nor roundtrip HLSL semantic equivalence, original ShaderLab program replacement, texture alpha/vertex stream/interpolation, Android Raft smoke appearance or user square-smoke identity. Do not fake ColorMask/blend or declare graphics READY. RENDER-002 OPEN NOT_READY 0/3.
- This source-only scope is finished; release unique resource. Next independent experiment: exact DXBC semantic read-mask component cardinality compared to original SPIR-V source/roundtrip (counts only), and then immutable semantic-to-location mapping with collision checks. Avoid guessing from compiler names (0 matches) or duplicated vec4 types.
