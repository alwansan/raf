# T5 scheduled scope — scene epoch regression

session_id: 20261107T2345Z-T5-scheduled-8c4a
origin: scheduled
branch: feature/android-native-port

## Evidence and scope
Owner device feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md; 42058825739 proves phone save/re-entry only on its artifact. Previous T5 source fix 00dead1b77a59cdc7d87a3c9f26fbaa68fc27b40 adds scene lifecycle boundaries to scripts/t5_unity_interval_epoch.py, but tests/test_t5_unity_interval_epoch.py at inspection lacks lifecycle-specific regression cases. Work only on tests/test_t5_unity_interval_epoch.py, then unique session file. No Unity, no shared mouse or display source edits, no native build.

## Hypothesis and experiment
A->B->A scene events with no performance sample in B must produce two epochs; unrelated events must not split; scene unload must split. Test with deterministic synthetic JSONL rows, not device performance. Key T5-SCENE-EPOCH-20261107-8c4a. Shared resource: none. Next: run source-only CI and compare CL event vocabulary before inferring phone results.
