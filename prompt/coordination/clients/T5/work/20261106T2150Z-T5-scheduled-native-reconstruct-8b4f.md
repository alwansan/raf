# T5 independent native reconstruction watch

session_id: 20261106T2150Z-T5-scheduled-native-reconstruct-8b4f
origin: scheduled
issue_id: DELIVERY-013 / INTEGRATION-001
base_sha: 75cf40a1f112a45f7f47a695d9ed70a9633f1699
status: waiting_ci
intended_files: prompt/coordination/clients/T5/work/20261106T2150Z-T5-scheduled-native-reconstruct-8b4f.md; prompt/coordination/clients/T5/sessions/20261106T2150Z-T5-scheduled-native-reconstruct-8b4f.md
experiment_key: native-reconstruct-42296450023-a1737bd736e276d53df808442cfae3b1eea0d488
resource_key: unity-2021.3.45f2-native-reconstruct-42296450023 (read-only, owned by running workflow)
hypothesis: existing native run may expose actual Unity/IL2CPP integration errors; do not infer phone behavior from source-only tests.
source: https://github.com/alwansan/raf/actions/runs/42296450023
observation: run in_progress, reconstruct job 128163021015 at Unity Editor 2021.3.45f2 Android import and compile; native-request-gate and unity-license-preflight succeeded. No equivalent dispatch permitted while active.
related: https://github.com/alwansan/raf/actions/runs/42298819268 completed success 17/17 synthetic delivery tests on 0345ee05da47cbdb7dc679b80e20c3ade2a79f81. Earlier ZIP conflict CI42283255333 success.
next: check exact reconstruct conclusion and logs; if failed isolate compiler error without changing T1/T2/T3/T4-owned files; if succeeded verify produced APK/OBB/XAPK artifact hashes, signing, versionCode, OBB name and delivery manifest. This run predates cross-pass packager fix.
