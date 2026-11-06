# T3 chat — diagnosing five Particle108 Material exported-YAML parser

- **session_id** `20261106T1515Z-T3-chat-5mat-yamlphase-e73b`, **origin** `chat`, issue `RENDER-002` **OPEN / NOT_READY**.
- **base_sha** `9a109902fefcff43945ccc141cf762ce7a44876b`; scope registered before edits at `prompt/coordination/work/RENDER-002/20261106T1515Z-T3-chat-5mat-yamlphase-e73b.json`, initial commit `71212a9a6f8c710b8a5064f5a3b48f0f190f1326`.
- **resumed_from_sessions** `20261106T1350Z-T3-chat-particle108-5mat-valuediff-d4e9` (5 source Particle Material RGBA/binary32 comparison INCONCLUSIVE), `20261106T1429Z-T3-scheduled-native-dummy-audit-a83f` (read-only native shader dummy audit), `20261106T1337Z-T3-chat-particle108-propstate-62fb` (original 13 authored properties+one Pass).
- **Prior actual evidence:** same source [42230103847](https://github.com/alwansan/raf/actions/runs/42230103847) failed `EXPORTED_RGBA_YAML` after 5 selected original Material↔export texture PPtr matching. This is a verifier/parser failure, **not yet proof of source RGBA or Float32 changes**. The exact selected original 108-use ParticleShader48 remains an exporter Dummy after TMP/PostFX/volumetric ([42223071341](https://github.com/alwansan/raf/actions/runs/42223071341)).
- **Parallel clients:** no T1 FFT, T2 Foam, T4 local/input, T5 packaging sources touched. T3 scheduled audit `1429Z` is a separate read-only track. T3 paired HLSL `1223Z` reserved files untouched.

## Completed new source-free controls

Restored `.github/workflows/raft-t3-particle108-sameexport.yml` to **manual-only** at commit `c2d1d93c96e47c0e60551395380da2e93327d560`, preventing unnecessary expensive exporter executions during debugging.

- `scripts/t3_particle108_sameexport_values.py` now has a separate allowlisted `PrivateDocumentError` with reason codes for the selected YAML document identity, missing/duplicated selected documents, malformed YAML, missing saved properties or colors, and RGBA vs Scalar encoding; commit `150d0fb6758b8bd8d71a1b306f99cd774b4a47e6`.
- `tests/test_t3_particle108_sameexport_values.py` now has **21 source-free tests** including sanitized selected-only YAML error codes. An intermediate run [42241928090](https://github.com/alwansan/raf/actions/runs/42241928090) failed two obsolete test message substrings (not real source); corrected them at commit `1da04e01ef6b71c55fb60d33395357f8ac6f0598`. Final [**CI 42241999485 SUCCESS**](https://github.com/alwansan/raf/actions/runs/42241999485) on that SHA. No proprietary source material values or identity strings in the new public reports.

## Pending genuine-source gate

One bounded original SHA-pinned W1+B02 same-instance export is necessary to classify which **selected Material YAML parser stage** actually fails, now that the source-free categories are verified. The original ZIP2 source is SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, 6 scenes and four shader/Material owners with one original texture stream; AssetRipper `036098ab525a3f9f693dc101edeb21faad4d32d8`. Expected output is `t3-particle108-values-safe.json`, with `safe_phase` and `safe_document_reason` only on an inconclusive path. **No device, Unity import, source shader restoration or Material patch is claimed**. Before ending cycle record exact run link/conclusion and keep work status waiting_ci until actual result is known.

**Next:** after real safe reason is known, fix only a proven source/extract format discrepancy; do not mask actual changes or force matches. The initial exact source selected 5 Material shader hasn't been made a functioning Android shader and device emitter identity remains unverified.
