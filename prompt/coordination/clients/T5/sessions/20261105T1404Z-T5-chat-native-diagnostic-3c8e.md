# T5 chat — one native diagnostic candidate
- session_id: 20261105T1404Z-T5-chat-native-diagnostic-3c8e
- origin: chat
- status: active
- resumed_from_sessions: 20261105T1348Z-T5-scheduled-7c91; 20261105T1302Z-T5-chat-delivery-e2e-f72c
- base_sha: 5eed7b6715a25177e733d17f383bb8735368bdbf
- work: prompt/coordination/work/INTEGRATION-001/T5-20261105T1404Z-T5-chat-native-diagnostic-3c8e-native-diagnostic.json
- experiment: prompt/coordination/experiments/T5/T5-20261105T1404Z-T5-chat-native-diagnostic-3c8e-native-diagnostic.json
- experiment_key: native-current-feature-original-water-explicit-limit-T4-AndroidSave-snapshot-20261105-v1
- resource_key: raft-native-engine-feature/android-native-port
- last real game: APK86 from 41812889049; T4 latest Android Save argumentFileSnapshot is newer and untested on phone.
- first Actions audit had zero nonterminal; later T1 Unity Vulkan source-free smoke appeared. Must recheck active heavy resource before request and preserve existing engine mutex.

## Plan
One owner-authorized, incompletely restored water, native APK+OBB/XAPK diagnostic on feature. Do not replace source, create fake flags or cancel jobs. Build can remain pending hours in GitHub; capture immutable run URL and avoid claiming phone success.

- next_step: investigate current native/Unity resource contention, then request one compatible run if clear.

## Native request actual execution checkpoint
- status: waiting_ci
- commit: 753802d75196210d721cca0f4fdec6ce7800bf0d
- workflow run: https://github.com/alwansan/raf/actions/runs/42042902522
- original head before trigger: 19f2af5a7940108ed4d9d6dc40b0cfd565e2644c
- exact push commit markers: raft-native-build and raft-device-test, existing approved full build/early delivery workflow.
- one native request only; T1 Unity Vulkan was active with shared raft-native-engine resource lock and cancel-in-progress false. No T1 cancellation or competing active native delivery observed.
- original water unmet names are explicitly copied from older working native trial request; live source gate will fail if these no longer match. This is NOT a green build or phone proof.
- next_step: inspect run step-level evidence, no duplicate, update completed result with exact verification.
