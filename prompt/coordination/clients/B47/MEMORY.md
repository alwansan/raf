# B47 — memory

- Session: `20261104T2055Z-B47-c4e7`, 2026-11-04 UTC. First registration; no prior B47 memory existed at branch HEAD `ef0846d094a769b20f3408db44d06aea56f668d9`.
- Read B_TEAM/PROMPT_AR, README, OPERATING_MODEL_AR, SOURCES_AND_ACTIONS_AR, SUMMARY, REVIEW, TEMPLATES, RESTORE; AGENTS.md, CURRENT_OWNER_REQUIREMENTS, prompt/README, CONTINUE, STATUS, ZIP2_SOURCE_PROVIDER, W1 original shader-links, W2 fullgame color/texture results, RENDER issue.
- Live baseline `ef0846d094a769b20f3408db44d06aea56f668d9`; APK86 release `android-early-test-41812889049-1`, build 41812889049; CL main `5394407b5cd0a0ca1848ff0902f8d2133bf6ea29`, reference device logs and images reviewed in B_TEAM/REVIEW. Last B50 offline Steam StoreStats boundary success 41909535306 / 41909535307; B50 also owns Cheat.GetSteamID probe. Do not overlap.
- P0 WATER-001 chosen: investigate `scripts/verify_water_render_contract.py` ShaderLab `Pass` contract. Hypothesis: loose regex counts empty Pass blocks and global unrelated program; structural check can falsely approve a missing authentic pass, permitting broken water before native build.
- Planned change: fail-closed per-Pass program verification with synthetic negative controls, no original shader bytes or GUIDs. Do not assert restored FFT/pixels/runtime. Audio/Settings unchanged, touch deferred.
- No tests or engineering changes yet. Next: create session/work record, inspect script/tests, implement tests and validation; after result update evidence, state and STATUS. NOT_READY 0/3.
