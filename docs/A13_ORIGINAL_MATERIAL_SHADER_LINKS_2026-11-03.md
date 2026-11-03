# A13 original Material → Shader source-reference audit — 3 November 2026

Client: `raft-20261103T123129Z-6533d5b4`, resumed session `a13-20261103T150000Z-7e4a02d9`; scope RENDER-002 original serialized material linkage, **not** A12's vendor-name overlap and not W1's graphics program recovery.

## Inputs and verification

[Source `816f680405aea70c18132ab4e5d2ef658f06b3a6`](https://github.com/alwansan/raf/commit/816f680405aea70c18132ab4e5d2ef658f06b3a6) introduced independent `scripts/probe_a13_material_shader_links.py`, 12 negative/positive CPU controls and dedicated `raft-a13-material-shader-links.yml`. [Exact-source GitHub Actions run41660807306](https://github.com/alwansan/raf/actions/runs/41660807306), job126003168097, **COMPLETED SUCCESS**, 12/12 real source tests, authenticated actual originals scanned in a separate step. [Safe aggregate artifact](https://github.com/alwansan/raf/actions/runs/41660807306/artifacts/13241532437) contains count/hash JSON only.

Original SHA-pinned, byte-count-checked input owners (from existing W1 cache; no third owner):
- `resources.assets`: 111533516 bytes, SHA256 `87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c`.
- `sharedassets0.assets`: 115978112 bytes, SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`.

The W1 LFS object cache hit; full SHA verification passed before UnityPy1.25.4 read source objects. No source assets were uploaded or changed. This is not the failing-run 140-Shader export; earlier 107 exported-file sample remains unproven complete.

## Verified original reference results

| Original owner | Material objects | Shader objects | Same-file internal resolved PPtrs | External FileID pointers (not resolved) |
|---|---:|---:|---:|---:|
| resources.assets | 163 | 47 | 14 | 149 |
| sharedassets0.assets | 351 | 58 | 344 | 7 |
| **Total** | **514** | **105** | **358** | **156** |

All 358 `m_FileID == 0` + nonzero `m_PathID` references resolve to Shader objects within their own source serialized container: **zero unresolved internal references**. Exactly **48 distinct** local Shader objects are referenced, with up to **113 Materials** referencing the same Shader object. The other156 pointers are nonzero `m_FileID` references whose target owners cannot be established from these two source files. They are **unknown**, not evidence of broken links or official built-in shader identity. No source Material has a null shader pointer in this verified inventory.

The join requires identical owner and PathID for any local reference. A similarly numbered Shader object in a different owner does not count. Synthetic cases reject missing/malformed PPtr, bool-as-int, negative IDs, cross-owner PathID collision, duplicate Shader/Material objects, and fabricated external link resolution. All 12 synthetic cases passed on the exact source in CI. No shader/material names, original PPtr IDs or raw shader source are published.

## Hypotheses versus proven claims

Proven: the exact two pinned original files still hold 105 Shader objects and 514 Materials; internal material links 358/358 resolve locally. There are 156 external references requiring further owner/dependency verification, and these two files cannot be presumed the full game shader/material inventory.

Not proven: whether any original Shader identity is one of the 198 official Unity built-ins (**A12's separate experiment**); whether the 140 exported one-pass files correspond 1:1 to this 105-object inventory; whether Material GUIDs survive reconstructed `.meta`; whether original color/texture, stage/pass/FFT, GPU or Android device output is equivalent. Neither the historic original built-in zero-match from [native41624581951](https://github.com/alwansan/raf/actions/runs/41624581951), nor broader RENDER-002/WATER-001 is repaired by this source audit.

## Next actionable engineering step

For the 156 external PPtrs, inspect **authenticated owner external-file tables and references** to resolve actual `m_FileID` mappings before joining `m_PathID` across owners. Then compare proven material→shader owner links with GUID-preserving exported .shader/.mat identities using an authenticated complete export, independent of A12's vendor identity count and W1's original shader body reconstruction. Do not invent names, bypass zero-match checks or substitute a generic shader.

No Unity Editor/import/build, APK/OBB/XAPK/Release, native request, CL write, original assets/.meta/GUIDs, LFS pointer changes or scheduled task modification. **RENDER-002, WATER-001 and FFT-FORMAT-009 OPEN; game NOT_READY, independent complete immutable-candidate reviews 0/3.**
