# T3 independent scheduled scope — DXBC smoke34 follow-through
session_id: 20261109T1935Z-T3-scheduled-dxbc-handoff-k7m4
origin: scheduled
base_sha: 392417ee4c8b281ca002cab4c21398bb323140b9
issue: RENDER-002 OPEN / NOT_READY 0/3
experiment_key: t3-smoke34-authentic-dxbc-two-keyword-pairs-translation-readiness-handoff-v1
resource_key: none (documentation/source-only; no original download or CI)
files: this new work record and independent T3 session only. No shared code, game asset, APK or workflow edits.

## Evidence and no-duplication decision
Latest T3 chat 20261109T1924Z establishes original source D3D11 inventory [CI42683328646](https://github.com/alwansan/raf/actions/runs/42683328646): 8 D3D11 table entries, 2 VS and 2 FS variants, 2 exact keyword-matched pairs, 0 unmatched; source 17 renderers/34 material slots/one shader. Earlier [CI42681908313](https://github.com/alwansan/raf/actions/runs/42681908313) proves exact original same-instance ShaderLab export marked ACTUAL_DUMMY_SHADER_TEXT_EXPORTER; lexical ColorMask RGB missing despite original pass RGB. The source has alpha-dependent color/alpha blend, ZWrite OFF, Cull OFF. The D3D11 program inventory is source-only and does not prove translation or Android use. Current latest workflow runs include successful source inventory, no need to rerun it.

## Next engineering gate (must not misstate proof)
Translate precisely both original VS/FS keyword-matched pairs **privately** using pinned toolchain; verify shader stage I/O signature, interpolants, vertex color/UV, alpha texture sample, keyword permutations, blending RGB mask, ZWrite and Cull from original parsed pass. Generate safe aggregate only (no DXBC, shader source, PathIDs or raw assets in public logs). Compare postvendor/current restoration by exact source identity; no broad shader replacement. If translation fails, record unsupported opcode/stage class without publishing bytecode. Only after program+pass parity build an isolated Unity graphics test; only owner phone evidence can validate square smoke.

## Team overlap and resource decision
T1 water/FFT, T2 foam, T4 mouse, T5 resolution/shared mini remain separate. The latest T3 chat has already run original D3D11 inventory; this scheduled cycle must not dispatch equivalent CI or overwrite its work. No shared heavy resource acquired.
status: evidence_handoff_completed; next: authentic private DXBC translation and postvendor comparison, not another source inventory.
