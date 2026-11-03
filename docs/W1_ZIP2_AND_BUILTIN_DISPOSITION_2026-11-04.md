# W1 — ZIP2 shader restoration and engine redirect investigation — 4 November 2026

W1 continues as raft-20261103T162900Z-73e8c2a1 on feature/android-native-port only. ZIP2 is read-only. No protected branches, scheduled tasks, shared native request or peer workflows changed this cycle.

## Actual prior native outcome
Native41687765928/sourcea8e04dd2 FAILED before Unity at built-in restoration:142/142loose shader declarations parseable,0matches to198official vendor identities. No APK/OBB/XAPK.
The same real full export **did install W1 Depth Copy** successfully before that failure:1target, exported metadata unchanged; reconstruction SHA0a7e11f750cac17ecc25cb7179c0a29850d6fb91fa983618f12e6bd8782ed1ea; meta SHAdc9864d5606c25a83ec061cfd38fa58a9569c596ce9bfd10340591bab714baf9; original exported source SHA9c802f3b4c0dfa7b2a82d5bf9af77bb3f8a119e514d8064f1ee97fd30b5b54de. This supersedes the earlier “actual export installation pending” checkpoint, but does NOT prove Unity property binding or phone rendering.

## ZIP2 implementation
scripts/w1_stage_zip2_owners.py authenticates pinned15964ea8f246b6e076ce26b60931ee2e1a9a2385 checkout identity and per-file independent expected lengths/SHA. Six original chunks reconstruct resources.assets and sharedassets0.assets; two plain canonical engine owner files are also read. Total4files/233,281,064bytes verified. Wrong bytes, missing chunks, redirects and conflicting outputs fail; verified outputs may be reused; publication is atomic and does not overwrite.

resources.assets/sharedassets0.assets retain the pre-existing original shader recovery pins. The two engine files' Git blobs also match the pre-existing feature-branch objects exactly:
- default resources:777ccb2db0b4d5957cc6d4e4ac95e202f84ab716,4,832,808bytes;
- builtin extra:b949c9ade5bdf6b489d5bb01c8f8542c9ec24195,936,628bytes.

Only W1's staging workflow is migrated here. Other existing lanes still using LFS need their own deliberate migration. The existing Raft tree is preserved; raw split directories are never passed to UnityPy or the shader builder. No whole-game content/fidelity claim follows from these4files.

## Build blocker investigation
Pinned exporter source nowl-it/AssetRipperCLI036098ab525a3f9f693dc101edeb21faad4d32d8 establishes:
- ProjectExporter.DoFinalOverrides installs EngineAssetsExporter after shader exporters.
- EngineAssetsExporter redirects assets in known engine owner files and assets matched by PredefinedAssetCache to fixed engine pointers.
- ShaderKey uses generated IShader.Name and an ordered property-name hash. The mapping of that generated property to raw m_Name versus parsed declaration has not yet been proven; both raw fields are now reported independently.
- SingleRedirectExportCollection.Exportable=false; such assets produce no loose .shader.
Thus a required positive number of loose built-in matches is not universally a valid completeness condition. This does NOT yet prove that all built-ins in the failing full export were correctly redirected. No production gate was weakened.

scripts/w1_probe_engine_shader_redirects.py compares original game Shader objects with the canonical original engine-owner identities and classifies local material shader pointers. Counts/hashes only; no names, raw assets or shader programs published. Embedded exporter TPK database/version and actual complete-export material references remain separate unverified inputs. Next resolve that exact missing mapping before proposing a gate correction, then address the independent strict water/FFT gate.

## Validation
32localW1tests passed (including6new restore/property-order cases).
First originalZIP2run41732681344 verified all233,281,064bytes with lfs_used=false, regenerated the exact pinned Depth Copy wrapper and passed synthetic installation. It then FAILED on the diagnostic's assumption that asset names equal ShaderLab declaration names; that is a diagnostic error, not resource corruption or a game-render failure. The second diagnostic run41733115872 also FAILED because raw asset names can be stripped/empty. Neither error concerned the authenticated source reconstruction or recovered wrapper. Final comparison reports raw asset-name keys and parsed-declaration keys independently and counts unavailable values, without inventing a mapping to the exporter's generated IShader.Name. New sourceafb4bc1b8b86d3254a35916b5cc336234fd547aa must be inspected for final CI; no successful exporter binding is claimed from mere declaration-name similarity. All earlier source/Unity/raster proof boundaries remain unchanged. No duplicate full native build. WATER/RENDER/FFT OPEN; NOT_READY0/3.


## Final live evidence
[Run41733600478](https://github.com/alwansan/raf/actions/runs/41733600478) **COMPLETED SUCCESS**, sourceafb4bc1b8b86d3254a35916b5cc336234fd547aa, job126256952854, aggregateartifact13276929044. All4original files reauthenticated, wrapper regeneration and synthetic GUID installation passed, and19CItests passed (5ShaderLab+8installer+6ZIP2).32localW1tests passed. Verified source bytes233,281,064; noLFS.

Bounded original comparison:105gameShaders, all105rawassetnames unavailable; parsed-declaration comparison found0matches to the loaded canonical-owner keys. The canonical files contain6+54Shaderobjects.514material pointers:358local-to-other/unmatchedshaderkeys,156externalunresolved. This is a **negative bounded candidate search**, not proof that engine references are lost or that a zero-loose-match gate is correct. Do not promote declaration similarity or absence of matches to an exporter identity claim. The embedded engine dataset used by the exact exporter and its generated Name mapping remain unverified.

Additional primary-source lead: upstream AssetRipper generator Pass504_FixShaderName at259caac0c7df906c94b80dd5a14d589787f67570 copies parsed name into asset Name during release/editor reads. The pinned CLI references AssetRipper.SourceGenerated1.3.2; inspect that exact generated binary/read method before asserting the same transformation for this exporter. No further original-image/raster repeats needed. Next reconstruct the exact embedded engine-cache mapping and verify full-export Material engine pointers, then propose a justified gate fix; separately close authentic water/FFT bindings. No new Unity/APK/XAPK run this cycle.
