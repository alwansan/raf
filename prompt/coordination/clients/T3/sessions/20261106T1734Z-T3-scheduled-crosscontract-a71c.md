# T3 independent scheduled session — 20261106T1734Z-T3-scheduled-crosscontract-a71c

- origin: scheduled
- issue: RENDER-002 OPEN / NOT_READY
- baseline HEAD: f05b516d1d91b722803298dd53b167539cb0f7f5
- scope commit: de2ef65b5759d17d2c61b879851d60a00a162ed0
- source snapshot: zip2 SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385 (not downloaded in this session)
- work: [independent scope](../../../../work/RENDER-002/20261106T1734Z-T3-scheduled-crosscontract-a71c.json)
- owner phone report: docs/DEVICE_FEEDBACK_42058825739_AR.md; device success restricted to Artifact 42058825739 and world/save/reentry.

## Source-code audit performed

Read scripts/t3_particle108_original_dxbc_rdef.py and scripts/t3_particle108_resource_binding_parity.py on the live branch. The former returns private original DXBC (input type, register point, count) and explicitly declares SPIR-V descriptor mapping unproven. The latter checks reflected SPIR-V (set,binding) layouts between original translation and roundtrip, but **does not compare against the original DXBC RDEF register contract**. Its stage descriptor parity is not a D3D-register semantic join. These are complementary gates, not contradictory results. No evidence of material/pixel repair follows from either alone.

Read latest T3 chat scope 20261106T1730Z-T3-chat-primary-index-4d8c; its source-authenticated CI 42262329490 reported VS primary layouts=3 and PS primary layouts=2. Do not repeat its original-source census. The next independent test should join original RDEF stage/family/count with translated SPIR-V stage/category/set/binding **in private CI only**, distinguish one-to-many remaps, arrays, unused bindings and keyword variants, and publish only aggregate failure categories. Require source SHA and stage/keyword identity matching before asserting correspondence. A numeric register==binding match alone is insufficient.

## Boundaries and next step

This cycle performed a static cross-contract gap audit, **not** a new test run, Unity build, source reconstruction, shader fix, or device validation. No raw game resources or identifiers were published. T4 physical mouse and T5 Resolution/button placement remain separate. Preserve .meta/GUID, .rgd, FMOD and Settings. Next cycle: add synthetic-only contract fixture covering array binding expansion and stage-specific remap, then run Python tests before any original-data CI; recheck HEAD and active T3 work first. Do not launch duplicate CI.
