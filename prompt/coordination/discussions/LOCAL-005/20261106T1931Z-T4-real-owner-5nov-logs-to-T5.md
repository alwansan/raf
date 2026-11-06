# T4 → T5 + scheduled T4: authenticated actual owner 5-Nov world/save/load logger census

**session:** `20261106T1918Z-T4-chat-owner-log-lifecycle-p6n2`; **origin:** chat; **branch:** feature/android-native-port; **issue:** LOCAL-005. Completed scoped source/real-evidence experiment; no game source edited.

## What the actual phone runtime recorded

Three owner Android `raft-logs` files from immutable [CL@520c4cf](https://github.com/alwansan/CL/commit/520c4cf409aa20a4db54ff80ed87d8807d9cba57) were read only inside an ephemeral 7-minute GitHub Actions runner, with exact Git commit and individual Git blob identity checks. Each session has complete event sequence and monotonic UTC; no `logging/queue_overflow` was observed. Static-only counters (no private ID or path):

| Original authored runtime boundary | 5-Nov log session 1 | Session 2 | Session 3 | Total |
|---|---:|---:|---:|---:|
| `WorldHasBeenLoaded.originalCompletionAssigned` | 1 | 1 | 2 | **4** |
| `SaveGame` enter/exit | 3 | 1 | 3 | **7** |
| `SaveWorld` enter/exit | 3 | 1 | 3 | **7** |
| `SaveUser` enter/exit | 3 | 1 | 3 | **7** |
| `Save.argumentFileSnapshot` nonzero | 6 | 2 | 6 | **14** |
| `Load<T>` enter/exit | 0 | 3 | 4 | **7** |
| `Load.argumentFileSnapshot` nonzero | 0 | 3 | 4 | **7** |
| `RestoreRGDGame` enter/exit | 0 | 1 | 1 | **2** |
| `RestoreUser` enter/exit | 0 | 1 | 1 | **2** |
| `Load.caughtException` | 0 | 0 | 0 | **0** |

These are **direct authentic phone log observations** for the *older* owner-tested 5-Nov artifact, consistent with owner-reported world entry/save/reopen, not mere synthetic-source tests. An original world completion marker is actually executed, never set artificially by the analyzer. They support a cross-session Save→Load *hint*.

**Hard limits:** JSONL events do not prove matching saved-vs-loaded world identity, process restart, returned deserialized object, persisted .rgd durability, or installed APK/OBB/source binary identity. This does not attest to the post-5-Nov fix or fix the remaining water/FFT/shaders/colors/mouse. No new phone trial approved or launched. `LOCAL-005` and `INPUT-005` OPEN, full readiness NOT_READY 0/3; r1 T4 `يحتاج` while T1/T2/T3/T5 `لا يحتاج`, **no 5/5**.

## Reproducible exact-source proof

- [Initial pinned CL CI42279653393](https://github.com/alwansan/raf/actions/runs/42279653393) **SUCCESS**, 7 source-only tests and 3 authentic phone logger files; noticed weakness: matching file *sizes* alone would not authenticate a direct caller.
- [RED CI42279906350](https://github.com/alwansan/raf/actions/runs/42279906350) test-only equal-sized fake JSONLs failed their missing `unverified_pinned_owner_log_git_blob` assertion exactly as expected.
- [Final CI42280021182](https://github.com/alwansan/raf/actions/runs/42280021182) **COMPLETED SUCCESS** on source [cba461ec](https://github.com/alwansan/raf/commit/cba461ecd1aebeb3a2e1bb67547ffa573c40d505): **8/8** synthetic guard tests and three exact CL blob-authenticated genuine phone logs parsed. No game DLL/world file, raw log detail, private user identity or RGD copied out of ephemeral runner; no published artifacts with raw content.
- New files only: `scripts/t4_owner5nov_jsonl_lifecycle.py`, `tests/test_t4_owner5nov_jsonl_lifecycle.py`, `.github/workflows/raft-t4-owner5nov-jsonl-lifecycle.yml`. Work completed/released at `prompt/coordination/work/LOCAL-005/T4-20261106T1918Z-T4-chat-owner-log-lifecycle-p6n2-owner5nov-jsonl-lifecycle.json`; experiment `prompt/coordination/experiments/T4/20261106T1918Z-T4-chat-owner-log-lifecycle-p6n2.json`; event `prompt/coordination/B_TEAM/events/T4/20261106T1930Z-T4-real-owner-world-save-log-p6n2.json`; [full session](../../clients/T4/sessions/20261106T1918Z-T4-chat-owner-log-lifecycle-p6n2.md).

**Next for T5:** retain this as the last phone-log execution baseline; when a separately authorized signed candidate exists, verify APK signed SHA/versionCode and matching main OBB name/bytes/SHA, collect fresh local user world creation/save/force-stop/reopen and real mouse pointer capture from the same installed package. Compare new actual marker sequences/CL with this baseline, but never call the real owner log positive hint a proof of .rgd durability or same-world identity. Do not rerun the already-green pinned 5-Nov workflow unchanged.
