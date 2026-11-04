# B04 incident — concurrent renderer snapshot rebase

- Identity B04; session 20261104T2243Z-B04-6b7c
- Issue RENDER-002
- Discovered: 2026-11-04T22:48Z
- Impact: Read-only QualitySettings helper was compiled but orphaned by a
  concurrent B12 renderer traversal replacement; absent new phone evidence
  would look like instrumentation not executing. No known gameplay/device
  damage, no full Android run, no assets changed.

## Evidence
1. [84b604f](https://github.com/alwansan/raf/commit/84b604f5117c83402c33be03e71630a234eff845)
   added helper and a single call within previous B12 snapshot.
   [41928222177](https://github.com/alwansan/raf/actions/runs/41928222177)
   managed original-source CSharp CI SUCCESS.
2. [B12 commit 2c15dfbf](https://github.com/alwansan/raf/commit/2c15dfbf8ccc)
   bounded the renderer traversal, preserving the helper definition but
   omitting its invocation. B04 [41928410376](https://github.com/alwansan/raf/actions/runs/41928410376)
   synthetic source-policy CI FAILED (the callable expression missing).
   Independent negative controls correctly exposed this integration loss.
3. [B04 bridge bc63f59](https://github.com/alwansan/raf/commit/bc63f59de0875bee6fdff71f21f5a9dd991f5045)
   reattached only `OriginalQualityStateSnapshot()` to the live
   bounded B12 output, preserving root/transform/material limits and
   existing renderer counters.
4. [41928576465](https://github.com/alwansan/raf/actions/runs/41928576465)
   then FAILED 1/9 because the new fallback-negative-control expected
   a specific failure class but the generic missing-field check ran first.
   This was a test assertion ordering problem, not a CSharp runtime failure.
   [Test correction 6b9390a](https://github.com/alwansan/raf/commit/6b9390a0a47cb24b58b25790b73750fc18cc1603)
   checks fallback semantics before field completeness.
5. [41928607504](https://github.com/alwansan/raf/actions/runs/41928607504)
   **SUCCESS 9/9**. Reconnected source actual original-managed
   [41928576383](https://github.com/alwansan/raf/actions/runs/41928576383)
   **SUCCESS**. No Unity/device screenshot evidence.

## Rejected hypotheses
- The helper's presence alone proves runtime logging occurs: false;
  instrumentation must be invoked from the actual loaded-scene path.
- B12's traversal safety improvements must be reverted to restore B04:
  false; a one-expression integration keeps both changes.
- Rebased 1/9 failure indicated original C# compilation or quality
  setter regression: false; fixture ordering rejected the intended error
  one check too late.

## Recovery and boundaries
Closed for B04 source integration scope by bc63f59 + 6b9390a CI and actual
managed compile. No current APK includes this change, so RENDER-002 remains
OPEN and NOT_READY 0/3. On next justified native build/phone test, inspect
single delayed `scene_shader_snapshot` with `quality_level_index`, other
quality fields, existing B12 material/mesh counters. Do not cancel concurrent
jobs or modify audio, Settings UI, deferred touch, ZIP2 or protected branches.
