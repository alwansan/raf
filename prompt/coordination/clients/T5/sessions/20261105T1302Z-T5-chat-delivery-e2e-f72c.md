# T5 chat — bundled Android delivery CLI integration

- session_id: `20261105T1302Z-T5-chat-delivery-e2e-f72c`
- origin: `chat`
- status: `active`
- resumed_from_sessions: `20261105T1248Z-T5-chat-linkport-6a19` and scheduled `20261105T1255Z-T5-scheduled-b7c2`
- base_sha: `8d16132dd39d490a2a45f9a8eea855271abfb818`
- issue_id: DELIVERY-013, resource_key: android-delivery-python-reassembler
- experiment_key: t5-bundled-release-script-execution-no-oslink-valid-synthetic-apk-obb-xapk-v1
- work_ids: `prompt/coordination/work/DELIVERY-013/T5-20261105T1302Z-T5-chat-delivery-e2e-f72c-bundled-reassembler-e2e.json`
- intended_files: `tests/test_t5_bundled_reassembly_e2e.py`, `.github/workflows/raft-t5-portable-reassembly.yml`, work/experiment/session/event files for this T5 only.
- run_urls: pending, no new native or Unity run.

## Resumed source and team baseline
T5 previous chat [source fix](https://github.com/alwansan/raf/commit/ee12bb7450d993e8cfb42ff17e165ea340aa00c8) and [24/24 CI](https://github.com/alwansan/raf/actions/runs/42030902212) verified Python missing `os.link` via synthetic direct-module fixture; not actual Termux phone. Scheduled T5 `20261105T1255Z-T5-scheduled-b7c2` independently inspected `package_android_delivery.main()` copying source script as `reassemble.py`; did not execute copied script. T4 original Android Load path compiled fixture [CI42031436693](https://github.com/alwansan/raf/actions/runs/42031436693) SUCCESS; T1/T2/T3 P0 projects separate. Actions at initial snapshot in_progress=0 queued=0; no native or other T jobs canceled. Owner's phone APK86 release still old, game NOT_READY 0/3.

## Independent scope
Hypothesis: The *actual* production `package_android_delivery.main()` script will copy byte-identical reassembler into the synthetic delivery, and that copied `reassemble.py` can function as a standalone CLI in a fresh Python process with `os.link` deliberately removed, rebuilding split XAPK and APK+OBB correctly. This is stronger than scheduled static copy evidence and direct importable-module tests.

Plan: write bounded Python synthetic integration test and run in existing isolated T5 source-only workflow. Create disposable valid tiny ZIP containers masquerading as APK and OBB; production packaging main with injected *size knobs only* to force multi-part splits and no real signing/device. Compare combined SHA256 and ZIP member bytes, require the bundled script match source exactly. Negative controls include corrupt part and existing signed output no-clobber; no original assets or source retrieved. No full Unity, release dispatch, .meta/GUID, water, local world, FMOD, Settings or touch changes.

## Pending
Record test commits, exact CI run ID/result/assertions; next actionable T5 task should be Unity/native-authentic graphics and world/save integration, not repeated scripted delivery checks without a new hypothesis.
