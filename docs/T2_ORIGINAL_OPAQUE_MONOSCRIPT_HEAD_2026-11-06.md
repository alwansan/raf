# T2 — original opaque MonoBehaviour built-in header and m_Script source lineage

Date: **2026-11-06 UTC**; owner `T2`, `origin=chat`; session `20261106T1808Z-T2-chat-monohead-script-links-42a7`; issue `WATER-001`.

## New original-source question

The previous [original 40-level scene PPtr census](T2_FOAM_ORIGINAL_40_LEVEL_SCENE_COMPONENTS_2026-11-06.md) SHA-verified 233237972 bytes, inspected 240961 selected components and fully parsed 185633, leaving **55328** unsupported/opaque components. That missing coverage prohibits any claim that the game's original Foam Shader is unused in all scenes.

This experiment reads **only the Unity-version class-database base MonoBehaviour header**, independently of custom serialized script fields or dynamically generated type trees, to recover original `m_Script` (`m_FileID`, `m_PathID`) pointers from those opaque components and identify their actual serialized source-owner category. No original scripts, object identifiers, private names, GUIDs, raw bytes, scene metadata or secret name digests are exported.

The distinction matters because UnityPy 1.25.4 custom/generated MonoBehaviour type trees can disagree with the original class database's `m_Script` alignment in some versions; do **not** trust an unvalidated generated header or modify original data to make a generated tree parse.

## Original immutability and tests

- SHA-locked ZIP2 `alwansan/raf@15964ea8f246b6e076ce26b60931ee2e1a9a2385` (never modified).
- Privately staged and individually SHA-authenticated **40 original level scenes** = **233237972 bytes**, plus independently SHA-authenticated original Foam owner `Raft_Data/sharedassets0.assets` = **115978112 bytes**, **349216084 bytes** total source. Exact prior 40-scene corpus counts independently checked during execution.
- The original Foam owner contains **zero original objects of type `MonoScript`**; this does **not** imply scripts are missing or invalid, only that scripts must be looked up in their actual external owner(s).
- Source: `scripts/t2_original_opaque_monoscript_head.py`; source-free adversarial tests: `tests/test_t2_original_opaque_monoscript_head.py`; isolated pinned workflow `.github/workflows/raft-t2-original-opaque-monoscript-head.yml`, Ubuntu24.04 / UnityPy1.25.4 / 25-minute maximum job / no cancellation of other workflows.
- **19/19** source-free controls cover base header type/boolean spoof, malformed and out-of-range script PPtrs, wrong owner/local PathID false positives, nonzero/zero script IDs, typed `MonoScript` matching, unknown source target and source count completeness. Original runner cleanup precedes safe artifact upload.
- Initial [CI42268476115](https://github.com/alwansan/raf/actions/runs/42268476115) **FAILED before original source checkout** due to a *synthetic test fixture only* passing `{}` (dict) rather than `set()`. Fixed the fixture in source commit `40d42257dbfaf237e3060b043bbb599e9cdd9903`; no source application/loader fix was needed to pass.

## Proven source result

[**CI42268585593**](https://github.com/alwansan/raf/actions/runs/42268585593) **SUCCESS** at test-fix SHA `40d42257dbfaf237e3060b043bbb599e9cdd9903`, job `128066916885`. 19/19 tests, authentic 41-source SHA checks, private built-in header inspection, finite safe assertion and private source cleanup passed. Count-only safe artifact `13527627106` (`t2-original-opaque-monoscript-header-safe-42268585593`, 748 bytes).

| Genuine source data | Observed |
|---|---:|
| Original scene files SHA verified | 40/40 |
| Original scene bytes SHA verified | **233237972** |
| Original Foam owner bytes SHA verified | **115978112** |
| All source bytes SHA verified | **349216084** |
| Scene components selected | 240961 |
| Previously fully parsed component records | 185633 |
| Previously opaque component records | **55328** |
| Opaque records that were genuine MonoBehaviours | **55328** |
| Opaque MonoBehaviour **base headers now parsed** | **55328 / 55328** |
| Opaque MonoBehaviour base headers still unparsed | **0** |
| Script m_Script null references | 0 |
| Invalid original script external fileIDs | **0** |
| Script refs to staged Foam owner sharedassets0 | **0** |
| Script refs to other external owner files | **55328** |
| MonoScript objects of type MonoScript in staged Foam owner | 0 |
| Structural header crosschecks against successfully read full-tree MonoBehaviours | **128 / 128** checked |

**Interpretation:** All 55328 previously opaque components are actual MonoBehaviour instances with recoverable **source-original built-in headers** and **valid external script references**. Thus the missing 55k custom-field records are not failed source scene file reconstruction or mangled `m_Script` headers. They reference **other original external serialized files** (not the source original Foam owner). This is a positive source-recovery result, but it only recovers base script pointers, **not** custom fields, MonoScript class identity or Foam Shader runtime assignment.

The next valid recovery step is to map these exact external m_Script fileIDs to original manifest asset providers, reconstruct and SHA-verify the *actual external script owner(s)*, confirm `MonoScript` typed target PathIDs there, then use original managed `Assembly-CSharp.dll` schemas/assignments (with proper header-alignment controls) to recover custom MonoBehaviour fields or runtime Foam material construction. The source owner file name alone is not a verified GUID or a guarantee of runtime linkage.

## Trial-build and coordination boundary

[T2 trial vote round `trial-20261106-r1`](../prompt/coordination/T_TEAM/TRIAL_BUILD_READINESS.md): **«لا يحتاج»** unchanged. This is source-only data lineage, **not** a new original Foam/Spectrum/Blur ShaderLab/CB0 integration or verified Android/Adreno water pixels. `WATER-001` remains OPEN; game NOT_READY. No native APK/OBB/XAPK run, game script/shader, scenes/materials/.meta/GUID, audio, Settings/touch or other workers' files modified. Scratch proprietary source bytes deleted before artifact publishing.
