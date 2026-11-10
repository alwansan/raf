# GFX-LAB — 20261110-GFX-chat-rdef-seven-pass-source-16
- session_id: 20261110-GFX-chat-rdef-seven-pass-source-16; origin: chat
- resumed_from: 20261110-GFX-chat-persistent-roadmap-15
- base_sha: 7c0e37af4f83934264393626b77868fada53daa2
- issue_id: RENDER-002
- experiment_key: GFX-MULTI-015-original-7pass-DXBC-RDEF-availability
- source_ref: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- scope: real original Shader48 selected one exact keyword/tier stage pair for all seven passes, count DXBC RDEF existence and generic verified chunk types for 14 stages; private runner, no exports of source code/bytecode.
- prior_runs: GFX-MULTI-014 CI42733664716 SUCCESS on one pair, no RDEF for VS/FS; RDEF absent count corrected null.
- run_url: created by workflow push; outcome initially CI_PENDING
- evidence_level: ORIGINAL_SOURCE only. Android Shader48 compile/GPU pixels and exact resource semantics remain FALSE.
- negative_controls: reject invalid DXBC size, unknown only-chunk, truncated chunk; missing RDEF returns null; source tokens/logs not exported.
- next_step: read safe CI report, update restore + backlog + session and state. If original RDEF absent broadly, inspect DXBC SHDR/SHEX declaration tokens or trusted independent original register reflection, not inferred SPIRV binding numbers.
- backlog: gfxlab/OPEN_WORK_AND_IDEAS_AR.md

## نتيجة مثبتة GFX-MULTI-015
- [CI42736017218](https://github.com/alwansan/raf/actions/runs/42736017218) **COMPLETED SUCCESS**, 80 source-free unit tests (source itself decoded in ephemeral runner); original fixed ZIP2 Shader48 2 SubShaders, 7 Passes, 14 exact representative VS/FS DXBC containers.
- RDEF was absent in **14/14** checked stages, present in **0/14**. Each selected stage has a bounded SHDR code chunk and an input/output signature chunk; declared DX11 resource and CB counts remain **UNKNOWN/null**.
- This proves RDEF absence in **one authentic pair per Pass**, not all 524 possible original VS/FS variant pairs.
- Files and original compiled program bytes purged after CI; no game/Unity Android GPU shader used, no pixel parity, no original shader restoration.
- Next: GFX-MULTI-016 parse original SHDR token declaration opcodes (strictly bounded) or independent reflection for b#/t#/s# register types/counts; this is still NOT original CB/sampler binding semantic equivalence.
