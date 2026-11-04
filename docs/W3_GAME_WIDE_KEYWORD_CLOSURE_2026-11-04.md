# W3 — game-wide keyword consistency closure — 4 November 2026

Seventh W3 step (client `raft-20261103T153100Z-b4d2c9e7`), pre-announced in [the scope message](../prompt/coordination/discussions/RENDER-002/2026-11-04T123000Z-raft-20261103T153100Z-b4d2c9e7-scope-announcement-game-wide-keywords.md). It lifts the step-4 headline from *priority scope* (1,282 materials on the 11 named targets) to **the entire original game**: every non-engine Material reference outside that priority set is now audited identically.

Inputs: identical 82 byte-authenticated local owners (same pins as the committed inventory); per-shader `m_KeywordNames` sets freshly read in-run; per-material `m_ValidKeywords` subset-checked against its shader's set. New script `scripts/probe_w3_game_wide_keyword_closure.py` (reuses the step-4 module's fail-closed tooling) + 4/4 model tests (prior 9/9, 7/7, 8/8, 8/8, 8/8, 10/10 suites remain green). Real-data run exit 0 with all five negative controls true.

## Headline result — the game-wide claim is now closed by completeness

| Aspect | value |
|---|---:|
| Material references walked | **1,556** (invariant: equals the total original Material count) |
| Engine transport references (fail-closed, never resolved) | 16 |
| Non-engine material references audited | **1,540** |
| Distinct referenced Shader targets aggregated | **77** (11 priority + 66 unnamed, keyed `owner:path_id`) |
| Non-priority materials covered by this step | **258** (across the 66 unnamed targets) |
| Keyword-set violations game-wide | **0** |
| Distinct violation name strings | 0 (aggregated locally only; game-wide commitment field is `null` by the empty-list rule) |

Combined with step 4, the serialized material corpus is now proven **keyword-consistent end-to-end**: for every one of the 1,540 non-engine material→shader references, the material's `m_ValidKeywords` is a subset of its shader's serialized `m_KeywordNames`. Consequence for reconstruction (W1's lane): any ShaderLab variant set carrying a shader's exact serialized keyword set admits **every** serialized material keyword-config in the game — the keyword gate is closed by completeness, not by sampling.

Publishing discipline: the 66 non-priority targets are published without any name disclosure (keys `owner:path_id`; per-target materials/empty-counts/distinct-strings/commitments). The committed artifact was verified programmatically free of keyword/violation name strings (`distinct_violation_names_commitment: null`).

## Limits

Keyword-structure scope only: values/tints/formats remain W2's lanes, program bodies W1's, export/build W4's (their active water-gate/Unity-import run is neither verified nor endorsed here). No visual/GPU/phone claim. **WATER-001/RENDER-002/FFT-FORMAT-009 remain OPEN; game NOT_READY; no immutable candidate; 0/3 reviews.** W3 next options: the 22 empty-config `Standard` materials base-variant audit, or the `StandardVColor` (sharedassets36:880) vertex-color field audit.
