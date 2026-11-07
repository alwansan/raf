# T4 checkpoint — owner-tested artifact preservation priority

- session_id: 20261107T0635Z-T4-scheduled-owner-artifact-priority-r8m2
- origin: scheduled
- base_sha: f050bc49a5f33da3caebf1300def070e1a044dd3
- scope_commit: 4b2a3182e62af139febf8fb215ae30aa3fd0d8b0
- resumed_from_session: 20261107T0538Z-T4-scheduled-artifact-lease-m7q4.md; prior chat checkpoints in clients/T4/sessions
- issue: LOCAL-005 (remains OPEN), INPUT-005 (device mouse unconfirmed)
- work: prompt/coordination/work/LOCAL-005/20261107T0635Z-T4-scheduled-owner-artifact-priority-r8m2.json

## New independently verified retention priority

The **owner-tested** artifact is the highest-priority preservation target, not just the newer untested package. GitHub API `/actions/runs/42110297871/artifacts` on 2026-11-07 returned artifact **13454900880**, `t5-retained-native-delivery-42058825739`, 5,948,243,834 bytes, `expired=false`, expires **2026-11-08T21:12:40Z**; archive digest `sha256:41bf01f9991521fac876c591b75adc19b493ad47882687846e5aae1c2af6a3ef`. Link: https://github.com/alwansan/raf/actions/runs/42110297871 . This is the rescued delivery associated with owner-tested run 42058825739, not cryptographic proof of which APK/OBB was installed.

The **newer, not device-tested** build run https://github.com/alwansan/raf/actions/runs/42296450023 at immutable source `a1737bd736e276d53df808442cfae3b1eea0d488` still retains signed checkpoint **13550196498** (2,974,171,581 bytes, expires 2026-11-09T23:48:15Z, digest `88e588fbddc4d55997b92fc3845a5c044f77e8a45b92ebe2ac1ee12340ae9a2e`) and delivery **13549514149** (5,948,365,703 bytes, expires 2026-11-09T23:49:06Z, digest `885502613c39f8388b692b65cd7e33ad7b6c49783e83f705e31177d6b9a3c233`); both `expired=false` at check. These archive digests are not per-APK/OBB hashes. GitHub release publishing previously failed HTTP403, so the existence of Actions artifacts is not evidence of successful release.

## Engineering decision and boundaries

**Preserve artifact 13454900880 first** before 8 November 21:12:40 UTC (one day earlier than the newer artifacts). T5 owns delivery; coordinate a non-Unity archive recovery and independently verify extracted APK signature, versionCode, OBB name/size/hash, transport manifest, and source provenance. Do not overwrite or confuse the two candidates. No authenticated binary download was possible through the text-only GitHub connector; no archive was copied, no CI was launched, and no phone test was run.

Owner-confirmed phone outcome on run 42058825739: world entry, save, exit, reopen succeeded; preserve as scoped evidence, not generalized Android readiness. Mouse camera relative movement, Raft menu cursor, pointer capture lifecycle and keyboard still require device testing; T4 physical-mouse fixes remain source/CI only. T5 handles three-button placement and Resolution. CL pinned source and screenshots are linked in docs/DEVICE_FEEDBACK_42058825739_AR.md. T4 vote remains `يحتاج` for trial-20261106-r1; 5/5 consensus absent. No new native build request, no change to original .rgd/.meta/GUID/audio/Settings/touch.

## Next step

Before the earlier deadline, T5 should recover owner-tested delivery artifact **13454900880**, then recover newer checkpoint/delivery if storage permits. If a new signed candidate reaches the device, compare pointer capture and keyboard, world reopen and save regression, and resolution without claiming source CI is device proof. This checkpoint does not replace other T4 sessions or shared memory.
