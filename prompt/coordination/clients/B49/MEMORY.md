# B49 — 20261104T2054Z-B49-c81f

- Session initial HEAD 649ec8e5b227ecae970b161ceb3339e2be1929c2; live read B_TEAM prompts/README/OPERATING_MODEL/SOURCES/TEMPLATES/REVIEW/SUMMARY/RESTORE, AGENTS, owner requirements, STATUS, ZIP2 provider, WATER-001 issue, shader contract.
- Latest game release APK86/run 41812889049; B50 LOCAL-005 source checks 41909535306 and 41909535307 succeeded. CL review 5394407: water pass failures and kernel count zero remain device-observed on APK86; new code not device-tested.
- Current work WATER-001: existing gate uses shader-wide program presence with raw Pass token count; multiple pass declarations can be accepted with only one program. Plan to require independently executable authored programs per pass, synthetic valid/missing/comment/string controls; preserve strict authentication flag, no dummy and no Unity native request.
- Original ZIP2 provider SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385; no original raw source fetched/published. B50 working LOCAL-005 independently. Audio/Settings preserved; touch deferred.
- Next: implement/test small code fix, update work/event/MEMORY/STATUS, verify CI. Water/GPU/device NOT_READY 0/3.

## Checkpoint — 2026-11-04T21:03:00Z

- B49 source repairs committed: helper 1173a23, regression fixture 588610c, live water-gate integration 5070247, isolated source-only workflow 3c4c6e3. No protected branches, native requests or external packages touched.
- [CI41911824567](https://github.com/alwansan/raf/actions/runs/41911824567) at source `3c4c6e3b350b611e5d364ae3fdc3c6837a11d4ea` **SUCCESS**. Job126861111744: 6/6 new tests plus 5/5 existing tests, code-only. The negative control with all required pass counts but only one complete program fails structural contract as expected. This rejects former pass/program global-count model, not original shader data.
- New contract sees each Pass's braces, matched CGPROGRAM/ENDCG or HLSLPROGRAM/ENDHLSL with content, ignores comment/string decoys; no original source emitted. Current native `authentic_water_kernel_identity_verified` remains false; WATER-001 OPEN, NOT_READY0/3. No Unity/device/FPS/Adreno results, no new APK.
- Experiment `prompt/coordination/experiments/B49/20261104T2054Z-B49-water-pass-guard.json`, report `docs/B49_WATER_SHADERLAB_PASS_CONTRACT_2026-11-04.md`, result event `events/B49/20261104T2101Z-water-pass-guard-result.json` and issue WATER-001 links updated.
- Rejected hypothesis: shader-global has_program was sufficient proof every pass was authored. Rejected from synthetic fixture and regression.
- B50 independently handles LOCAL-005, including SteamStats and Cheat; do not repeat. B45 works original Blur pass proof. Next distinct useful work: authenticated original Spectrum/Foam pass program and material binding recovery, avoiding B45's Blur and existing W1/W2 inventories. Begin by inspecting current B sessions and existing W2 binding topology, then stage SHA-verified ZIP2 programs for private compilation and pixel validation when permissions/resources allow.
- Session paused at this checkpoint; no background work promise. No B49 original source hydration performed.
