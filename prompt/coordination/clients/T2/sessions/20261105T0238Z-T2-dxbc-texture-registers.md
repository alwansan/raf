# T2 20261105T0238Z — direct original Foam DXBC register mapping (start)

Identity: **T2**. Separate session to avoid possible concurrent paused T2 identity; shared T2 state/MEMORY not edited until exclusive session ownership is established. User explicitly requested Continue. No other T clients' files changed.

Baseline HEAD at read: `8397f6ce5bb3fecb5d8a3c82e7e9ba2d38ded810` (2026-11-05T02:28:18Z). No in_progress or queued GitHub Actions. Last game release APK86 `android-early-test-41812889049-1`, CL main `5394407b5cd0a0ca1848ff0902f8d2133bf6ea29`; no new on-phone water success.

Scope: WATER-001 original Foam/Global two passes, four stages. T2 prior authentic CI41942245746 established 21 compiled sampling calls and 6 actual **translated numeric** image/sampler pairs. Original Foam `m_TextureParams` aliases/numeric register identity still unproven. B17 `scripts/b17_spectrum_compiled_bindings.py` already parses authentic DXBC resource declarations and compares serialized indices in Spectrum; reuse its authored parser, no new blind bytecode decoder. B20/B24/B25 provide SHA-authenticated original Foam object/4-stage packet. T2 original resource/name probes preserved.

**Falsifiable plan before edits:** Add a bounded original Foam `m_TextureParams[].m_Index/m_SamplerIndex` vs original D3D11 DXBC `dcl_resource tN` and `dcl_sampler sN` parity verifier, with per-stage source blob SHA pins and explicit positive/negative anti-spoof tests. Where sampler index=-1/unavailable or texture declaration differs, report precise numeric disagreement, not fabricate mapping. Reuse stage_variants/linked_program/compiled_declarations. Numeric t/s parity is distinct from compiled SPIR-V set/binding mapping and original Unity material upload; keep them UNVERIFIED. Execute on ZIP2 SHA-authenticated original in independent low-cost CI; retain no private decoded program/names.

Intended files: `scripts/t2_foam_original_dxbc_registers.py`, `tests/test_t2_foam_original_dxbc_registers.py`, independent workflow `.github/workflows/raft-t2-foam-original-dxbc-registers.yml`, one work/experiment and evidence files under T2. No Unity native request, no touch, audio, Settings, .meta/GUID edits.

Owner/source attribution: B17 DXBC parser; B20/B24/B25 original Foam stage and pass state; T2 prior compiled-use proof. WATER-001 OPEN, NOT_READY 0/3.
