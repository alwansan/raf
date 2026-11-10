# GFX-LAB — 20261110-GFX-chat-relative-CB-AST-41

- **origin:** chat
- **resumed_from:** successful GFX-MULTI-065 (CI42879705849), GFX-MULTI-066 (CI42880727817)
- **base SHA:** 649e23eae42601f7abc511b7a1904d7813915999
- **source:** ZIP2 15964ea8f246b6e076ce26b60931ee2e1a9a2385
- **scope:** GFX-MULTI-067 source-private relative CB operand AST grammar, NOT Shader48 Android runtime
- **CI:** https://github.com/alwansan/raf/actions/runs/42882730895 — initially CI_RUNNING
- **tool:** `gfxlab/tools/multi_shader_original_cb_relative_expression067.py`
- **tests:** `gfxlab/tests/test_multi_shader_original_cb_relative_expression067.py`
- **status at creation:** CI_RUNNING; final outcome must be read from GitHub run and artifact

New parser preserves in-memory source DXBC nested relative operand, signed immediate displacement and leaf register selection, checks independent token boundaries against GFX047 decoder, and compares aggregate CB operands to GFX063 and GFX051. Source/private b-register indices, nested input operand registers, offsets, program binaries, shader names, PPtrs/GUIDs must never be exported. SAFE category counts only. Fail closed for invalid registers/lengths, unrecognized representation, mismatched independent parser, and source ZIP2 SHA. After CI, record success or failure here and update `RESTORE_AR.md`, `memory/STATE.json`, `memory/MEMORY.md`.

**Unclosed gates:** original relative-index expression ↔ exact SPV SSA dynamic-index identity still blocked (no trustworthy original DXBC temp-def-use→vkd3d SPV origin); 427 genuine relative source operands not GPU semantically proven, 11,297 original instructions outside nine covered arithmetic opcode families; GFX054 Material property→b/t/s and CB member offsets absent, original Shader48 Android runtime and PC↔Adreno pixel parity open. No fake `originalShaderRestored` success flags.
