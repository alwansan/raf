# 20261110-GFX-chat-extended-literal-rest133-40 — GFX-MULTI-066

- origin: chat
- resumed_from: GFX-MULTI-065 CI42879705849 SUCCESS (466 tests, 24/24 original pairs, 77/77 distinct source CB ranges loaded)
- base_sha: 777ee1c3348a4a59248d765d17033ec986f97afc
- source: ZIP2 SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385
- scope: disjoint Pass-JOINT source class representative indices [24,157); 133 exact source pairs /266 stage instances; CPU source-private only
- run: https://github.com/alwansan/raf/actions/runs/42880727817
- status: CI_PENDING until job and purge independently verified

Recompute 157 source classes, recheck GFX063/064 original 763 modified-literal +427 true-relative +6800 unmodified source CB uses and 656 stage-local distinct read ranges, then run all remaining 133 representative original pairs with Vulkan1.1 SPV validation, authenticated original b Uniform and UBO vec4, and original modifier-literal b/vec4 range→real SPV OpLoad overlap. Missing range fails evidence and original source private cleanup always. Separately count CB-free stages and individual source operand occurrences; neither a source range match nor an SPV pointer load alone proves original modifier numeric semantics or per-instruction mapping. GFX054 Material binding and 427 relative indices remain blocked; originalShaderRestored=false, phase_closed=false.

## CI verified GFX066
[CI42880727817](https://github.com/alwansan/raf/actions/runs/42880727817) SUCCESS: 472 source-free tests; disjoint [24,157) **133/133 real original source pairs, 266/266 Vulkan1.1 SPV stages**, 265 original CB stages authenticated +1 CB-free, **682 source modified literal index operand occurrences**, **579/579 distinct stage-local source b/vec4 ranges** observed in translated SPV OpLoad, zero missing; private source purge PASS and safe artifact 13793667632 (expires 2026-11-17T19:00:33Z UTC). Combined with GFX065 [0,24): 763 original modified-literal source operand occurrences and **656/656 stage-local distinct source ranges** corroborated by real SPV loads across **157 source class representative pairs /314 stage instances** (311 CB stages, 3 without CB); 427 true-relative index uses unproven. Range presence cannot prove one-to-one operation/value semantics, original CB property labels, 524 full shader programs, Unity runtime or Adreno pixels. `originalShaderRestored=false`; `phase_closed=false`.

### Next GFX-MULTI-067 (P0)
Synthetic-first DXBC relative vec4 address-expression grammar, then original source-private SSA provenance for 427 truly relative source CB indices; prove specific original DXBC relative-expression→SPV OpAccessChain index expression, not merely count of dynamic OpLoads. If impossible, report explicit BLOCKED_SOURCE_DYNAMIC_CB_INDEX_PROVENANCE. GFX054 original Material property→t/s/b/CB semantic bridge also independently blocked.
