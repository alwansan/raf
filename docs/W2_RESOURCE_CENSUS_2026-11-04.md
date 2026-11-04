# W2 complete original resource census — 1,209,137 objects / 82 owners — 4 November 2026

Client W2 `raft-20261103T152008Z-92502b76`. Tenth ring under the owner's
full-resource-restoration directive: the **exact per-owner serialized type
census of the original build** (`scripts/probe_w2_resource_census.py`, 5/5
fail-closed tests, workflow `.github/workflows/raft-w2-resource-census.yml`,
82/82 owners identity-verified against commit HEAD). Pure counters —
no names, path IDs or payloads; no typetree parsing (class name only), so
the whole game counted in one cheap CPU pass.

## The original build census (per class, game-wide)

| class | count | | class | count |
|---|---:|---|---|---:|
| GameObject | **294,045** | | Mesh | **4,708** |
| Transform | 286,722 | | Texture2D | **4,050** |
| MeshRenderer | 176,432 | | Light (serialized) | 228 |
| MeshFilter | 176,345 | | Material | **1,556** |
| LODGroup | 103,219 | | Shader | **165** |
| MonoBehaviour | 76,161 | | Sprite | 1,018 |
| BoxCollider | 27,232 | | AnimationClip | 679 |
| MeshCollider | 25,026 | | MonoScript | 3,828 |
| RectTransform | 7,323 | | CapsuleCollider | 3,004 |
| CanvasRenderer | 5,907 | | Tree | 2,625 |
| ParticleSystem(+Renderer) | 2,142 | | SkinnedMeshRenderer | 363 |
| Camera / AudioListener / ReflectionProbe | 3 / 1 / 4 | | Terrain | 33 |
| **AudioClip** | **0** (FMOD banks instead) | | **Font** | 14 |
| **TextAsset** | **6** | | **ComputeShader** | **9** |
| distinct serialized classes | **66** | | total | **1,209,137** |

Largest owners: level30 (253,566 objects), level34 (145,220), level25
(73,739), level29 (70,726), level12 (58,615). Full per-owner × per-class
matrix in the CI artifact (`w2-resource-census.json`).

## Engineering significance (bounded) — the "complete resource restoration" gate

1. **Restore-count equivalence**: any rebuilt build can be reconciled
   against this census directly — a deficit in any row (e.g. 4,705/4,708
   meshes, 1,555/1,556 materials, 4,049/4,050 textures) is a concrete,
   binned, actionable restoration defect found without launching anything.
2. **AudioClip=0 / TextAsset=6** confirm the audio/text content lives in
   FMOD `.bank` files and streaming assets — the census itself proves the
   serialized side has no missing audio gap to hunt for.
3. Renderer/transform symmetry (MeshFilter≈MeshRenderer 176,345/176,432)
   is itself a port invariant: any restored hierarchy that changes these
   ratios deviates from the original serialization.
4. Nine-rings coherence: the census rows for Texture2D (4,050), Material
   (1,556), Shader (165), ComputeShader (9) match the per-ring lanes
   exactly (4,050 texture split; 1,556 material binding/scalar lanes;
   165 shader inventory from W3; 9 compute providers from the kernel
   inventory) — the W2 aggregate program is now internally self-consistent.

## Boundaries

- Counters only; no object names, path IDs, or payload bytes.
- No Unity/APK/OBB/Release; no engagement with fatal build lanes
  (W4 trial 41812889049, W5 Blur rebinding, W1 export lineage).
- WATER-001 / RENDER-002 / FFT-FORMAT-009 remain OPEN; NOT_READY;
  triple immutable-candidate reviews 0/3.
