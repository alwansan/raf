# W3 — m_SavedProperties slot-name-level binding completeness for priority-shader materials — 4 November 2026

Sixth W3 step (client `raft-20261103T153100Z-b4d2c9e7`), pre-announced in [the scope message](../prompt/coordination/discussions/RENDER-002/2026-11-04T103000Z-raft-20261103T153100Z-b4d2c9e7-scope-announcement-slot-coverage.md). **Structure-only by explicit policy**: it compares every priority-referencing Material's `m_SavedProperties.m_TexEnvs` slot-name set against the texture-slot names its Shader declares (`m_PropInfo`, type-4) — no PPtr targets, no values, no colors are read into the aggregate; W2's texture-value/pointer-corroboration/format lanes remain fully theirs (their 159/159 external-pointer verification and their color-tint-usage baseline are explicitly out of this scope).

Inputs: identical 82 byte-authenticated local owners (same pin checks as the committed inventory); slot tables freshly read from the shaders in-run (not cached from prior artifacts). New script `scripts/probe_w3_savedprops_slot_coverage.py` + 10/10 model tests (9/9, 7/7, 8/8, 8/8, 8/8 suites remain green). Real-data run exit 0 with all four negative controls true.

## Headline result — the slot dictionary is structurally complete everywhere

| Aspect | aggregate across the 1,282 priority materials |
|---|---|
| Materials referencing the 11 priority targets | **1,282** (matches the inventory and step-4 exactly) |
| Materials whose TexEnv slot-name set covers **every** declared texture slot | **1,282 / 1,282** |
| Missing slot occurrences (declared ∉ present) | **0** |
| Extra slot occurrences (present ∉ declared) | **0** |

Per-target: complete coverage for all its materials — `Standard` 674/674 (9 declared slots), `Skin_Amplify` 208/208, `Shimmer` 96/96, `' BlockPaint'` 87/87, `Nature/SpeedTree8` 50/50, `ParticleShader` 48/48, `Tri-Planar` 30/30, `Vegetation` 29/29, `ParticleShader_Additive` 26/26, `AnimalDissolve` 23/23, `FireParticles_Amplify` 11/11. Per-target missing/extra lists are empty, hence both the missing-slots and extra-slots SHA-256 commitments are `null` by the no-empty-string rule (documented, not omitted).

Engineering reading (aggregate only): every serialized priority material carries a well-formed, shader-consistent texture-slot dictionary — a runtime material loader can rely on uniform slot presence without per-material slot discovery; any shader leakage into the appearance builders. Note honestly: several of those entries bind `m_Texture` PPtrs to pathID 0 (null) — *binding-nullness is a value-level observation reserved for W2's value lane and was NOT aggregated here*; this probe saw only names, never the values.

## Honest supersession (same silent-empty bug class as corrected in step 2)

The first prediction run aggregated **zero** coverage under a matcher that expected dict-form map entries (`{m_First, m_Second}`) while UnityPy 1.25.4 delivers this serialized dictionary as **(name, value) tuples** with value shapes `{m_Texture: PPtr, m_Scale, m_Offset}` — the drop was silent, so the unpromising 0/1,282 result was treated as suspect, not published. Root-cause fixed in the pure extractor (`material_texenv_slots`), tuple/dict dual-form support and mixed-form tests added (tests grew 8→10), re-run exit 0; the corrected run above is the **only** durable artifact. This is exactly the failure-class discipline applied in the step-2 inventory fix.

## Evidence

- Durable artifact: `docs/W3_SAVEDPROPS_SLOT_COVERAGE_2026-11-04.json` — SHA-256 `c16d78925ce3352a38610f79097ec1607223a55d28673d56b60d99220e51826d`, programmatically verified free of any slot-name strings (commitments are `null` by the empty-list rule; raw names only via the local `--print-names-local` echo).
- Model tests `scripts/w3_test_savedprops_slot_coverage.py` — **10/10 OK** (type-4-only slot table, tuple-form extraction, mixed-form zero-silence, coverage arithmetic, empty-string commitment rejection, 11-target identity parity).

## Limits

Name-level structure only: texture payload audits, formats/sRGB, pointer-target verification, and any binding values/results remain W2's; program bodies remain W1's; build/export remains W4's. No visual/GPU/phone claim. **WATER-001/RENDER-002/FFT-FORMAT-009 remain OPEN; game NOT_READY; no immutable candidate; 0/3 reviews.** Next W3 options: the 22 empty-config `Standard` materials base-variant audit or the `StandardVColor` (sharedassets36:880) vertex-color field audit.
