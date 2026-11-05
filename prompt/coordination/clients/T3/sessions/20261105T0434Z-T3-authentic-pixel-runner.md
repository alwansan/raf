# T3 isolated recovery 20261105T0434Z-T3-authentic-pixel-runner

Identity T3 only. Resumed from 20261105T0332Z-T3-pixel-ci-review. Shared state/MEMORY is stale and several independent T3 sessions exist: paused_identity_conflict for shared writes, no overwrite of another session. Branch feature/android-native-port only.

Baseline HEAD at reading: 6c6593f6094e38bc8c204bdbb7e539acd0c4a747. Existing real original/export streamed workflow and eleven+three pinned ZIP2 providers inspected; 41946037472 verified 106/106 importer closure, 41955404774 passed 11 synthetic pixel checks. No decoded original pixel comparison had run. Existing T1 workflow 41959712898 failed Unity license boundary; no Actions canceled.

## Engineering change
- 71733e0ff10cd4d5e24671629ce3a38d12b6348e: new scripts/t3_authentic_decoded_pixel_export.py: source 41-Material typed links → exactly 106 unique Texture2D source IDs → same-instance B02 trace GUID → actual exported PNG .meta → UnityPy decoded original RGBA → PIL exported PNG; compare all RGBA channels with existing T3 guard. Fail closed for missing/duplicate/unverifiable identity, unsupported source decoding, incomplete scope. Public output aggregate only, no raw images/IDs.
- 18cf01a2395ef4c8e5a6fdbb1cdb26c13a83b567: wire real comparison into existing T3-only 45m ZIP2 SHA-pinned genuine export workflow, Pillow pinned 11.3.0; publish aggregate even on failure. No game asset edits, no .meta/GUID modifications, no Unity/Android test.
- Original source 15964ea8f246b6e076ce26b60931ee2e1a9a2385; three .resS providers 2262546672 bytes authenticated by workflow. Previous source tests alone never proved decoded pixels.
- Potential limitation: source decoder may yield unsupported formats; those must remain explicit, never silently normalized. Pixel parity is still not GPU sRGB/lighting/ShaderLab or phone proof.

Next: inspect new workflow Actions run, distinguish source decoder errors vs real pixel mismatches; fix any schema/decoder issue with a single evidence-based patch. If 106 paired, classify exact/orientation/alpha/RGB and inspect shader/variant on actual device next. RENDER-002 OPEN; NOT_READY 0/3. Do not touch audio, Settings, deferred touch, or other T agents.
