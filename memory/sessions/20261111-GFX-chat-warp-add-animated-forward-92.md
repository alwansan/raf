## 11 Nov 2026 — GFX128 Windows ForwardAdd verified; GFX129 sampled animated Forward

Session `20261111-GFX-chat-warp-add-animated-forward-92`, origin=chat. Write only `experiment/android-graphics-rootcause`.

[Windows GFX128 run 43056032415](https://github.com/alwansan/raf/actions/runs/43056032415) executed the original M02 ForwardAdd DXBC with checked per-stage CB slots and source sampler mapping. Controlled ONE/ONE RGB, alpha preserved, depth write off and LEQUAL. Windows changed 1,979 pixels and matched the exact saturating sum, zero light and NEVER kept the base byte-for-byte. All 2,008 covered pixels matched Mesa; composite RGB hash differs and magnitude of the inter-driver difference is unmeasured. Windows base regression 43056032164 reproduced all four previous RGBA hashes. Artifact 13870883994 has aggregate data only.

GFX129 evaluated three authenticated original M02 clips at five sample times each, reusing GFX111 source positions and bone weights. Preserved indexed geometry, UVs and tangent handedness, and used controlled linear transforms on the normal and tangent directions. A fixed camera was computed from the bounds across all poses. Mesa rendered all 15 frames with the original translated Forward program. Distinct images per clip: 1, 5, 5. The existing scene playback, Unity skinning of directions and full Animator runtime are still unverified.

The batch now has seven cases / 35 expected captures. The assembly check verified 187 fixture entries with the old source-free shell as a ZIP harness. Audited 7 cases/35 captures and a partial failure replay with 6 cases/24 captures. [Android shell run 43056576757](https://github.com/alwansan/raf/actions/runs/43056576757) succeeded, artifact 13870664397. No new signed APK or phone run. Remaining scope includes Windows animated reference, original Unity pass states, shadows/Deferred, original gameplay parity and final device acceptance. `phase_closed=false`.

