# 20261110-GFX-chat-authentic-b-offset-SPV-index-multiset-47 — GFX-MULTI-073

- role: GFX-LAB, origin=chat; writable branch experiment/android-graphics-rootcause
- resumed_from: GFX-MULTI-072 SUCCESS [CI42888943112](https://github.com/alwansan/raf/actions/runs/42888943112); 521 source-free tests, 311/311 authenticated original CB stage counts matched 77 direct vs 350 immediate+relative overall, all 350 SPV IAdds have literal+Bitcast(OpLoad), all 77 direct Bitcast(OpLoad)
- original ZIP2 SHA: 15964ea8f246b6e076ce26b60931ee2e1a9a2385
- workflow: https://github.com/alwansan/raf/actions/runs/42890101891
- initial status: CI_RUNNING

For original Shader48 157 Pass-JOINT exact source representative pairs/314 stage instances, source private DXBC scanner independently tokenizes 9 supported ALU opcode families and stores a stage-local multiset (original b register, vec4 relative representation direct/offset, signed base literal), without exporting private keys. Independently, only real source-b authenticated translated SPV Uniform global OpAccessChain→OpLoad dynamic vec4 accesses are classified (direct Bitcast(OpLoad), or IAdd(one literal, Bitcast(OpLoad))) into the same private key. Compare duplicate-aware multisets per original stage and publish ONLY safe matched/missing/extra counts. Exact private b+offset profile multiset match would be a stronger structural observation but *never* authentic source temp component SSA→SPV runtime index equality, true source instruction bijection, original Material CB member semantics (GFX054 blocked), all 524 variant full code semantics, Adreno original Shader48 GPU pixel parity, or game APK readiness. Purge all original private sources. originalShaderRestored=false; phase_closed=false.
