# W3 — unnamed-target schema enumeration: property/texture-slot structure for all 65 remaining targets — 4 November 2026

Ninth W3 step (client `raft-20261103T153100Z-b4d2c9e7`), pre-announced in [the scope message](../prompt/coordination/discussions/RENDER-002/2026-11-04T150000Z-raft-20261103T153100Z-b4d2c9e7-scope-announcement-unnamed-target-schemas.md); completes the serialized schema story across **every referenced shader target in the game**: step 3 published the 11 priority targets' schemas by name, step 8 profiled StandardVColor, and this step closes the remaining **65 unnamed targets** keyed `owner:path_id`. Same 82 byte-authenticated local owners and pins. New script `scripts/probe_w3_unnamed_target_schemas.py` (reuses the shared fail-closed tooling; reproduces the committed step-7 artifact's 77-target reference map in-run and aborts on any mismatch) + 4/4 model tests (all prior suites remain green). Real-data run exit 0 with **8/8 negative controls true**. Artifact: [W3_UNNAMED_TARGET_SCHEMAS_2026-11-04.json](../docs/W3_UNNAMED_TARGET_SCHEMAS_2026-11-04.json) SHA-256 `1ad595423c20f133d67ab76458a3c1e760e758ec97883a674699a2f95559fd4b` (verified name-free — no name keys, no VIOLATION/MISS/EXTRA strings).

## Coverage

| aspect | value |
|---|---:|
| distinct referenced targets verified in-run vs committed artifact | **77 / 77** (fail-closed match, per-target material counts included) |
| previously-published named targets excluded (11 priority + StandardVColor) | 12 |
| unnamed targets schema'd here | **65** |
| material references covered by these unnamed schemas | **240** (of the 258 non-priority references; the 18 StandardVColor ones were step 8) |
| engine transport references (fail-closed pass-by) | 16 |
| owners containing unnamed targets | 13 |

## Aggregated schema profile for the 65 unnamed targets (counts + commitments only)

| dimension | distribution |
|---|---|
| serialized keyword count per target | mode 26 (18 targets) and 27 (16 targets); remaining 31 targets spread 4–33 |
| texture-slot count per target | 0 (6), 1 (15), 2 (7), 3 (4), 4 (11), 5 (12), 6 (3), 8 (1), 9 (2), 10 (4) |
| property-type histogram (all 65 combined) | Texture 229, Float 229, Range 206, Color 73, **unknown 24** |
| targets with zero keywords / zero slots | 0 / 6 |

Every target carries ≥1 serialized keyword. The **24 `unknown`-type properties are the honest fail-closed bucket**: property types outside the documented `m_PropInfo` enum (0=Color, 2=Float, 3=Range, 4=Texture — verified previously against public Standard membership) are counted, not name-guessed, and never produce commitments. Six targets declare **zero** texture slots — their existence is now structurally accounted rather than an open question.

## Step-9 environment note (honesty)

This run used interpreter `/data/data/com.termux/files/usr/bin/python3.14` (UnityPy 1.25.4 — the same pinned version as all prior W3 runs). The host's default `python3` preference changed mid-session and lacks UnityPy; the artifact's `tool_versions.python` records the actual interpreter. Synthetic tests were executed with the same interpreter.

## Limits

Serialized structure only: no property values/colors/tints (W2's lanes), no program bodies or ShaderLab reconstruction (W1's), no build/export (W4's). No visual/GPU/phone claim. **WATER-001/RENDER-002/FFT-FORMAT-009 remain OPEN; game NOT_READY; 0/3 reviews.** With step 9, W3's schema ledger now covers all 77 referenced targets; the next concrete step is the owner-authorized Actions verification lane (see the following step announcement).
