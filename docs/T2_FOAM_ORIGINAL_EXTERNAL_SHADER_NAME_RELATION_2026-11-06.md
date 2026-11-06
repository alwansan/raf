# T2 — original external Shader name relation to original Foam (source-authenticated)

Date: 2026-11-06 UTC. Issue: WATER-001. Agent: T2; `origin=chat`; session `20261106T1714Z-T2-chat-target-foam-name-63f0`.

## Question and source

The earlier [four-original-owner graph](T2_FOAM_ORIGINAL_FOUR_OWNER_SHADER_PPTR_GRAPH_2026-11-06.md) and [manifest target verification](T2_FOAM_EXTERNAL_MANIFEST_PPTR_2026-11-06.md) established two genuine original external `Material.m_Shader` references, one distinct SHA-pinned external original owner, and two typed Shader PathIDs. **Do either of those Shader objects have the exact serialized original Foam Shader name or raw object bytes?** This is different from repeating the already successful target-file/PathID verification.

Immutable original provider: `alwansan/raf@15964ea8f246b6e076ce26b60931ee2e1a9a2385` (ZIP2).
Original `Raft_Data/sharedassets0.assets`: **115978112** bytes, SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`.
Original Foam `Shader` PathID `2420` raw SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`.
Manifest has 366 validated metadata rows representing **declared** 7789295609 bytes. The full data set was **not** downloaded or SHA-verified. The single external target asset (758412 bytes) **was** SHA-checked against its pinned original manifest entry in CI.

## Independently validated original experiment

- Script: `scripts/t2_foam_original_target_name_relation.py`; source-free controls `tests/test_t2_foam_original_target_name_relation.py`; isolated workflow `.github/workflows/raft-t2-foam-original-target-name-relation.yml`.
- Final authentic [Actions 42260338766](https://github.com/alwansan/raf/actions/runs/42260338766) — **SUCCESS**, source commit `bdc3095f7e1445307a719d15b038858982005db2`; 10/10 new and 11/11 inherited source-free tests passed. Original source staging/Shader object authentication, private comparison and all final safe report assertions passed. Safe artifact `13523704013`, `t2-foam-original-target-name-safe-42260338766` (478 bytes).
- Verified **2** original external target Shader objects in one original SHA-pinned source file, both typed and both source-name readable (**2/2**). The exact original `m_ParsedForm.m_Name` matches original Foam `m_Name` in **0/2** cases; original raw Shader object byte identity matches **0/2**.
- No private original Shader names, GUIDs, hashes of individual names, Unity binary payloads, decompiled original HLSL or private files were sent to the public artifact. Only count-only attestation was published; private temporary owner/target source files were removed before upload.

## Diagnostic false positive corrected before final proof

Initial [Actions 42260145863](https://github.com/alwansan/raf/actions/runs/42260145863) completed with **FAILURE** at a **post-comparison report assertion**, although all source and target checks and private comparison succeeded. The assertion treated the substring `private_shader_name` inside the safe boolean key `private_shader_names_or_digests_published` as a forbidden field. The narrowed workflow change at `bdc3095f7e1445307a719d15b038858982005db2` checks forbidden **exact JSON keys** while retaining SHA, count, data-shape, no-source-output and no-GUID claims. Corrected independent CI passed.

## What this proves and what it does not

For the two original material Shader pointers under inspection, **the two target Shader serialized names do not equal the exact original Foam Shader name** and their raw Shader object bytes are different. This supports a precise negative for *these two candidate targets only*. The original Foam source object still exists and is authenticated; the name mismatch does not establish the cause of Android's missing water effects. These Materials may use entirely different Shader objects, and original Foam may be bound elsewhere, dynamically loaded or associated with materials not in this owner.

A filename+SHA+typed PathID candidate and name comparison do **not** independently authenticate Unity external FileIdentifier GUID identity, runtime Material binding, Foam CB0 upload, active Unity ShaderLab pass bindings, FFT/Spectrum/Blur correctness, GPU rendered pixels or Android device acceptance. Do not rewrite any Material/Shader GUID, inject a guessed alias, claim Foam restored, or relabel WATER-001 closed. The separately observed phone artifact [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) demonstrated world entry/save/reopen and still needs water visual restoration.

## Next engineering step

In a *new coordinated scope*, privately authenticate the actual original serialized external GUID/FileIdentifier and owner/Material identity for the two external typed Shader targets. If the GUID does not independently corroborate the basename candidate, mark the edge unresolved rather than replacing an object. After a true original Foam Material/Shader host path is located, trace real CB0 values and pass/sampler bindings, then test Unity/Vulkan and Adreno phone pixels separately. Coordinate Material ownership with T3 and FFT binding with T1. `WATER-001` remains **OPEN**, full game **NOT_READY**.
