# T3 — actual AssetRipper same-instance original Particle108 Material/Texture export linkage

**Verdict: GENUINE BOUNDED SAME-INSTANCE EXPORT COMPARISON COMPLETE; 5/5 Material21, 2/3 Texture2D28 trace, 9/10 exact TexEnv PPtrs, 10/10 UV. RENDER-002 OPEN / NOT_READY. Android GPU pixel fidelity unverified.**

## Actual authoritative CI — not a synthetic-only run

- [GitHub Actions 42130529677](https://github.com/alwansan/raf/actions/runs/42130529677) **COMPLETED SUCCESS** on exact workflow/source commit `7a8833bfa46c141618df76204d2cf88101c8df36`; source-free 93 Python tests passed (9 new same-instance join + 84 inherited).
- Pinned immutable ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; SHA-authenticated original six scene assets plus exactly four Material/Shader owner files and two runtime global provider assets (12 total source files). Source ParticleShader48 target privately selected from 108 scene Particle Renderer material slots / five Material21 originals / three Texture2D class28 originals; 10 exact source local Texture PPtrs.
- ONE externally streamed original .resS provider selected by the three `m_StreamData` objects; its full bytes/size/SHA verified from immutable ZIP2 in this SAME run, with all three original source spans read. No game archive bytes uploaded.
- Exact public AssetRipperCLI source commit `036098ab525a3f9f693dc101edeb21faad4d32d8` compiled with W1 Material21, B02 Texture2D28 and optional B21 Light private tracing via the reviewed C# helper. ONE actual exporter invocation produced both W1 and B02 traces sharing the SAME `export_instance`; actual ExportedProject Unity Material YAML parsed using B05 duplicate-key-protected parser.

## Real original-source→same-export result

| Precisely source-authenticated particle shader scope | Actual bounded result |
|---|---:|
| Original targeted ParticleSystemRenderer Material slots | 108 |
| Distinct original Material21 source objects | 5 |
| Distinct original Texture2D class28 source targets | 3 |
| Original Material m_TexEnvs entries | 10 |
| Original selected Material21 objects present in W1 same-export trace | **5 / 5** |
| Source Texture2D28 objects present in B02 same-export trace | **2 / 3** |
| Source Material21 objects with actual exported Material YAML | **5 / 5** |
| Original TexEnv slot labels preserved in exported Material YAML | **10 / 10** |
| Original→export exact class28 Texture PPtr matches | **9 / 10** |
| Source links with target missing from B02 source→export trace | **1** |
| Source Texture non-null became null after export | **0** |
| Bound source links resolved to wrong exported GUID | **0** |
| Source TexEnv UV scale+offset values preserved | **10 / 10** |
| Extra exported TexEnv slots on selected Materials | **0** |
| Export GUID collision in selected scoped Material or Texture trace | **0** |

**Interpretation:** One original source Texture2D28 target has no record in this bounded B02 trace, leaving one of the ten source TexEnv GUID bindings unproven. The exported Material YAML still contains the slot and nonnull pointer, but this source-specific verifier cannot authenticate it as the expected exported Texture2D. The other nine were exactly matched by original source owner/pathID→same-instance exported GUID/fileID/type and actual Material YAML; all ten UV values matched.

This is a genuine **scoped export trace identity deficit**, NOT proof that the missing texture is absent from a full Unity build or signed Android APK/OBB. The original T3 source three Texture2D28 were verified from full-SHA streaming bytes in [source CI42125608932](https://github.com/alwansan/raf/actions/runs/42125608932); source input availability is no longer the blocker. B02's reviewed instrumentation explicitly skips `collection.Exportable=false` Texture2D objects; whether that applies to this one source target is currently **unverified**, so do not assert it as the cause without another private collection-classification probe.

## Code and private guards

- `scripts/t3_original_particle_material_texenv.py` adds a caller-owned PRIVATE `private_material_texenvs` outparam, valid only for the exact SHA-source graph / five Material objects / ten slot labels. No original source names, labels or PathIDs in outputs.
- `scripts/t3_particle_same_export_bindings.py`: exact source-only 5 Material→3 Texture join through B05's `_slot`, W1+B02 strict `export_instance` gate, source-origin `(owner,PathID)` and real YAML `m_TexEnvs`; counts missing trace, null, wrong target, UV drift separately. Public aggregate is fixed numeric allowlist; no game IDs, GUIDs, HLSL, original bytes or actual private trace uploaded.
- `tests/test_t3_particle_same_export_bindings.py`: nine independent synthetic controls for same-export match, cross-export contamination rejection, missing Material/Texture traces, null and wrong GUID, UV/slot drift, duplicate identity/collision, source scope changes. Initial runs [42130208972](https://github.com/alwansan/raf/actions/runs/42130208972) and [42130365900](https://github.com/alwansan/raf/actions/runs/42130365900) failed **only** on synthetic fixture owner assumptions before any original export; fixtures corrected to original Material21 owner set, then CI42130529677 passed.
- `.github/workflows/raft-t3-particle108-sameexport.yml`: isolated on-own-file push only/manual dispatch, concurrency cancel false, 50 minute cap, source-specific staged bytes plus optional private capture, safe anonymous artifact only. Does not cancel T5, launch a native Unity APK/OBB build or alter game assets.

## Next source-export causal probe

Trace the EXACT unrecorded third original Texture2D28 privately: inspect whether the original object is present in any AssetRipper export collection, and whether `collection.Exportable=false` (B02 intentionally skips such objects), or another reason prevented tracing it. Prefer a privacy-preserving **source-ID-level nonexportable/omitted classification** in the disposable B02 helper rather than guessing a name or GUID. If present but nonexportable, inspect the actual exported Material's nonnull `m_TexEnvs` PPtr and classify its GUID target through a documented native built-in/engine mapping. If absent from exporter graph, investigate original stream importer and export scope; avoid forcing a dummy image/opaque placeholder. Coordinate same-instance full-native T5 build and phone test to establish actual square-fire/smoke GPU cause.

**No game shader, `.meta`, prefab, asset, water, FFT, sound, Settings, input, saved world, APK, OBB or user device file was modified. The 1/3 trace deficit does not establish Android device failure. RENDER-002 stays OPEN.**
