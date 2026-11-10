# 20261110-GFX-chat-extended-literal-batch0-24-39 — GFX-MULTI-065

- origin: chat
- resumed_from: GFX-MULTI-064 SUCCESS CI42876582659
- base_sha: c3e8df433b3c521d467672fe17a6e8e9069c73e7
- source_ref: ZIP2 pinned 15964ea8f246b6e076ce26b60931ee2e1a9a2385
- experiment_key: GFX-MULTI-065 [0,24) Pass-JOINT first batch extended literal CB to real SPV OpLoad
- scope: source-private CPU only; no APK, T1–T5/main/zip2 read-only
- status: CI_PENDING, do not infer success from commit

Recheck authentic 157 representative pairs and 314 stage instances against original GFX063/064 partition 763 extended literal / 6800 unmodified / 427 dynamic source occurrences and 656 stage-local distinct CB b/vec4 ranges. Then only [0,24) exact original pairs, 48 Vulkan1.1 SPV stage validations, original b Uniform global + reflected vec4 UBO, actual OpLoad range presence. Include no-CB stages explicitly; record source operand occurrences and distinct ranges separately. Strict failure if any missing, and purge original ZIP2/DXBC/SPV in always block. Count-only evidence export.

Limits: 24 pairs don't prove all 763 individual extended-modifier operands; source range overlap does not prove operand-by-operand or numeric modifier equivalence; 427 dynamic relative indices unresolved; GFX054 Material property→original b/t/s/CB offsets BLOCKED; no Unity original shader, PC/Adreno pixel parity or owner acceptance. originalShaderRestored=false; phase_closed=false.
