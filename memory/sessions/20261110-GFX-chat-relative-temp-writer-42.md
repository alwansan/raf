# GFX-LAB — GFX-MULTI-068 original CB relative source temp writer candidate probe

session_id: 20261110-GFX-chat-relative-temp-writer-42
origin: chat
base_sha: 9faf2896d44b6c64666bb5b797e8221ddcee1561
resumed_from: GFX-MULTI-067 SUCCESS CI42882730895 (427 nested relative CB vec4 source temp components, 409 distinct stage-local expression keys)
source: ZIP2 15964ea8f246b6e076ce26b60931ee2e1a9a2385
run: https://github.com/alwansan/raf/actions/runs/42883869947
status: CI_QUEUED at creation; only a finished CI with verified log/purge establishes facts

GFX068 scans the original 157 Pass-joint class representative source VS/FS pairs (314 stage instances) and compares an independently decoded original CB relative operand AST to the GFX067 parser. For each of 427 source relative CB vec4 uses, retain private source temp register and selected x/y/z/w component, look for the nearest preceding writer inside a contiguous supported 9-ALU opcode run, invalidate candidate writers at *every* unrecognized opcode / potential control-flow and any unknown destination, and count unresolved separately. Positive evidence is **local previous-writer syntax candidate ONLY**, not a control-flow dominance proof, runtime bounds, exact vkd3d SSA root or source→SPV numerical equivalence. Original b#, temp number and all DXBC are CI-private, aggregate-only. Source ZIP2 always purged.

Do NOT claim original Shader48 restored; GFX054 original Material property→original t/s/b and CB-byte semantics still blocked, 427 exact dynamic address expressions not proven equivalent on SPV/Adreno, full 524 variant instruction semantics not proven. No original Unity shader or game APK produced.


## Verified GFX068 original source-only outcome
[CI42883869947](https://github.com/alwansan/raf/actions/runs/42883869947) COMPLETED SUCCESS 491 source-free tests, authentic 157 Pass-joint source representatives, 314 stages, original 427 relative CB index uses, all 427 source temp components syntactically valid. **0/427 nearest prior temp component writer found inside only nine supported arithmetic ALU contiguous runs; 427/427 unresolved in that narrow run.** Source opcode barriers 11,297; original full DXBC parser cannot conclude these temp components have no writers. Source purge PASS. Safe artifact 13794328581 expires 2026-11-17T19:18:55Z UTC. No CFG dominance/SPV SSA/per-operand semantics proven; originalShaderRestored=false, phase_closed=false.
