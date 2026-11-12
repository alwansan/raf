# GT Chat-25 — Spectrum original keyword scope and 82-owner Material closure

**Date:** 2026-11-12. **Only write:** `feature/android-native-port`. **Original ZIP2 read-only:** `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. Never use Git LFS or overwrite original Shader / Material / GUID / .meta.

## Four newly verified independent CI milestones

1. [43297804472 SUCCESS](https://github.com/alwansan/raf/actions/runs/43297804472), two jobs. Synthetic Unity **2021.3.45f2** Android Vulkan Global `multi_compile` and Local `multi_compile_local` keyword controls: original-format serialized flag bytes **Global=0**, **Local=1**; `Shader.keywordSpace.isOverridable`: global=true, local=false. 6,217B synthetic bundle, Shader errors=0; finalized log hidden GLSL/import/internal-variant errors=0. Original ZIP2 Spectrum flag index4=0 from [43296468683](https://github.com/alwansan/raf/actions/runs/43296468683) thus source-corroborated global candidate. This mapping is measured from a **synthetic** Unity2021 target, not from running the original Spectrum game Material.
2. [43299461114 SUCCESS](https://github.com/alwansan/raf/actions/runs/43299461114), all three jobs. SAME private **single** seven-Pass source-authentic Spectrum ShaderLab with original index4 keyword: Unity2021 Android Vulkan imported 7 Passes, 2 ShaderVariantCollection entries, 0 Shader errors, **14,484B** private bundle. New `privateKeywordGlobalOverridableConfirmed=true` and `privateMaterialKeywordOffOnOffAccepted=true` for a **new synthetic Material**, with finalized second-job console errors all zero. **Not** original runtime material or Adreno pixel equivalence.
3. [43299180998 SUCCESS](https://github.com/alwansan/raf/actions/runs/43299180998): SHA-original ZIP2 40 `sharedassets` owners, **474,065,455 bytes** verified, **1,392** serialized Materials inspected, **0** exact local/external `Material.m_Shader` references to `sharedassets0.assets / PathID2432`. Source-only coverage.
4. [43300053045 SUCCESS](https://github.com/alwansan/raf/actions/runs/43300053045): **FULL 82/82 original serialized owners** SHA verified (**819,595,355 bytes**) and **all 1,556 Materials** scanned, **zero** exact direct local or external Material.m_Shader PPtr links to original Spectrum Shader PathID2432. The source Shader itself was authenticated and its keyword index4 flag remains 0. This **rules out a serialized direct Material reference within 82 original owners**, NOT a dynamically created Material, `Shader.Find`, script-generated water component, engine internal resource, alternative runtime binding, exported Unity GUID or phone rendering.

## Important engineering consequence

Do not invent or patch `Spectrum Material GUID` from this source: no original serialized Material binding to this shader was found among all 1556. Next evidence path is the **SHA-original managed assembly/runtime shader acquisition**, e.g. typed `Shader.Find`/ `Material(Shader)` IL and water renderer assignments, verified source not literal grep only. Existing Foam-specific typed IL lineage scripts may be adapted to Spectrum with fresh source-authenticated names and exact typed-call identities. Keep source bytes, method symbols, names, GUIDs and IL private. Only aggregate SHA-linked evidence should be committed.

`M2/P06` remains BLOCKED: original runtime Material, sampler/CB0/RT, Foam Global original 2Pass, compute kernel6 provenance, device water pixels and 770 Dummy post-restorer are still missing.

## Existing full native build

[43299084397](https://github.com/alwansan/raf/actions/runs/43299084397) uses snapshot `2666622cbc93a4fde0dae22371cd3b157dc15ab7`, earlier than this GT scope work; in `reconstruct` stage at the time of inspection. Do not rerun or cancel. Even a successful XAPK from that older snapshot will NOT include these GT tests or prove water pixels.

## Recovery

Read `clients/GT/RESTORE_AR.md`, `RESTORATION_PLAN_AR.md`, `RESTORATION_PLAN.json`, `state.json`, `SUMMARY_AR.md`, `MEMORY.md`, then Chat23/24/25. Check latest branch HEAD + actual job conclusions before any writes. Working policy: ZIP2 SHA only, no LFS; source/Unity/private/device stages distinct and fail-closed.
