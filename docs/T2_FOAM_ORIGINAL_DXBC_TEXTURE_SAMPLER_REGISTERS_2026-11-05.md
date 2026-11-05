# T2 WATER-001 — original Foam Unity texture indices vs genuine D3D11 register declarations

## Result (2026-11-05)

**Real source-authenticated [CI41957269478](https://github.com/alwansan/raf/actions/runs/41957269478) COMPLETED SUCCESS**, 15/15 new anti-spoof/ambiguity tests. Exact original ZIP2 provider `alwansan/raf@15964ea8f246b6e076ce26b60931ee2e1a9a2385`, `Raft_Data/sharedassets0.assets` 115978112 bytes SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`. Exact Foam Shader PathID2420 object SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`, **all four B20 original stage DXBC SHA256 validated individually**.

T2 reused **B17's native DXBC `compiled_declarations`** (not a new speculative decoder), **B24 linked original D3D11 programs**, **B25 name/CB gates** and T2 original `m_TextureParams` data. It matched the actual native DXBC `dcl_resource tN` and `dcl_sampler sN` slot sets against `m_Index/m_SamplerIndex` in each source row. The original source has no explicit `m_Samplers` rows; each of its six Texture rows has an explicit nonnegative sampler candidate. All 4/4 stage comparisons passed exact numeric **register set parity**.

| Original stage | Serialized t/s pairs | Native compiled dcl_resource / dcl_sampler | t parity | s parity |
| --- | --- | --- | --- | --- |
| Pass0 vertex | none | none | yes | yes |
| Pass0 fragment | t0/s0, t1/s1, t2/s2, t3/s3, t4/s4 | t0..t4 / s0..s4 | yes | yes |
| Pass1 vertex | none | none | yes | yes |
| Pass1 fragment | t0/s0 | t0 / s0 | yes | yes |

Each native original DXBC sampler declaration has numeric mode **0** in this bounded source; this does not establish the original Unity sampler filter/wrap parameters. No `m_SamplerIndex=-1` in six observed fragment rows. The source row pair is a plausible original binding candidate, but **declaration-set parity alone does not prove a compiled executable `sample tN,sM` instruction joins the candidate pair**. That separate instruction-use question remains.

### Authorship, integration and private evidence

- [T2 source implementation 37f5f189](https://github.com/alwansan/raf/commit/37f5f1899fefe7a47fb0a90a582437ab1a95a3e3) `scripts/t2_foam_original_dxbc_registers.py`, [15 adversarial tests 36e2f697](https://github.com/alwansan/raf/commit/36e2f697aaa03d5f4436e8331111ccd6d1b3ccaa) and [isolated original workflow c3bc1839](https://github.com/alwansan/raf/commit/c3bc183901411fefc0ec3a977e0ea27ef07c11fc) (no native Unity, zero LFS pulls, private source erased on success/failure).
- Numeric only artifact **13384056820**, ZIP SHA256 `6523865257841c0c73b3d82b5c2e5ce276a618806def78b514298e61dd3981b0`, verified by independent file inspection. No private game code, names, DXBC, HLSL or SPIR-V uploaded.
- Previous authentic T2 [SPIR-V sampled-image uses CI41942245746](https://github.com/alwansan/raf/actions/runs/41942245746) established 21 **translated** sample calls/six numeric pairs: pass0 image b6..10 ↔ sampler b1..5, pass1 b2↔b1. The translation *numeric* mapping from native original DXBC t0..t4 / s0..s4 to those SPIR-V set/binding values is **not directly proven by this new DXBC declaration comparison** and must not be asserted solely from ordering or offset. Source symbol equality to SPIR-V image names is **0/6** per [original CI41941354379](https://github.com/alwansan/raf/actions/runs/41941354379).
- Unity ShaderLab authored property map, material upload, shader passes actually imported/rendered, original sampler states and Adreno pixels are **unverified**. Last device game APK86 predates current source proof. WATER-001 **OPEN**, project **NOT_READY (0/3)**, audio/Settings unchanged and touch/layout deferred.

### Next

Inspect real original DXBC executable `sample` instructions and t/s register operands (reuse pre-existing `blur_sample_operands.py` when supported), reject unsupported opcode/dynamic resource index rather than assuming declarations are used. Then verify native register to translated SPIR-V binding identity with explicit translation provenance, map source property/Material upload, reconstruct private two-pass ShaderLab and validate Unity/GPU/Android separately.

## Follow-up: genuine executable DXBC SAMPLE instruction-use proof (2026-11-05)

**[Original CI41958159556](https://github.com/alwansan/raf/actions/runs/41958159556) COMPLETED SUCCESS**, source commit [faed3a4a](https://github.com/alwansan/raf/commit/faed3a4a57d4113e0bcf907461a9d25baf4469af): **15/15 declaration controls + 16/16 new SAMPLE operand/unsupported-opcode controls PASS**, original ZIP2 `sharedassets0.assets` SHA authenticated and four exact original stage SHA pins. Added [T2 native instruction scanner](https://github.com/alwansan/raf/blob/feature/android-native-port/scripts/t2_foam_original_sample_edges.py), reusing **the inherited `scripts/blur_sample_operands.py` decoder** and exact native source row t/s register pairs; compiler tokens bounded, dynamic/modified or unowned t/s reference rejected.

| Original stage | Genuine native DXBC opcode69 SAMPLE calls | Distinct actively used original numeric pairs | Unsupported sample variants (70–74) |
|---|---:|---|---:|
| Pass0 vertex | 0 | none | 0 |
| Pass0 fragment | **17** | **t0/s0, t1/s1, t2/s2, t3/s3, t4/s4** | **0** |
| Pass1 vertex | 0 | none | 0 |
| Pass1 fragment | **4** | **t0/s0** | **0** |

**21 native DXBC SAMPLE calls / 6 distinct active native pairs**. All six original `m_TextureParams` row candidates were actually used by SAMPLE opcode69 in the appropriate original fragment stage; vertex stages contain none. No unhandled DXBC SAMPLE variants 70–74 observed in these four original stages. This is **not just declaration parity**. Earlier independently authenticated [translated SPIR-V use CI41942245746](https://github.com/alwansan/raf/actions/runs/41942245746) found **17+4=21** translated sampling calls and six compiled image/sampler pairs, with pass0 b6→b1 through b10→b5 and pass1 b2→b1. This identical scoped cardinality/usage is strong parallel evidence but not a per-resource **native DXBC tN/sN ↔ compiled SPIR-V descriptor/binding identity proof**. Neither shader register numbering nor ordering alone proves a Unity Material shader property, source sampler state, ShaderLab import or device pixel equivalence.

New safe numeric artifact ID **13383159040**, ZIP SHA256 `14f55dd06ca25aa4d1cb83f70ff3ad37d8f2b861758007f82294e1009ca86bbb`, independently downloaded and inspected. No proprietary symbols, DXBC or HLSL/SPIR-V uploaded. Private original staged source deleted by workflow even on failure. Source-only; **WATER-001 remains OPEN, NOT_READY 0/3**, real game latest APK86 unmodified. Other T clients' workflows, audio, Settings and deferred touch unchanged.

**Next necessary proof:** authenticate native t/s resource → translated SPIR-V descriptor identity, including CB offset/separate sampler remapping and sample operands; map actual original Material shader properties and texture/sampler upload. Only then construct/install an authentic two-pass Foam ShaderLab and validate Unity import, numeric GPU/pixels and device on a new build. No fake property aliases or claimed visual restoration.
