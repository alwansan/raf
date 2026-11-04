# B10 — generated vendor Shader metadata restoration (4 November 2026)

Session `20261104T2132Z-B10-a6e1`; source baseline `e6484daffbaef7dca57da63e1cb4869f9095078a`; production source fix [46b9fb69](https://github.com/alwansan/raf/commit/46b9fb69d0e63526717e010bf9d7eb487fe9e2c5), final regression correction [1f76e243](https://github.com/alwansan/raf/commit/1f76e243c067b77a507a81e603f1ce90e5b68dc0).

## Observed engineering blocker

[W1 native41741108965](https://github.com/alwansan/raf/actions/runs/41741108965) failed **before Unity**, with post-restoration material inventory reporting **two Shader files lacking a .meta**. [W1 source investigation](W1_NATIVE_FAILURE_AND_ENGINE_REFERENCE_PROOF_2026-11-04.md) identified `scripts/restore_tmp_shaders.py` adding authenticated vendor fallback `*.shader` files **without .meta**. This is a reproducible production source defect; the exact two missing native paths were not retained, so equivalence of these particular two items remains an evidence gap. In particular this finding does not explain the separate builtin 0/142 export-identity failure or recover any original water program.

## Source fix integrated

The production TMP/vendor restoration helper creates `ShaderImporter` metadata **only** for newly synthesized missing vendor fallbacks. GUIDs use a namespaced deterministic SHA256 derivation over the output include root and exact official vendor Shader identity, yielding one 32-character hexadecimal value. All existing .meta GUIDs in exported Assets are screened for collisions; distinct new fallback identities also cannot share a GUID. Preexisting fallback shader/.meta pairs are accepted only if byte-identical. Generated shader+.meta enter the existing staged transaction and rollback; failed writes restore original shader bytes and remove new dependencies. A repeated restore does not misclassify generated vendor fallbacks as original exported shaders. No source asset, program, pass, original .meta or original GUID is rewritten by this fix.

This also affects official PostFX and volumetric restorers that reuse the same shared helper, without changing their shader content. Source remains the pinned vendor packages already in the existing code. ZIP2 original provider commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385` is unchanged; no LFS/new downloads or private game data transfer performed.

## Verification

[Isolated B10 CI41917602226](https://github.com/alwansan/raf/actions/runs/41917602226) **SUCCESS, 22/22** Python tests on immutable source `1f76e243...`, including generated Shader metadata, deterministic repeat, original GUID preservation, missing/changed dependency, original GUID collision, symlink rejection, and failure rollback, plus existing TMP, PostFX and volumetric source regressions. [A3 CI41917602139](https://github.com/alwansan/raf/actions/runs/41917602139) **SUCCESS**, 9/9 transaction tests plus preexisting vendor suites. Initial [B10 41917440764](https://github.com/alwansan/raf/actions/runs/41917440764) and [A3 41917392549](https://github.com/alwansan/raf/actions/runs/41917392549) were **FAILED** from literal-newline errors in the *new tests*, not in the production patch; both corrected and recorded in [B10 incident](../prompt/coordination/incidents/B10/20261104T2135Z-double-escaped-fixture.md).

## Scope and next acceptance

The fix closes the generated-vendor Shader metadata source defect only. **It does not prove Unity accepted a complete original Shader export**, does not prove Material→Shader original identity, any kernel/pass/pixels, or resolve 40,327 invalid water-pass / 5,555 invalid compute-kernel reports on the older Android APK86. It also does **not** prove that the exact two native missing-meta files were produced by this helper because their paths were not recorded. RENDER-002, WATER-001, LOCAL-005 remain OPEN; Raft NOT_READY; independent full reviews **0/3**.

On the **next already-authorized/coordinated actual export**, run the existing exported Shader GUID inventory *before and after vendor restoration*, capture paths privately / counts safely, and confirm zero missing meta without changing original shader GUIDs. Do not start a duplicate full native build just for this scoped verification; prioritize original water/FFT and actual Material lineage. Audio and Settings left unchanged; touch/layout deferred. No new release, APK, scheduler, task, or protected branch touched.
