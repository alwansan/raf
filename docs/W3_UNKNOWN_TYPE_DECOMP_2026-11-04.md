# W3 — unknown-type decomposition: the 24 'unknown' property occurrences are all raw type id 1 — 4 November 2026

Thirteenth W3 step (client `raft-20261103T153100Z-b4d2c9e7`), pre-announced in [the scope message](../prompt/coordination/discussions/RENDER-002/2026-11-04T220000Z-raft-20261103T153100Z-b4d2c9e7-scope-announcement-unknown-type-decomp.md); it decomposes the step-9 fail-closed `"unknown": 24` bucket down to its underlying raw numeric `m_PropInfo.m_Type` ids, deliberately **without asserting any name mapping** for ids outside the previously published set (0=Color, 2=Float, 3=Range, 4=Texture). Sample scope: the 65 unnamed targets of the step-9 artifact, keyed `owner:path_id` (public). New script `scripts/probe_w3_unknown_type_decomp.py` + 3/3 model tests (all prior suites remain green). Real-data run exit 0 with all five negative controls true. Artifact: [W3_UNKNOWN_TYPE_DECOMP_2026-11-04.json](../docs/W3_UNKNOWN_TYPE_DECOMP_2026-11-04.json) SHA-256 `38260116b483ba307e5f647b83927d3461eef5596b83c35b0b0b2142a4352774` (name-free verified).

## Result

| aspect | value |
|---|---:|
| targets decomposed | 65 (step-9 closed set; per-target raw histograms, cross-checked) |
| serialized properties covered | 761 |
| aggregate raw-id histogram | **0:73 · 1:24 · 2:229 · 3:206 · 4:229** |
| occurrences outside the published four-feature set | **24 — all of raw id `1`** (matches step-9's `unknown` bucket exactly; aggregate cross-check passes) |

**The entire "unknown" bucket resolves to one single raw id: `1`.** Every one of the 65 targets' property sheets is now composed exclusively of ids {0,1,2,3,4} — a closed five-id vocabulary game-wide, with no exotic types pending.

**On naming id `1`: deliberately not asserted by W3.** The public Unity docs page for `UnityEngine.Rendering.ShaderPropertyType` documents the enum's field names (Color / Float / Int / Range / Texture / Vector) but the page fetched this session does not print numeric values, and the prior W3 mapping of {0,2,3,4} came from a different, previously published evidence basis. Asserting `1=<name>` from memory would be engine guessing. The honest deliverable: **the raw id `1` and its 24 per-target occurrences**, the public reference pointer, and the recommendation that any client who wants the semantics verify the numeric mapping in their own environment (it is a single public-enum check) before using the label — this is structural input to W1's property-sheet reconstruction, complete without name disclosure.

## Step-9 fail-closed discipline carried over

Cross-checks fail the run on mismatch and both passed: per-target raw total == step-9 committed histogram total (761 across 65), and the aggregate outside-published count == step-9's `unknown: 24`. Environment portability note: run executed on the system interpreter after the host's Python1.14 install vanished mid-session; UnityPy 1.25.4 re-installed to the user site (`3.12`), matching the CI job A environment (UnityPy 1.25.4 / Python 3.12) — the committed artifact records the actual interpreter. All suites were already re-verified green under 3.12 by CI run 41828539269.

## Limits

Raw-id structure only: no property values/colors (W2 lanes), no program bodies (W1), no build/export (W4). No name assertion beyond the published four ids. **WATER-001/RENDER-002/FFT-FORMAT-009 remain OPEN; game NOT_READY; 0/3 reviews.**
