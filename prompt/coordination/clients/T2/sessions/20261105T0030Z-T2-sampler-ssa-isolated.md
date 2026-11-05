# T2 — isolated Foam sampled-image use investigation (20261105T0030Z)

Another T2 session (`20261105T0023Z-T2-foam-texture-identity`) remains active in state.json. Do not overwrite its state, MEMORY, work record, script or workflow. Conflict status: **paused_identity_conflict** for shared identity/state; independently scoped non-overlapping investigation from this explicit user Continue.

Read T_TEAM instructions and inherited B09/B17/B20/B24/B25/B45 evidence, live branch HEAD and nonterminal Actions. CI 41941354379 succeeded original Foam private source literal name analysis: **0/6** source texture symbols equal translated SPIR-V image symbols, while six original source textures, six SPIR-V sampled images and six SPIR-V samplers exist; no original source→material identity or Unity upload proven.

Plan before implementation: create standalone `scripts/t2_foam_spirv_sampler_use.py` and `tests/test_t2_foam_spirv_sampler_use.py` to trace *executed OpSampledImage→OpImageSample* uses to actual numeric image/sampler descriptor bindings in private compiled SPIR-V. Reuse B20 SHA-authenticated 4-stage packet and T2 resource gate, fail closed on ambiguous provenance, publish only numeric aggregate. New isolated source-only workflow with original ZIP2 pin and private cleanup, no reuse or modification of current T2 workflow. Do not start Unity/native build or alter game, audio, Settings or touch.

The proposed numeric compiled sampler pair is **not** original Material texture identity, original sampler state, ShaderLab import or device pixels; those remain unresolved. Attribution: B20/B24/B25 original Foam source/translation, B17 descriptors, T2 earlier CB/resource/name probes.
