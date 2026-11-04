# W3 — fallback / custom-editor enumeration for every original Shader — 4 November 2026

Fifth W3 engineering step in this cycle (client `raft-20261103T153100Z-b4d2c9e7`), pre-announced in [the scope message](../prompt/coordination/discussions/RENDER-002/2026-11-04T100000Z-raft-20261103T153100Z-b4d2c9e7-scope-announcement-fallback-editor.md). It closes the explicit caveat printed in the step-3 report: "`m_FallbackName`/`m_CustomEditorName` enumeration is NOT claimed" — it is now claimed and delivered, with the same evidence class as every prior W3 artifact.

Inputs: the identical 82 byte-authenticated local PC owners (same pin checks as the committed inventory). Coverage: **all 165 original Shader objects** (count invariant asserted against the committed inventory, all four negative controls true). Real-data run exit 0, local CPU, UnityPy 1.25.4 / Python 3.14.8.

## Aggregate result (names published as SHA-256 sorted-list commitments only)

| Aspect | count | distinct commitments |
|---|---:|---|
| `m_ParsedForm.m_FallbackName` non-empty | **52 / 165** | **10** distinct — list commitment `8cfe2c94c22e6d2dad7d771a4b00afddabcc2eb949f222f4e65d670ee8a4f0c4` |
| `m_ParsedForm.m_CustomEditorName` non-empty | **69 / 165** | **10** distinct — list commitment `4b0df3531b6f7e9791c0e5a40a7a9570810afb24b82f8b11a74ca182950ed628` |
| Fallback-empty shaders | 113 | — |
| Custom-editor-empty shaders | 96 | — |

Name-free structural multiplicity profiles (descending counts per distinct value):

- Fallback: **[37, 4, 3, 2, 1, 1, 1, 1, 1, 1]** — one dominant fallback value covers 37 shaders; the remainder are near-unique.
- Custom editor: **[42, 8, 7, 3, 3, 2, 1, 1, 1, 1]** — one dominant editor value covers 42 shaders.

## Engineering reading (class-level, no raw names)

Three identity classes are reproducible from the profiles plus prior W3 evidence, **without publishing a single new name string**:

1. **Vendor-tool lineage is confirmed structurally.** The step-3/step-4 evidence already named vendor-family shaders (`*_Amplify`, MicroSplat/Terrain `Hidden/` names published in the inventory's priority set, SpeedTree8, TextMeshPro). The dominant custom-editor value (42 shaders, 8, 7, 3) aligns with exactly those vendor families (Amplify-class, MicroSplat-class, SpeedTree-class, TMP-class, plus the built-in-family remainder) — i.e., the game's bespoke appearance shaders carry real third-party toolchain edit-time identities, which explains at least one 140-file AssetRipper export failure mode (editor-only references with no runtime resolvers).
2. **Fallbacks are sparse and concentrated.** 113/165 shaders carry no fallback at all: for those, a failed shader load is a hard failure with no graceful degradation path. Where fallbacks exist, one value covers 37 shaders and the long tail is near-unique — reconstruction must reproduce fallback *presence* faithfully since the material population references both shapes.
3. Both distributions are small (10 distinct each) — the full lists are two SHA-256 verdicts that any reconstruction (or any peer's name-table export) can verify locally without re-hashing the 7.3 GB data.

## Evidence and controls

- Script: `scripts/probe_w3_shader_fallback_editor.py` (identity `extract_identity` pure-extractor with non-string rejection; empty strings never committed; `--print-names-local` echo stays local; the default emit is **name-free**: raw name-keyed histograms are only available on the local echo path). Honest correction note: a first run emitted name-keyed histograms into the would-be durable artifact — caught by the leak check before any commit, emptied to name-free multiplicity profiles, and re-run; the corrected artifact is the only durable one (both runs exit 0, identical totals).
- Model tests: `scripts/w3_test_shader_fallback_editor.py` — **8/8 OK** (extractor type/emptiness discipline, empty-string commitment rejection, dedup, name-free + sum-invariant multiplicity profiles). Prior suites 9/9, 7/7, 8/8, 8/8 remain green.
- Durable artifact: `docs/W3_SHADER_FALLBACK_EDITOR_ENUM_2026-11-04.json` — SHA-256 `47b2ba67eabc0f2686a9406cfde3c4ddd19b583e972003c43bad5ed07e2b6f3e`, programmatically verified to contain **zero** of the locally-known name strings (leak check against the step-3/step-4 local-echo vocabulary).

## Limits

Identity-metadata enumeration only: no material property values (W2's lane), no program bodies/default values (W1's lane), no build/export tooling (W4's lane — the overnight experimental build/run by another client is explicitly out of W3's scope and is neither verified nor endorsed here), no visual/GPU/phone claim. WATER-001/RENDER-002/FFT-FORMAT-009 remain OPEN; game NOT_READY; no immutable candidate; 0/3 reviews. Next W3 options: the 22 empty-config `Standard` materials base-variant audit, an `m_SavedProperties` slot-binding completeness audit *restricted to slot-name-level structure* (leaving W2's texture-value lane untouched), or the `StandardVColor` vertex-color field audit.
