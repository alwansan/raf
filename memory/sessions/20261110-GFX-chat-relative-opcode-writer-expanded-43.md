# 20261110-GFX-chat-relative-opcode-writer-expanded-43 — GFX-MULTI-069

origin: chat
resumed_from: GFX-MULTI-068 CI42883869947 SUCCESS, 427/427 source temp uses unproven by narrow nine-ALU writer runs
source ZIP2 SHA: 15964ea8f246b6e076ce26b60931ee2e1a9a2385
base: 9faf2896d44b6c64666bb5b797e8221ddcee1561
status: CI_PENDING (no claim until run/log/artifact confirms)

Added narrowly audited public Microsoft DXBC writer opcode families (14 extra known one-dest arities) to the 9 source scanning ALU opcodes, preserves independent 427/7990 source CB checks, strict parser and destination write mask, clears local candidate cache at ANY non-whitelisted opcode, especially control-flow. Returns only candidate vs unresolved counts; regardless of positive candidate these cannot prove control-flow dominance, actual register value, vkd3d SPV SSA correspondence or original Shader48 GPU/pixel correctness. No source b/temp index names or material IDs exported; runner purge always. No game/Unity APK.
