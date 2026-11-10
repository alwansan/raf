# GFX-LAB — 20261110-GFX-chat-shader-variant-feasibility-06
- session_id: 20261110-GFX-chat-shader-variant-feasibility-06; origin: chat
- resumed_from: 20261110-GFX-chat-owner-six-shader-gap-05
- base_sha: c919f6816e79306d4234ca0f519b077f5062e7b1
- experiment_key: GFX-MULTI-006-shader-stage-program-variant-source-feasibility
- scope: count source Shader48 seven-pass Vertex/Fragment m_SubPrograms and compressed platform metadata privately, no GPU equivalence claims or source leak
- source_ref: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- runs: previous GFX-MULTI-005 CI42725841763 SUCCESS; new GFX-MULTI-006 auto trigger pending
- experiment limitation: stage variant counts or GPU blob indices cannot prove Android GLES program compilation, keyword/CB/sampler/semantics parity, or player rig restoration
- expected outcome: private source structure viability report; no compiled shader bytecode output, no APK

## GFX-MULTI-006 first-run and parser correction
- First CI 42726475369 SUCCESS unit tests but **0 in legacy m_SubPrograms per pass**; one compiled platform metadata entry and one compression metadata entry. Cannot conclude absence of compiled programs from this result.
- Unity 2021.3 serialized Shader version 3 can use m_PlayerSubPrograms tiered lists while m_SubPrograms is empty (public AssetRipper source investigation). Corrected parser to inspect both, with nested typed m_BlobIndex count and negative synthetic test. Retry triggered via workflow-file change; awaiting evidence.
- No source bytes/keywords/IDs printed. OriginalShaderRestored remains FALSE.
