# T2 WATER-001 — Original Foam source Texture names in compiled managed setter contexts

**Source-authentic CI [42019735778](https://github.com/alwansan/raf/actions/runs/42019735778) SUCCESS — 5 Nov 2026.** ZIP2 immutable commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, original Foam owner `sharedassets0.assets` 115978112 bytes SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`, Foam Shader PathID2420 raw SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`, original `Assembly-CSharp.dll` 3211776 bytes SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`.

Prior [CI42017542487](https://github.com/alwansan/raf/actions/runs/42017542487) authenticated two authored original Foam Shader properties, just **one Texture property**; this same name is used once in each of the two fragment passes, accounting for **2 of 6** serialized source Texture usages. The **four other pass0 fragment source Texture names** are *not* authored Shader Texture properties. Among 351 Material objects in same original asset owner, none has direct local `m_Shader` PPtr fileID0/pathID2420; this is a limited owner-level observation, **not game-wide absence**.

Private scratch T2 Python enumerated the four non-authored and one authored names from the SHA-verified original Foam pass name registry and computed SHA256 hashes solely in ephemeral runner temp; no plaintext names or their hashes were emitted to logs/artifacts. Pinned Mono.Cecil 0.11.5 C# oracle scanned actual original compiled IL `ldstr` and recognized typed calls to `UnityEngine.Material.SetTexture`, `MaterialPropertyBlock.SetTexture`, `Shader.SetGlobalTexture`, `CommandBuffer.SetGlobalTexture` and `ComputeShader.SetTexture`. No original DLL executed.

| Validated original IL evidence | Numeric observation |
|---|---:|
| Method bodies examined | **19,118** |
| Compiled instructions examined | **491,490** |
| `ldstr` instructions examined | **7,246** |
| Distinct four non-authored original Foam texture names found as `ldstr` | **4/4** |
| Non-authored literal occurrences | **4** |
| Original methods containing all four occurrences | **1** |
| Methods with non-authored matched literal and typed texture setter | **1** |
| Four non-authored `ldstr` occurrences with a typed texture setter within 8 subsequent IL instructions | **4** |
| Same matched method contains `Material.SetTexture` and `MaterialPropertyBlock.SetTexture` | **Yes (both)** |
| Same matched method contains `Shader.SetGlobalTexture` | **No** |
| Authored Shader Texture name seen as original managed `ldstr` | **1/1** |
| Authored name directly adjacent to `Shader.PropertyToID` | **5 occurrences** |
| Non-authored name directly adjacent to `Shader.PropertyToID` | **0** |

**Interpretation:** This discovers the exact compiled managed source location class of the four omitted static Shader Texture properties; their literal strings and Material/MaterialPropertyBlock setters reside in one original method and each literal is near such a setter. **Literal proximity and same-method co-occurrence are NOT actual string argument/dataflow proof**. The managed method may have an unrelated setter or dynamic/cached IDs; no original runtime texture object upload, authored sampler filter/wrap/UV, constant-buffer member upload, genuine 2-pass ShaderLab/Unity import or Adreno pixels are established. A count of zero `Shader.SetGlobalTexture` in the one matched method is NOT a claim about other methods or assemblies.

CI lineage: first [42019245510](https://github.com/alwansan/raf/actions/runs/42019245510) blocked on eager Cecil dependency resolution; [42019520567](https://github.com/alwansan/raf/actions/runs/42019520567) scanned original 4/4 but its validation step rejected JSON UTF-8 BOM; final source fixes used deferred Cecil parsing and BOM-free UTF-8 [90646aa2](https://github.com/alwansan/raf/commit/90646aa2eea80e2034d47863ae8712cd38c765d7). **[42019735778](https://github.com/alwansan/raf/actions/runs/42019735778) completed SUCCESS** with **13/13** private source hash fixture tests and one public Mono.Cecil synthetic exact `ldstr`/PropertyToID test. Safe artifact **13410074764**, ZIP SHA256 `f9c76ade62b26c58cd429eb1d627fc9ba7b01646c7e8050d1e0d55f7cb658072`; two original SHA-pinned inputs and private hash file erased by cleanup. No private names, hashes, class/method labels, IL source/binaries or game assets uploaded.

Scripts: `scripts/t2_foam_managed_literal_targets.py`, `android-port/Experiments/T2/FoamRuntimeStringBridge/`, isolated `.github/workflows/raft-t2-foam-managed-literals.yml`; historical T5 Mono.Cecil and B05/W3/B20/B25 original metadata helpers retained attribution.

**Next proof:** trace exact `ldstr` stack argument into typed Unity Material/MaterialPropertyBlock `SetTexture` overloads using conservative branch-sensitive IL semantics and positive/negative controls; reject coincidental proximity. Then verify texture object provenance, property ID/CB/sampler upload, private genuine ShaderLab/Unity import, Adreno/device. WATER-001 **OPEN**, game **NOT_READY 0/3**, last on-phone game APK86. No source asset/.meta/GUID or audio/Settings/touch changes.
