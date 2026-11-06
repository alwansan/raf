# T3 — authentic 108-use Particle Shader48 exported to DummyShaderTextExporter source

**Result:** Actual source-identity-linked AssetRipper output for the exact original ParticleShader48 source with 108 six-scene Particle Renderer Material slots contains **`//DummyShaderTextExporter`**. The file has a structurally valid one-pass CG/HLSL program block but is a **dummy template, not proven authored original code**. `RENDER-002` remains **OPEN / NOT_READY**.

## Genuine source-to-output experiment

- [GitHub Actions 42136474867](https://github.com/alwansan/raf/actions/runs/42136474867) **COMPLETED SUCCESS**, exact source/workflow commit `2aa84a40bff9ac0b69277552e4a071e1a59299d4`, **16+9+4+13+7+23+7+9+11+14 = 113/113** strict/source-free tests PASS. First two same-experiment CI runs [42136195978](https://github.com/alwansan/raf/actions/runs/42136195978) and [42136368256](https://github.com/alwansan/raf/actions/runs/42136368256) failed **synthetic fixture setup only**, before any original source staging: new shader-only synthetic tests omitted required Material21/Texture2D28 same-instance rows, then a missing-Shader48 test removed the Material fixture too. The final tests were fixed without weakening production source guard.
- Six original scenes, four Shader/Material owners, two runtime globals SHA authenticated at immutable ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. Full manifest size/SHA of ONE original external `.resS` provider verified; three source Texture2D28 streams read. Pinned public AssetRipperCLI source `036098ab525a3f9f693dc101edeb21faad4d32d8` compiled and ran one bounded actual export. W1 and B02 private source→export object traces share the same `export_instance`.
- Exact unique original source Shader48 was selected ONLY by private six-scene `(owner, PathID)` graph: **108 ParticleSystemRenderer Material-slot references / 54 distinct Renderers**, five authenticated original Material21 and three actual Texture2D28. The original Shader48 has one parsed normal Pass with alpha-dependent blending and ColorMask RGB. No source Shader names/IDs/ShaderLab/HLSL code, source byte values or export GUIDs were published.

## Authenticated exact same-export Shader48 output quality

| Fact | Observed value |
|---|---:|
| Exact original source Shader48 identified via six-scene ParticleRenderer graph | **1** |
| W1 original→same-export class48 source trace | **1 / 1** |
| Real exported Shader `.shader.meta` matching source-linked GUID | **present** |
| Real exported `.shader` for exact GUID | **present** |
| Original Shader48 parsed pass count | **1** |
| Exported ShaderLab pass count (structural B49 parser) | **1** |
| Exported pass with syntactically paired CGPROGRAM/ENDCG or HLSLPROGRAM/ENDHLSL | **1** |
| Exported ShaderLab braces balanced | **yes** |
| Export text explicitly contains `//DummyShaderTextExporter` | **YES** |
| Export text `// No subprograms found` marker | **no** |
| Export pointer classed as custom Shader rather than builtin | **yes** |
| Source original DXBC/fragment semantics reproduced in exported ShaderLab | **NOT PROVEN** |
| This exact source shader identified as user's phone fire/smoke emitter | **NOT PROVEN** |
| Android ARM64 shader pixels/alpha verified | **NOT PROVEN** |

**Impact:** The standalone original AssetRipper export preserves the source Shader identity, one-Pass structure and selected Material+TexEnv bindings (**10/10 exact source→same-export Material texture references, including 1 original nonexportable/internal class28 pointer, from prior CI42134436841**) but substitutes the selected original Shader48's executable program text with a marked dummy. A balanced one-pass `.shader` and a CGPROGRAM block therefore cannot be called a visual/fidelity recovery. This source-bound shader-output defect is real; its relationship to the *complete* Android native restoration pipeline and the user's square fire/smoke screenshot still requires proof.

## Implementation and privacy

- New `scripts/t3_particle108_shaderlab_export_quality.py` validates unique original source 108-use Shader48 via SHA-pinned original six-scene/four-owner graph, links to one exact source W1 class48 identity and same-instance W1+B02 validator, scans only bounded real export `.shader.meta` GUIDs and the corresponding `.shader`, and fail-closed classifies built-in, missing output, dummy text, no-program text, incomplete/extra pass and merely structural-program states.
- New nine source-free regression tests in `tests/test_t3_particle108_shaderlab_export_quality.py` include fake valid-looking program + dummy marker, wrong source trace, missing/duplicate meta, cross-instance source contamination, Unity builtin reference, false program in comments, missing subprogram and pass-count mismatch. The dedicated `.github/workflows/raft-t3-particle108-sameexport.yml` uploads ONLY anonymous safe numeric/classification JSON; the raw shader files/Shaderlab text/Material labels/GUIDs/PathIDs stay in ephemeral runner folders.
- No `.shader`, `.meta`, original image, Material, prefab, scene, Android OBB/APK, sound, water/FFT, Settings, saved game or input asset was modified. Other client CI not canceled. This result says nothing about whether T5's subsequent post-vendor/export-restoration workflow already replaces this particular Shader correctly.

## Next action

Coordinate with T5 on **the exact SHA-origin class48 source→same-instance exported Shader GUID** and inspect the **post-vendor/native Unity project** to determine if the dummy is still present after all project restoration steps. If still dummy, recover the original selected **one-Pass D3D11 vertex/fragment programs and keyword permutations** through pinned W1 recovery tooling, generate/review original-state-preserving Unity ShaderLab (ColorMask RGB, alpha Blend, ZWrite OFF), and validate Unity Vulkan/Android import and phone fire/smoke pixel test before touching production `.shader` or claiming ready. Preserve original five Materials' **10/10** matched Texture PPtrs; do not replace the internal/nonexportable Texture with a guessed image.

**Gate:** `RENDER-002 OPEN / NOT_READY`; actual phone emitter and APK/OBB/GPU pixels unverified.
