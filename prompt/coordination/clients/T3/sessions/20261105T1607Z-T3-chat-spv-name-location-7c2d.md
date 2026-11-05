# T3 chat — original Shader48 interface reflected-name preservation versus SPIR-V Location remapping

- session_id: 20261105T1607Z-T3-chat-spv-name-location-7c2d; owner T3; origin chat; status active; issue RENDER-002 OPEN; branch feature/android-native-port; base_sha 8d7cf4b47d739fdf9bed8873e992d8ffb29195e3.
- resumed_from_sessions: 20261105T1542Z-T3-chat-io-drift-integration-a6d9, 20261105T1526Z-T3-scheduled-iosem-6c42. 
- Evidence CI42058881426: SHA-pinned ZIP2 six original scenes, four owners; source Shader48 selected by 921 Renderer material-slot uses; 8/8 valid D3D11 to SPIRV to derivative HLSL roundtrip, unchanged resource slot dictionaries 8/8 and type multisets 8/8, input remap candidates 8/8 and output 4/8. No DXBC semantic correspondence proven.
- Question: determine if per-location reflected private interface name+type identity survives numeric-location relocation. Report only aggregate, never names, source bytecode, SPIRV, HLSL, hashes or paths. Reflected name may be generated and is NOT proof of original DXBC semantics.
- Team actions: independent native 42058825739 and T2 ledger refresh 42061316352 active; no interference. No Unity shader, meta, GUID, scene, prefab, save or audio/Settings touch.
- work file: prompt/coordination/work/RENDER-002/T3-20261105T1607Z-T3-chat-spv-name-location-7c2d.json; current result pending. RENDER-002 OPEN.
