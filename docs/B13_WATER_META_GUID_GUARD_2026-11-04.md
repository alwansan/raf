# B13 WATER-001 — fail-closed original water Shader/Compute .meta GUID identity (4 Nov 2026)

Session `20261104T2132Z-B13-7e6b`, only writable branch `feature/android-native-port`. This is a **structural source gate**, not restored original graphics content, not pixel equivalence, and not device confirmation.

## The gap and integrated fix

The existing [water pass/kernel preflight](../scripts/verify_water_render_contract.py) accepted the physical existence of a `.shader.meta` or `.compute.meta` as `original_meta_present=true`, without validating its Unity asset GUID. A malformed or duplicate identity can make an exported asset association unusable even if the shader's pass count and compute entrypoints look sufficient. Preserve prior B14 symlink rejection and B49/B47 authored program checks.

[Code commit 2db5078f](https://github.com/alwansan/raf/commit/2db5078f38d1cbd36ea20d351b9033bd88ffd29a) adds a bounded, **read-only** GUID preflight for the named required water shaders and water/FFT-named compute files:
- Require an unlinked regular original sidecar, at most 64 KiB, with exactly one top-level `guid:` field containing exactly 32 hex characters; normalize its comparison case without modifying the file or publishing its value.
- Reject duplicate water shader/compute GUIDs across those checked identities, ambiguous fields, malformed fields and oversized metadata. Missing ordinary `.meta` continues to mean unmet source coverage; linked `.meta` still fails closed.
- **No GUID generation/replacement, shader substitution, material change, Unity import, FMOD, Settings, gameplay, .rgd or touch modification.** Does not establish source-authentic identity against ZIP2; it only rejects demonstrably impossible/suspicious structural metadata.

Four source-free negative controls exercise malformed GUID, duplicate Shader→Shader, duplicate Shader→FFT compute and ambiguous compute fields; existing ten tests verify pass counts, kernel structural checks, symlink rejection and absence semantics.

## CI evidence and failed independent regression resolved

- [B13 run 41920455834](https://github.com/alwansan/raf/actions/runs/41920455834) **SUCCESS 14/14** on original code commit `2db5078f`. Same-source reconstruction preflight [41920455636](https://github.com/alwansan/raf/actions/runs/41920455636) and B49 authored-pass test [41920455691](https://github.com/alwansan/raf/actions/runs/41920455691) **SUCCESS**.
- **Retained failure evidence:** B47 original workflow [41920455700](https://github.com/alwansan/raf/actions/runs/41920455700) FAILED its legacy synthetic assertion expecting an FFT `.meta` symlink to be silently ignored. The current B14 path guard already raises `ValueError` for a linked original sidecar. Replacing the exception with `false` would weaken that fail-closed contract and break B14 negative controls.
- [B13 compatibility-only test commit ccefdd71](https://github.com/alwansan/raf/commit/ccefdd7151726155ed592376d6e6311797521ce3) updates **only** the B47 symlink test expectation to assert the existing error; no B47 production kernel parser changed. [B47 rerun 41920734179](https://github.com/alwansan/raf/actions/runs/41920734179) **SUCCESS**.
- B13 workflow was expanded at [ac315223](https://github.com/alwansan/raf/commit/ac3152230c62be054a2cece1750ddb01be42791b) to execute both validator suites on every relevant bounded change. [Final B13 combined CI 41920753737](https://github.com/alwansan/raf/actions/runs/41920753737) **SUCCESS 14+8 = 22/22 source-free tests**; no LFS/Unity/phone build.

## Remaining

The original water ShaderLab programs, compiled FFT runtime kernel identity, bound Material/Texture data, and Adreno runtime still require authentic source recovery and graphics verification. Last genuine phone game APK86 has known water pass/kernel failures; these tests do **not** change that APK. WATER-001 stays **OPEN**, project **NOT_READY (0/3 complete independent reviews)**. The diagnostic can now reject invalid sidecars; only real original source-to-export GUID mapping and a later Unity/phone render test can establish true binding and rendering. Preserve owner-confirmed audio and Settings, continue deferring touch.
