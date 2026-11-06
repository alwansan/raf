# T2 — original material Shader external pointers: immutable ZIP2 manifest and typed target proof
Date: 2026-11-06 UTC. Issue: WATER-001. Origin: chat.

## Source and provenance
- Provider: alwansan/raf ZIP2 immutable commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.
- Source owner: `Raft_Data/sharedassets0.assets`, verified **115978112 bytes**, SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`.
- Original Foam Shader object PathID 2420 raw SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1` rechecked in private runner.
- Manifest: 366 rows, 7789295609 aggregate **declared** bytes, strict schema, unique safe paths and independently known four-owner pins. The full 7.79 GB was **not** downloaded or SHA-verified. Only needed original owners/targets were reconstructed and byte-verified.
- Baseline [source-original four-owner graph 42247200163](https://github.com/alwansan/raf/actions/runs/42247200163): 156 material external Shader PPtrs across four owners, including 154 basename+typed-target candidates and two unresolved in `sharedassets0`. The 154 are **not** verified Unity GUID bindings.
- This scope extends [T2 scheduled manifest resolver](../prompt/coordination/clients/T2/sessions/20261106T1619Z-T2-scheduled-external-target-ambiguity-k8m2.md), preserving its collision and traversal guards.

## Independent source-original result
- New implementation: `scripts/t2_foam_original_manifest_pptr.py`; source-free controls: `tests/test_t2_foam_original_manifest_pptr.py`; workflow: `.github/workflows/raft-t2-foam-original-manifest-pptr.yml`. Final code commit `605acff84d7a7d59315cdeaf227fb1ce748df295`.
- [Final authenticated CI 42256633561](https://github.com/alwansan/raf/actions/runs/42256633561) **SUCCESS**, 11/11 new + 7/7 inherited synthetic controls. Full original SHA stage succeeded. Original private file/asset paths and GUIDs never emitted or uploaded.
- Source owner: 351 Material objects; **7 external Shader PPtrs**. Five resolved to previously pinned owner names, **two** had no prior four-owner link. Both previously unresolved pointers had **unique**, not ambiguous or missing, candidate paths in the immutable 366-row manifest; **one distinct target file**.
- That one candidate was staged from immutable original ZIP2, all **758412 bytes SHA-verified** against the exact manifest entry, and contained **two genuine typed Shader PathIDs** matching the two source Material pointers. **2 of 2 typed targets**; no unresolved target, no budget skip, no unreadable SerializedFile.
- [Earlier correct-source experiment 42256271654](https://github.com/alwansan/raf/actions/runs/42256271654) also **SUCCESS** with equivalent numeric outcome and safe artifact. Final CI removes a Git CLI compatibility fallback and relabels manifest *metadata* accurately.
- Safe final artifact: `t2-original-manifest-pptr-safe-42256633561` (artifact id `13523097034`, 600 metadata-reported bytes). This artifact contains count-only JSON, no private Shader names/GUIDs/paths/raw assets.

## Failed diagnoses and corrected command
- [42255582427](https://github.com/alwansan/raf/actions/runs/42255582427) original source stage passed; first private pointer step blocked.
- [42255987406](https://github.com/alwansan/raf/actions/runs/42255987406) isolated the problem safely to `candidate_sparse_checkout` (no raw private error leakage).
- The original script used unsupported `git sparse-checkout add --no-cone`. A local synthetic Git CLI check independently reproduced the unsupported option. The supported `git sparse-checkout set --no-cone` succeeded in authentic CI. No original bytes or game shader data were modified.
- Diagnostic failures were **CI staging command failures**, not evidence of missing Shader material links, nor failure of ZIP2 original file hashes.

## Interpretation and strict limitations
This is *source-authentic typed-object candidate resolution*, not a Foam Shader or material identity proof. Filename+SHA+PathID confirms typed target candidates under the staged file but cannot alone validate Unity external **GUID** resolution, actual runtime Material→Foam identity, CB0 upload, Spectrum/Blur/FFT runtime integration, Unity ShaderLab compile, GPU pixels, performance or Android acceptance. The two material references may belong to shaders unrelated to water. Do not turn these names into invented aliases, substitute Shader GUIDs or claim WATER-001 fixed.

The owner has separately confirmed world entry/save/reopen on [device-tested artifact 42058825739](https://github.com/alwansan/raf/actions/runs/42058825739). That is not this code's phone validation.

## Next meaningful engineering step
Privately authenticate Unity external file-identifier GUID and material ownership for the two typed candidates and trace whether the original Foam Shader or water render path actually references either. Use a narrowly bounded ZIP2 target and scene/prefab source only when SHA-pinned, keep private GUID/name comparisons inside scratch, and require a truly linked ShaderLab/Unity compile and device pixel comparison before declaring water restored. Coordinate any shared Material parser/scene edits with T3 and FFT attachment work with T1. `WATER-001` remains OPEN; no `READY` assertion.
