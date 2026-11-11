# 20261111-GFX-chat-owner-gfx098-archive-68 — GFX100 / GFX-OWNER-004
- **origin:** chat
- **role:** GFX-LAB
- **branch (only writable):** `experiment/android-graphics-rootcause`
- **resumed_from:** `prompt/graphics-lab/RESTORE_AR.md`, GFX098 CI42927645102, GFX099 CI42930674563, `gfxlab/PHASE_ONE_CURRENT_PLAN_AR.md`.
- **base_sha:** project branch at beginning of owner evidence update (first own commit `ab29616d17435727a4e396b0281c1d89fca0ae7c`); no rebase or changes to T branches.
- **issue / experiment:** `GFX-OWNER-004` / `GFX-MULTI-100`.
- **evidence level:** actual Android `GPU_EXPERIMENT` *diagnostic only*. No original Shader48 execution.
- **owner archive:** `g.zip` SHA256 `60b6cb3e13ea1da7808128311696e9a906655340ea6a2537ad9c9db8d50faa69`; verified privately, NOT uploaded to repo.

## Phone evidence audited
- Outer owner ZIP and **5 nested export ZIPs CRC PASS**. **3 sessions**, **227 recorded events**, **147 snapshots**; all summary counts match. Reports **0 Unity errors**, **0 warnings**, **0 dropped messages** inside their recording windows only.
- **4 complete 12-case studio matrices** (M00–M05 × modes 3 and 4). **48/48 PNG captures** present with matching on-disk JSON SHA256; 12 model-mode cases reproduced byte-identically across repeats. All images remain private; only count-only report committed.
- Device identified in private sessions as Xiaomi 23013PC75G / Adreno 730 / OpenGLES3 / Unity2021.3.45f2 / Linear; studio fallback is diagnostic Standard, `originalShaderRestored=false`.
- GFX041 standalone synthetic interpolation ran **twice**, **8 recorded GPU readbacks**, all sample positions foreground. **Linear spread 0.19739**, **Flat 0**, **NoPerspective 0.19739**, **AffineEmulated 0.14510**. The actual saved Linear and NoPerspective **PNG files have identical SHA256**, and the app explicitly records `DIAGNOSTIC_NATIVE_QUALIFIER_COLLAPSED_TO_SMOOTH` twice. Hence native NoPerspective behavior is **not discriminated** by this Unity diagnostic, not evidence Adreno hardware is broken.
- The 20 ShaderCache entries inside the owner ZIP are *not* original Shader48 program identity witnesses. No original Shader48 pipeline or PC↔Android pixel parity.
- Source-safe anonymous JSON: `gfxlab/evidence/20261111_gfx100_gfx098_owner_safe_counts.json`.
- New bounded, source-free safe inspector: `gfxlab/tools/unified098_owner_zip_audit.py`; 4 synthetic positive/negative regression cases in `gfxlab/tests/test_unified098_owner_zip_audit.py`; CI workflow `gfxlab-100-owner-zip-safe-audit.yml` has been created, **not yet independently confirmed terminal SUCCESS**.

## Next P0 engineering (requires separate verified experiment)
1. Make an actual GLES3 native interpolation comparison where an explicit *real* `noperspective` qualifier and a perspective-weighted control cannot collapse silently. Prefer program binary/active shader inspection and a known analytic triangle W test. Fail closed on unsupported backend or compiled qualifier removal; keep source-free diagnostic separate from Shader48.
2. Restore full original vertex streams + indexed submeshes + skin weights/bindposes/hierarchy for skinned M01/M04 (no OBJ merge losing bone identities); separate original rig from static screenshots.
3. Shader48 full material input/Pass states/normal mip and GPU sampling, then same camera/light PC vs Adreno image metrics with private captures. GFX099 PC source compile is not pixel equivalence.
4. No full game/APK rebuild just for this already-successful GFX098 owner audit. No other branch changed.

**Negative gates:** `originalShaderRestored=false`, `originalAnimationRestored=false`, `phase_closed=false`, no claim RENDER-002/WATER-001 READY.
