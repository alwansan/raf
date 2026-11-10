# 20261110-GFX-chat-extended-literal-rest133-40 — GFX-MULTI-066

- origin: chat
- resumed_from: GFX-MULTI-065 CI42879705849 SUCCESS (466 tests, 24/24 original pairs, 77/77 distinct source CB ranges loaded)
- base_sha: 777ee1c3348a4a59248d765d17033ec986f97afc
- source: ZIP2 SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385
- scope: disjoint Pass-JOINT source class representative indices [24,157); 133 exact source pairs /266 stage instances; CPU source-private only
- run: https://github.com/alwansan/raf/actions/runs/42880727817
- status: CI_PENDING until job and purge independently verified

Recompute 157 source classes, recheck GFX063/064 original 763 modified-literal +427 true-relative +6800 unmodified source CB uses and 656 stage-local distinct read ranges, then run all remaining 133 representative original pairs with Vulkan1.1 SPV validation, authenticated original b Uniform and UBO vec4, and original modifier-literal b/vec4 range→real SPV OpLoad overlap. Missing range fails evidence and original source private cleanup always. Separately count CB-free stages and individual source operand occurrences; neither a source range match nor an SPV pointer load alone proves original modifier numeric semantics or per-instruction mapping. GFX054 Material binding and 427 relative indices remain blocked; originalShaderRestored=false, phase_closed=false.
