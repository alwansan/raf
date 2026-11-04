# B30 — original FFT variantMap/keyword discriminator rejection (2026-11-04)

Session `20261104T2140Z-B30-7c29`; WATER-001, owner-assigned identity **B30**; write branch `feature/android-native-port`.

## Why this source probe was necessary

B48 independently correlated ten original two-pass candidate program pairs with SHA-authenticated source selectors and 20 compiled programs; B08 subsequently verified **only one distinct original serialized kernel name** across all 20 compiled positions. A remaining hypothesis was that the original compiled entries' `variantMap` headers or their global/local keyword bundle signatures might distinguish banks/sizes/passes so that a runtime selection mechanism could be inferred. **Those fields cannot be assumed to represent Unity runtime kernel IDs.**

## Authentic execution and reproducible evidence

**Final passing source/test run: [41920323250](https://github.com/alwansan/raf/actions/runs/41920323250)**, job `126890849525`, source/test SHA [`c3a0a02cecf5782ab472a5b10bfd8cf134e50f75`](https://github.com/alwansan/raf/commit/c3a0a02cecf5782ab472a5b10bfd8cf134e50f75): **12/12 independent synthetic checks PASS**, plus actual original FFT source SHA/digest and same-slot DXBC verification. A prior green run [41920289281](https://github.com/alwansan/raf/actions/runs/41920289281), job `126890676451`, ran 10 controls and the identical authenticated original source experiment. Both reported the same original routing collisions.

Original provider: read-only ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. `Raft_Data/sharedassets0.assets` reconstructed from **three transport parts**, authenticated exact **115,978,112 bytes** with SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`. Original FFT ComputeShader object pathID `2456`, raw SHA256 `9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247`. The probe uses the existing independent original DXBC ordered slot authentication, not guessed compiled binaries or filenames.

Actual **original-source findings**, excluding private names/programs:

| Checked discriminator | Distinct signatures among original 20 compiled positions | Collision population |
|---|---:|---|
| Kernel name | 1 | 20 |
| Serialized variantMap opaque header | 1 | 20 |
| Global + local keyword bundles combined | 1 | 20 |
| Header + keyword composite | **1** | **20** |

All ten adjacent source-candidate pass pairs and all ten cross-bank position pairs have the **same** header/keyword composite. Original source workgroup cardinality/order is independently correlated and preserved; compiled slots nevertheless contain different programs (not copied or published). This is a falsification of **the hypothesis that these explicit serialized fields uniquely route the compiled slots**. It is *not* proof the original engine lacked a separate internal selector or that its actual `FindKernel` ID mapping is known.

## Controlled failures and rejected assumptions

- [41919872465](https://github.com/alwansan/raf/actions/runs/41919872465) failed at the final source invocation because the initially borrowed workflow module name was wrong. Original ZIP2 source authentication and synthetic tests passed before the invocation; corrected by [22c021f](https://github.com/alwansan/raf/commit/22c021f33d2a843e2af99e49cfcbffd2e78afde4).
- [41919906912](https://github.com/alwansan/raf/actions/runs/41919906912) reached the original source and refused a typed `variantMap` header. [41920054719](https://github.com/alwansan/raf/actions/runs/41920054719) safely classified it as `Invalid variantMap tuple`: the assumption that the header must be an integer was **false**. The accepted code [fd6fdfc](https://github.com/alwansan/raf/commit/fd6fdfc5e897a9a0132515f73d58b86e2a8ff6f5) treats its bounded typed value as an **opaque hash for equivalence testing only**, without inferring semantics; synthetic structured-header and invalid custom-object negative cases raised final tests to 12.
- Mutation controls reject reordered workgroups, fake 20 named runtime kernels, duplicate keywords, malformed/ambiguous map, bad binary signature, unsafe typed headers; original private strings/DXBC and device artifacts are never uploaded or logged.

Source diagnostic: [`scripts/b30_fft_variantmap_routing.py`](../scripts/b30_fft_variantmap_routing.py). Test: [`tests/test_b30_fft_variantmap_routing.py`](../tests/test_b30_fft_variantmap_routing.py). Independent workflow: [`raft-b30-fft-variantmap.yml`](../.github/workflows/raft-b30-fft-variantmap.yml) (ubuntu-24.04, 18-minute cap, strict ZIP2 SHA, no LFS, no Unity/native build, no private artifacts).

## Integration and limitations

This is a **source-integrated diagnostic with authenticated original-source negative evidence**, not restored authored `.compute`, shader pass, GPU draw, or Android fix. No current game asset, shader source, `.meta`/GUID, FMOD audio, Settings, touch, original ZIP2, CL, native build requests or protected branches were changed.

**Follow-up:** search for a separate authenticated **Unity serialization/runtime selection mechanism**, e.g. original kernel/program subprogram binding or runtime specialized tables; map it against the B48 candidate source selectors and independently verify with Unity. Do not fabricate distinct kernel names or clear `authentic_water_kernel_identity_verified`. Keep WATER-001/RENDER-002/LOCAL-005 OPEN and game NOT_READY / independent full readiness reviews 0/3. Audio/Settings remain owner-confirmed functional; touch/layout deferred.
