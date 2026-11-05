# T1 — Raft Android FFT engineering memory

Session: 20261104T235355Z-T1-9fca (started 2026-11-04T23:54:43.431Z); identity T1, T-team generation 2026-11-05; write branch `feature/android-native-port` ONLY.

## Startup and confirmed baseline
Read T_TEAM/PROMPT_AR.md, README.md, OPERATING_MODEL_AR.md, LEGACY_HANDOFF.md, MIGRATION_2026-11-05.md, TEMPLATES.md, SOURCES_AND_ACTIONS_AR.md, owner requirements, AGENTS.md, prompt README/CONTINUE/STATUS, ZIP2_SOURCE_PROVIDER; inherited B01/B06/B08/B18/B30/B48 memory. First live HEAD `cde13f783e5274d5898703459e8178e2485ef9db` and no nonterminal branch Actions in current 100-run page. Last actual Raft Android delivery APK86 `android-early-test-41812889049-1`, source `d181ee7152580f49ee0b41dfd05fa2bfdacfafe5`; latest CL `5394407b5cd0a0ca1848ff0902f8d2133bf6ea29`. No Unity or on-device proof for latest source. B18 `41931883517` verifies two explicit descriptor maps at original compiled-program level; B30 variantMap cannot select 20 slots; B48 candidate selectors do not establish Unity runtime kernel ID.

## Work in progress
Work: `prompt/coordination/work/WATER-001/T1-20261104T235355Z-T1-9fca-runtime-kernel-provenance.json`; issue WATER-001 remains OPEN/NOT_READY0/3. Original ZIP2 pinned `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, staged resources only after original bytes/SHA verified. Next investigate Dx11FFT/GpuFFT native caller method and serialized Unity compute naming/bindings. Hypothesis: compiled-slot indexing must not be passed to Unity FindKernel or Dispatch. No original source/shader bytecode will be published. T2/T3/T4/T5 track adjacent resources; avoid editing their files. Do not touch audio/Settings/touch/layout or start native build without coordination.

## Recovery procedure
Re-read current HEAD and T1 files before editing; check Actions nonterminal; inspect T-team work/messages; preserve B evidence; use expected SHA lease and no force. Outcome/test/run/commit to append after substantive step. No claims of restored FFT or device water.

## 2026-11-05 — first substantive FFT sampled-image role experiment (T1)
- New code `scripts/t1_fft_binding_sensitivity.py`, 6 synthetic controls, isolated workflow `raft-t1-fft-binding-sensitivity.yml`, original metadata only. Source commits a85355c, 318eb3d, c371ee0, 77dc8c9, 0888b13; final scoped code **ec6618e14ef6a26ba0d0dc925f3b17056d03721a**. Original untouched.
- Proven positive CI **41939314440 SUCCESS**: 3-part original ZIP2 source owner size115978112 and SHA0498f738...; ComputeShader pathID2456 SHA9d934f5c...; bank0 original compiled pairs0/1 and8/9 × profiles baseline, first swapped, second swapped = **6 actual two-pass CPU Vulkan executions**; both input swaps change numeric output for 2/2 pairs. No Unity/Adreno/device or raw assets.
- Recorded negative evidence: **41938536760** candidate pair18 second-swapped Mesa lavapipe SIGSEGV (-11); **41939082498** pair10 second-swapped finite/written but source-comparator tolerance=false. Do not count bank1; final scoped positive excludes it. Earlier run41938039589 anchor fixture failed before original; corrected. [Incident](../../incidents/T1/20261105T001100Z-original-fft-bank1-permutation.md).
- Report `docs/T1_ORIGINAL_FFT_INPUT_ROLES_2026-11-05.md`; experiment `prompt/coordination/experiments/T1/20261105T001110Z-T1-original-fft-sampled-roles.json`; resource `prompt/coordination/B_TEAM/resources/fft-original-sampled-descriptor-roles-t1.json` and result event in B ledger.
- Next independent real blocker: authenticated authored Unity `.compute` reconstruction with true runtime kernel identities/dispatch, strict descriptor resource names and Unity 2021/Adreno test. WATER-001 OPEN, NOT_READY 0/3, APK86 unchanged. Preserve old B evidence and green/negative URLs.
