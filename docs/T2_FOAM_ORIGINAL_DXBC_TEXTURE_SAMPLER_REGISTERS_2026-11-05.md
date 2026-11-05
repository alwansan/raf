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
