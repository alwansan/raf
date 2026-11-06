# T2 — source-original opaque MonoBehaviour script target provenance (typed SHA join)

Date: 2026-11-06 UTC. Agent T2, origin `chat`, session `20261106T1817Z-T2-chat-original-script-target-5ac9`; issue WATER-001 OPEN.

## Why a second experiment?

The immediately previous [original class-database MonoBehaviour header inspection](T2_ORIGINAL_OPAQUE_MONOSCRIPT_HEAD_2026-11-06.md), [CI42268585593](https://github.com/alwansan/raf/actions/runs/42268585593), proved **55,328** previously opaque `MonoBehaviour` source headers could be read, all `m_Script` references valid, all pointing to **other external source file(s)** and none to the original Foam Shader's `sharedassets0.assets` owner.

That previous result did **not** stage the referenced external script owner or verify a single real script object. The question here is distinct and genuinely necessary: Do the 55,328 m_Script source PPtrs actually resolve to typed `MonoScript` objects in an independently SHA-authenticated source file?

## Immutable source proof and privacy

- Immutable ZIP2 provider: `alwansan/raf@15964ea8f246b6e076ce26b60931ee2e1a9a2385`.
- Original 366-row asset manifest validated with its file sizes and SHA; original 40 scene level assets independently SHA verified, **233237972 bytes**.
- For each opaque source `MonoBehaviour`, read the original-version class database base header, resolve its *actual* serialized `m_Script` external fileID to original external path privately, map its basename **only to a unique original manifest candidate**, and stage the exact candidate provider file under a bounded source budget. Separately SHA-verify the provider's original bytes against immutable manifest, then confirm each source `m_PathID` belongs to an actual original **`MonoScript` object** in that file. The runtime Unity GUID remains **not authenticated** merely by this candidate join.
- Source `scripts/t2_original_monoscript_target_join.py`, regression `tests/test_t2_original_monoscript_target_join.py`, isolated workflow `.github/workflows/raft-t2-original-monoscript-target-join.yml` on ubuntu24.04 with UnityPy==1.25.4, 25-minute maximum, separate no-cancellation concurrency.
- **16/16** adversarial synthetic tests checked duplicate basename ambiguity, unlisted target missing, strict file size/sha/kind validation, bool/negative PathID rejection, typed vs wrong-type object, duplicate referenced IDs, source-reference cardinality and SHA budget skipping.
- The runner deleted all source files, original strings/paths, private GUIDs, typed class names and raw data before uploading the safe count-only artifact. No proprietary source asset or private identifier was published.

## Genuine source result

[**GitHub Actions 42269806221**](https://github.com/alwansan/raf/actions/runs/42269806221) **SUCCESS**, source SHA `91e6df3cca18fb808b6a63538ce60cbefe1e6032`, job `128071119561`. Tests, SHA stage, original-data comparison, finite/privacy assertions, cleanup and safe artifact upload all succeeded.

| Authenticated result | Count |
|---|---:|
| Original level scene files independently SHA checked | **40/40** |
| Original level scene source bytes SHA checked | **233237972** |
| Original opaque MonoBehaviour `m_Script` PPtrs examined | **55328** |
| Unique external file path variants referenced | **1** |
| Script PPtrs with a **unique** original ZIP2 manifest filename candidate | **55328 / 55328** |
| Missing manifest basename candidates | 0 |
| Ambiguous manifest basename candidates | 0 |
| Actual external candidate original serialized files SHA staged | **1** |
| Actual original external target provider bytes SHA checked | **758412** |
| Original script PPtrs checked against typed target object inventory | **55328 / 55328** |
| References resolving to real original typed `MonoScript` objects | **55328 / 55328** |
| References missing original PathID or resolving to non-`MonoScript` objects | **0** |
| Distinct referenced typed `MonoScript` object targets in the single verified provider | **473** |
| Rows excluded because of stage size or file-count budget | 0 |

Count-only safe artifact ID `13529310602` (`t2-original-monoscript-target-typed-safe-42269806221`, 693 bytes).

## What is now proven

All **55,328** previously opaque scene MonoBehaviour records have real Unity-version source base headers whose `m_Script` references point to **473 distinct, source-original typed `MonoScript` object targets** inside **one independently SHA-verified original provider file**.

This is **more than** a filename or guessed assembly-class name: each referenced PathID is present as a real `MonoScript` object of the expected Unity class type, in the precisely reconstructed original asset file. The 758412-byte target source size matches the size independently seen in previous [external Shader candidate work](T2_FOAM_EXTERNAL_MANIFEST_PPTR_2026-11-06.md), but **file identity must be compared directly in private source memory** before claiming the two target paths are the same; size alone does not establish source identity.

The next useful step is to read the SHA-authentic `MonoScript` class/assembly metadata privately, match each to the SHA-pinned original managed assembly schemas, and reconstruct only the necessary custom `MonoBehaviour` fields with the **correct Unity class-database base header alignment**. Then identify the actual water/Foam script-to-material/Shader runtime binding. No original `MonoScript` name, GUID or private source content was published.

This evidence does **not** establish that any of these scripts loads the original Foam Shader PathID2420, creates a Foam `Material`, binds CB0, compiles an original ShaderLab program or renders on Android/Adreno. Original source manifest basename+typed PathID is not independent GUID/Unity runtime resolution proof.

## Trial-build decision

T2's [trial build vote](../prompt/coordination/T_TEAM/TRIAL_BUILD_READINESS.md) in `trial-20261106-r1` remains **«لا يحتاج»** because no substantial tested **integrated** Android water shader/material/CB0 fix exists yet. `WATER-001` stays OPEN and game NOT_READY. No native APK/OBB/XAPK, protected original asset/shader/scene/.meta/GUID, FMOD/Settings/input/touch or another team's jobs/files were changed.
