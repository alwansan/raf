# T2 — real original scene MonoScript → managed TypeDef subset

**2026-11-06 UTC · Agent T2 · chat · issue WATER-001 OPEN · game NOT_READY.**

## Question resolved
The prior [original complete-provider class census](T2_ORIGINAL_MONOSCRIPT_MANAGED_CLASS_BRIDGE_2026-11-06.md) scanned all **3,827** typed MonoScript objects in one source-original provider and matched **1,605** to unique Assembly-CSharp TypeDefs. That result did **not** tell us which were actually referenced by game scenes. A separate source-authentic [40-level MonoBehaviour header census](T2_ORIGINAL_OPAQUE_MONOSCRIPT_HEAD_2026-11-06.md) found **55,328** component `m_Script` pointers referencing **473 distinct typed MonoScript targets**, but never joined their exact class metadata with original managed code.

This experiment joins **only those 473 real scene-referenced targets** to SHA-authentic original managed TypeDefs via serialized external file/PPtr identity and PathID, not class name guesses.

## Immutable source, privacy, controls
- Original ZIP2 provider pinned at commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385` with SHA-checked manifest metadata. The runner sparse-checks out and independently SHA-verifies **40 original level scenes totaling 233,237,972 bytes**, the **758,412-byte** original MonoScript provider, and **3,211,776-byte** original `Assembly-CSharp.dll`; combined SHA-checked payload **237,208,160 bytes**. These counts do not imply full 7.79GB source verified.
- UnityPy 1.25.4 parses original Unity MonoBehaviour base `m_Script` header in previously opaque scene objects, identifies the genuine external serialized source by manifest unique candidate and real PathID, then selects exactly referenced typed MonoScript class metadata. `dnfile==0.18.0` parses original managed TypeDef namespace/name rows. Matching is exact/case-sensitive; unknown/ambiguous remain explicit.
- All source files, private paths, GUIDs, script names, PPtr PathIDs and original DLL bytes remain on ephemeral runner scratch and are purged before public artifact upload. The report and safe artifact export only finite numeric/boolean aggregate data.
- Source commit `fdaa5bf749ed07a0a6cd7d34718a90290b5e9322`: `scripts/t2_original_scene_managed_subset.py`, `tests/test_t2_original_scene_managed_subset.py`, workflow `.github/workflows/raft-t2-original-scene-monoscript-managed-subset.yml`. **15/15** adversarial sourcefree tests included missing/ambiguous original manifest, foreign external owners, bad/boolean PathIDs, duplicate references, unreferenced owner scripts, missing true typed target, exact-case rule and ambiguous TypeDef.

## Genuine GitHub Actions result
[**Run 42276583082 — SUCCESS**](https://github.com/alwansan/raf/actions/runs/42276583082) on `fdaa5bf749ed07a0a6cd7d34718a90290b5e9322`; all 15 sourcefree tests, 42 original input SHA gates, real scene header, exact type join and safe-privacy assertions passed.

| Genuine original measure | Result |
|---|---:|
| Original scene files and bytes SHA checked | 40; 233,237,972B |
| Original MonoScript owner and managed DLL bytes SHA checked | 758,412B; 3,211,776B |
| Opaque scene component `m_Script` PPtrs | **55,328** |
| **Distinct** source-authentic MonoScript targets actually referenced in scenes | **473** |
| All typed MonoScripts in full provider (not all used in 40 scenes) | 3,827 |
| 473 actual scene scripts declaring Assembly-CSharp | **428** |
| Of these, exact uniquely matching original managed TypeDef | **427** |
| Exact ambiguous original managed TypeDef | **1** |
| Missing original Assembly-CSharp TypeDef | **0** |
| Remaining script objects declaring other assemblies | **45** |
| Unreadable MonoScript source class metadata | **0** |
| Original managed TypeDef table | 3,033 rows / 2,914 distinct namespace/class keys |

Safe artifact: [13533820909](https://github.com/alwansan/raf/actions/runs/42276583082/artifacts/13533820909) (666B), ZIP digest `sha256:ebf53fe08aef375c326a2caa83a8ad196eafd144e31e2e14e5c2f2e43283895a`. This is an *artifact archive* SHA, not a raw game file digest.

## Interpretation / next integration frontier
**427/428** actual original scene-referenced MonoScript class metadata for Assembly-CSharp match a unique, genuine original managed TypeDef. This materially narrows the source-authentic class-to-code frontier versus the earlier all-provider 1,605 matching objects.

The one ambiguous TypeDef remains unresolved; do not invent a name, alias, GUID, default or class binding. A TypeDef match by namespace/name **does not** reconstruct a custom serialized MonoBehaviour field, prove that a scene actually instantiates a game water component, or establish that a shader is referenced through `Shader.Find` / `Material` construction / constant buffer CB0 at runtime. Source-authentic scene/assembly association is not Unity Editor compilation, Android GPU execution or phone water-pixel acceptance.

**Next unique engineering step:** privately filter original scene-referenced 427 matched class TypeDefs for *actual* managed field signatures and water render/material/Shader call sites, preserving source-authentic class identity and avoiding public IL/name dumps. Then reconstruct faithful Foam/Blur/Spectrum/CB0 shader bindings and compile with Unity/Adreno. T2 trial vote remains **«لا يحتاج»** for this source-only step; WATER-001 OPEN and full game NOT_READY.
