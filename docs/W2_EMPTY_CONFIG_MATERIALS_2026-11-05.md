# W2 — Empty-config (base-variant) materials census: exact reconciliation with W3's 22/674 — 5 November 2026

Fourteenth W2 counters lane (client `raft-20261103T152008Z-92502b76`). This is the owner-authorized takeover of **W3's announced but unclaimed option** "the 22 empty-config `Standard` materials base-variant audit" ([his step-6 report closed with exactly these two options](W3_SAVEDPROPS_SLOT_COVERAGE_2026-11-04.md), and his per-material keyword report supplies the ground truth: 22/674 Standard references run with an empty `m_ValidKeywords` list = the base keyword configuration). W3 stands by awaiting a peer-announced lane; this delivery executes the audit at the W2 count level and hands him the reconciliation, keeping his keyword-structure ownership untouched.

Inputs: the identical 82 byte-authenticated local owners this program has used since ring 10, every owner verified against commit HEAD via `git show` bytes (`verify_and_hash`). New script `scripts/probe_w2_empty_config_materials.py` + 5/5 fail-closed synthetic tests. Real-data run exit 0.

## Definition grounding (no ambiguity left)
- **empty-config = `m_ValidKeywords` is an empty list.** This is W3's own definition in his per-material keyword usage report; it is used verbatim.
- **Shader identity lives in `m_ParsedForm.m_Name`.** The top-level serialized `m_Name` is `''` for every Shader in this build — a resolution sink this lane documents and tests (the index would otherwise resolve every material to an unnamed shader).

## Headline result — the triple reconciliation is exact
| Metric | W3 census | W2 re-run |
|---|---|---|
| Standard shader identity | `sharedassets0.assets:2398`, 674 material refs | 674 Standard references |
| Standard base-variant | 22 (empty `m_ValidKeywords`) | **22** |
| Other keyword-empty families | Skin_Amplify 208, Shimmer 96, ' BlockPaint' 87 (leading space) | identical (208/96/87), plus ParticleShader 42, Tri-Planar 30, Vegetation 29, ParticleShader_Additive 26, AnimalDissolve 23 |

Game-wide materials classified: **1,556** across the 82 owners (consistent with ring 9's scalar census). 16 shader refs resolve through the documented external buckets and are counted, never guessed.

## The 22 base-variant materials — shape, not content
All published as counters (owner names of serialized files are public paths):
- **Owner distribution:** sharedassets0 12, sharedassets36 2, sharedassets6 2, sharedassets1/11/24/32/34/35 1 each. The two real empty-config materials this lane's earlier diagnostic run found in sharedassets1.assets are consistent: exactly 1 of them is a Standard base-variant.
- **Every one:** `m_CustomRenderQueue = -1` (22/22), `m_InvalidKeywords` size 0 (22/22), `m_DoubleSidedGI` off (22/22).
- **Lightmap flags:** 21 at 4, 1 at 5. **Instancing:** 12 off, 10 on — the only feature-split among the 22.
- **Texture emptiness split:** 17/22 have **all Standard texture slots null** (pure factory default), 5/22 have **some slot bound** — i.e. textures matter for appearance even where the variant is base.
- **Serialized record byte-length shape invariant:** base-variant records occupy the 904–944B range (904×5, 908×5, 912×3, 916×1, 936×2, 944×1) while configured records mass at 924–960B (952×139, 948×107, 956×93, 924×85, 960×75). A loader can therefore distinguish base-variant from configured Standard materials from record shape alone, without decoding a single property.

## Publishing discipline
Counters, booleans, byte lengths, and engine-metadata shader-name identities only. No material names, no path IDs, no keyword strings, no texture/color values. The probe is leak-guarded against `m_Texture`/`m_Color`/`m_Scale`/`m_Offset`/`m_ParsedForm`/`m_Floats`/`m_TexEnvs` keys in its own JSON, and CI runs the 5-test synthetic suite before any real data is touched.

Scope line unchanged: count level only — W3's keyword-structure ownership, W1's program bodies, W4's export/build lanes remain untouched. No visual/GPU/device claim. **WATER-001/RENDER-002/FFT-FORMAT-009 remain OPEN; game NOT_READY; no immutable candidate; 0/3 reviews.**
