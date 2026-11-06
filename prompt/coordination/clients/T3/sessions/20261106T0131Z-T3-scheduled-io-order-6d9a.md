# T3 scheduled — source-only SPIR-V reflection ordering fix

- session_id: 20261106T0131Z-T3-scheduled-io-order-6d9a; origin: scheduled; issue: RENDER-002 OPEN / NOT_READY.
- resumed_from: 20261106T005710Z-T3-chat-particle108-vulkan-c8f1; 20261106T0030Z-T3-scheduled-native-stage-order-e6b4.
- baseline HEAD: 797174cc02e14aef3f115a5917730a4068623c75; scope commit bd6027810fed3a9a32a9863c46bb3a1a7d764143; code commit 42a77991812983a9d2f682640b73d096badbcba6.
- Scope: scripts/t3_original_particle108_spirv_translation.py and tests/test_t3_original_particle108_spirv_translation.py; source-only, no game assets.
- Fixed false negative: the stage IO comparison used order-sensitive raw lists despite unique validated locations; comparing sorted location/type records avoids misclassifying reversed SPIR-V reflection arrays. Added a synthetic reversed-order regression. Did not change actual stage compatibility or original bytecode.
- The branch advanced during preparation; re-read current files, created a fresh tree and committed using expected-SHA without force. Original CI42141506120 established 8/8 Vulkan-valid stages but only 2/4 roundtrip pair interfaces compatible. This fix does not establish better interface compatibility or phone rendering.
- Validation: code change committed; local Python test and new CI result NOT VERIFIED. Next: inspect new CI, run targeted test if absent; then coordinate exact post-restorer Shader48 identity with T5. Owner phone artifact 42058825739 world/save/re-entry successful, white hand/raft and square smoke remain. T4 mouse and T5 UI untouched.
