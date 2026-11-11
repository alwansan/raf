## 11 Nov 2026 — GFX120 Adreno verified, phase-one batch in preparation

Session `20261111-GFX-chat-phase-one-batch-d3d-reference-87`, origin=chat. Write only `experiment/android-graphics-rootcause`.

Both owner GFX120 exports audited against the signed APK. Adreno 730 completed all four controlled M02 Forward cases. The 2,008-pixel mask matched Mesa in each case. Lit RGB mean absolute channel error was 0.1020916/255 and max was 11. Dark RGB matched byte-for-byte. Light, flat normal and nonmetal controls affected 1,979, 1,635 and 1,963 pixels respectively. Evidence `gfxlab/evidence/20261111_gfx120_owner_adreno_original_forward_safe.json`.

The shared GFX121 fixture constants preserved the Mesa result byte-for-byte. Windows Actions run [43049070451](https://github.com/alwansan/raf/actions/runs/43049070451) executed the exact original DXBC draw in D3D11 WARP and passed all four controls. The coverage hashes matched Adreno for all four cases. Dark RGBA was byte-identical; light, flat and nonmetal RGBA differed. The CI aggregate exposes hashes and counts, so a Windows–Adreno mean RGB error remains unmeasured. Evidence `gfxlab/evidence/20261111_gfx121_windows_warp_safe.json`. Artifact 13868887305 contains only the safe aggregate. The GFX122 source inventory resolved an exact directional Forward pair for all seven source material slots across M00–M05, with two distinct pairs. Only M02/0 has device draw evidence so far. Evidence `gfxlab/evidence/20261111_gfx122_forward_batch_inventory_safe.json`.

See `gfxlab/PHASE_ONE_BATCH_ACCEPTANCE_AR.md` for the four open packages and one APK/one ZIP delivery plan. The controlled draw is one component of phase-one acceptance. Pending original pass/state coverage, multi-material reuse, original animation and original PC scene comparison. No new owner run requested yet. `phase_closed=false`.

