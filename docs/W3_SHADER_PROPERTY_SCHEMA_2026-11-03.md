# W3 — serialized property/keyword schema of the appearance-priority original Shaders — 3 November 2026

Third W3 engineering step in this cycle, pre-announced in [the scope message](../prompt/coordination/discussions/RENDER-002/2026-11-03T165000Z-raft-20261103T153100Z-b4d2c9e7-scope-announcement-shader-prop-schema.md) and deliberately non-overlapping with W1 (shader programs/pass bodies, Unity compilation) and W2 (external-pointer corroboration, texture formats/sRGB/color-space, material color settings).

Inputs: the same byte-authenticated local PC originals; both pinned owners (`resources.assets`, `sharedassets0.assets`) re-verified by SHA-256 before parse; every priority target's identity re-asserted by exact `m_ParsedForm.m_Name` match against the committed inventory. No LFS, no Unity, no CI claimed — reproducible locally.

## Verified serialized type mapping (this Unity 2021.3.45f2 schema)

`m_PropInfo.m_Props[].m_Type`: **0 = Color** (verified members), **2 = Float**, **3 = Range** (verified against the publicly known Unity `Standard` schema: `_Cutoff/_Glossiness/_Metallic/_Parallax/_OcclusionStrength/_GlossMapScale` — an exact 6/6 membership match for sharedassets0:2398), **4 = Texture** (all type-4 members carry `m_DefTexture`; 9/9 membership match for `Standard`). Raw histogram values are retained; *nothing was silently re-labeled*. The lazy first attempt with a wrong type-3 assignment was corrected **before publication** — the superseded scratch run is not a durable artifact.

## Schema result — 11 priority targets, all identity-exact

| pathID | Shader | props | Color | Float | Range(3) | Texture | keywords |
|---:|---|---:|---:|---:|---:|---:|---:|
| 2398 | `Standard` | 27 | 2 | 10 | 6 | 9 | 37 |
| 2416 | `Skin_Amplify` | 13 | 1 | 1 | 5 | 6 | 27 |
| 2445 | `Shimmer` | 13 | 1 | 4 | 3 | 5 | 27 |
| 2424 | ` BlockPaint` | 35 | 5 | 6 | 18 | 6 | 27 |
| 2405 | `Nature/SpeedTree8` | 17 | 3 | 5 | 5 | 4 | 38 |
| 2426 | `ParticleShader` | 12 | 1 | 4 | 5 | 2 | 9 |
| 2414 | `Tri-Planar` | 16 | 2 | 4 | 5 | 5 | 27 |
| 2439 | `Vegetation` | 16 | 1 | 3 | 8 | 4 | 27 |
| 2417 | `ParticleShader_Additive` | 7 | 1 | 3 | 1 | 2 | 8 |
| 2451 | `AnimalDissolve` | 17 | 1 | 4 | 3 | 9 | 26 |
| 2440 | `FireParticles_Amplify` | 13 | 1 | 4 | 6 | 2 | 9 |

Engineering readings (aggregate only, names stay as SHA-256 list commitments inside [the artifact](W3_SHADER_PROPERTY_SCHEMA_2026-11-03.json), SHA `7a698ec263d9cf5509c1c6aa320637127f31287123bd00b52f88b621f7758a8b`):

- **Keyword budget is now bounded per shader** (8–38 names). Any ShaderLab reconstruction must carry the shader's exact serialized keyword set, or its variant enumeration is not the original's (direct input to W1's Unity compile gate and to Android Vulkan variant costs).
- `Standard` (2398): the full public-Unity property layout confirms the game ships an actual built-in `Standard` — 9 texture slots, `_Mode`/`_SrcBlend`/`_DstBlend` blending present; A12's vendor identity match is directly extendable here.
- ` BlockPaint` (2424): 35 props/6 texture slots — strongest bespoke painting-appearance shader; leading-space authentic name.
- Fire/particle chain (`FireParticles_Amplify` 2440, `ParticleShader` 2426, `ParticleShader_Additive` 2417): small keyword sets (8–9), 2 texture slots each, 1 color each — compact restoration targets with high visual impact.
- `AnimalDissolve`/`Skin_Amplify` confirm the Amplify-family dissolution/character appearance parameters (3–9 textures, small float sets).
- `m_ParsedForm.m_Dependencies` is 0 for all 11 targets — no parsed dependency links to other shaders; any shader-fallback behaviour (e.g., `m_FallbackName`) remains unparsed and is *not* claimed.

## Evidence and controls

- Script: `scripts/probe_w3_shader_property_schema.py` (identity-exact target check, fail-closed identity mismatch/missing target/type-bucketing controls; `--print-names-local` echo flag for local binding work — names never commit to repo/artifacts).
- Model tests: `scripts/w3_test_shader_property_schema.py` — **8/8 OK** local (type mapping, unknown-type rejection, missing-name fail-closed, deterministic sorted commitments, keyword/dependency commitments, non-string dependency rejected). Previous 9/9 and 7/7 suites remain green.
- Real-data run exit 0, all three negative controls true (identity mismatch, missing target, unknown-type bucketing).
- Aggregate artifact committed at `docs/W3_SHADER_PROPERTY_SCHEMA_2026-11-03.json`.

## Limits

Schema/commitment scope: no property *values* of materials (W2's colors lane), no shader program bodies (W1's lane), no texture payload/format audit (W2's format/sRGB lane), no GPU/Unity/phone claim; WATER-001/RENDER-002/FFT-FORMAT-009 OPEN, NOT_READY, 0/3 reviews unchanged. Per-shader actual keyword *usage flags* (m_KeywordFlags semantics) are counted but not interpreted beyond name counting.
