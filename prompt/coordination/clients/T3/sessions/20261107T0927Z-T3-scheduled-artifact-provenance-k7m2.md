# T3 scheduled checkpoint — 20261107T0927Z-T3-scheduled-artifact-provenance-k7m2

- origin: scheduled; issue: RENDER-002; state: EVIDENCE_GAP_IDENTIFIED / OPEN / NOT_READY.
- resumed_from_session: 20261107T0827Z-T3-scheduled-rgb-classifier-v4k9; base_sha: bc3beac4215832a05da9295f977470b094e903db.
- Work scope registered first at commit 4413b76fb42485e133f0d068aa941c7427cbeb7a. Independent artifact provenance audit only; no overlapping T4 mouse or T5 display/delivery edits.
- Downloaded and inspected actual 41968665857 artifact 13389400444. The 3 JSON files contain **aggregate-only** data; none contains `pairs` records needed by integrated classifier. Baseline 106 = 76 exact + 30 RGB drift confirmed; 106 GUIDs present in exported metadata; 114 sampler bindings and zero measured sampler field mismatches. Detailed evidence: [artifact audit](../../../work/experiments/T3-20261107T0927Z-T3-scheduled-artifact-provenance-k7m2-artifact-audit.md).
- Owner phone feedback: 42058825739 enters/saves/reopens world, but white hand/raft, lighting and square smoke persist; no phone visual repair proven. CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57.
- No original per-pair sRGB/format manifest available in artifact. Do not fabricate it or run classifier against aggregate JSON. Need private same-export extraction + aggregate-only output, then original Material/ParticleRenderer association.
- No Unity build, CI rerun, asset mutation, .meta/GUID/.rgd edits or shared status overwrite. The run's ZIP remains expiring 2026-11-12 04:38 UTC; this audit records reproducible safe aggregates.
