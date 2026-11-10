# 20261110-GFX-chat-relative-opcode-writer-expanded-43 — GFX-MULTI-069

origin: chat
resumed_from: GFX-MULTI-068 CI42883869947 SUCCESS, 427/427 source temp uses unproven by narrow nine-ALU writer runs
source ZIP2 SHA: 15964ea8f246b6e076ce26b60931ee2e1a9a2385
base: 9faf2896d44b6c64666bb5b797e8221ddcee1561
status: CI_PENDING (no claim until run/log/artifact confirms)

Added narrowly audited public Microsoft DXBC writer opcode families (14 extra known one-dest arities) to the 9 source scanning ALU opcodes, preserves independent 427/7990 source CB checks, strict parser and destination write mask, clears local candidate cache at ANY non-whitelisted opcode, especially control-flow. Returns only candidate vs unresolved counts; regardless of positive candidate these cannot prove control-flow dominance, actual register value, vkd3d SPV SSA correspondence or original Shader48 GPU/pixel correctness. No source b/temp index names or material IDs exported; runner purge always. No game/Unity APK.


## Verified outcome
[GFX069 CI42884845500](https://github.com/alwansan/raf/actions/runs/42884845500) SUCCESS /497 tests. Strictly added 14 Microsoft opcode arities to GFX068 writer whitelist; original 427 source relative CB index uses rechecked, 68 nearest preceding candidate writers in contiguous trusted opcode segments (all opcode 41 ISHL; 17 one instruction and 51 two–four instructions apart), 359 uses remain unresolved. 558 additional trusted writer opcode instances, 10,739 hard barriers. Original private source purge PASS, safe artifact13796065658. These are **not** actual source def→SPV SSA or control flow dominance equivalence; GFX054 Material→resource binding blocked; originalShaderRestored=false and phase_closed=false. Next GFX070 first examine 68 ISHL candidates with def-use/CFG+SSA root evidence, avoid fake success.
