# T4 chat — native Android window focus and immersive bars

- session_id: `20261106T1334Z-T4-chat-windowfocus-m8v3`
- origin: `chat`
- base_sha: `2ec048fefdc2167fdd55faa2c2f5ce43f3082302`
- resumed_from_sessions: `20261106T1320Z-T4-chat-immersive-lease-v4n8`, `20261106T1304Z-T4-chat-null-activity-p7h2`
- issue_id: INPUT-005 (OPEN); status: active
- work: `prompt/coordination/work/INPUT-005/20261106T1334Z-T4-chat-windowfocus-m8v3-focused-window-guard.json`
- experiment_key: `T4-input005-android-windowfocus-v1`

## Scope reserved prior to source edit

Prior original Unity2021 managed ABI CI [42225179203](https://github.com/alwansan/raf/actions/runs/42225179203) succeeded for Activity-identity and generation guards. Android documentation says Activity.hasWindowFocus independently reports native main-window focus. A Unity focus flag can remain true during external dialogs or overlays. This cycle adds a native Activity window-focus requirement to the queued hide path, keeps original identity/generation and swipe/Back/Home behavior, then tests C# policy and original managed ABI in the existing isolated T4 immersive workflow. No native game build, packaged APK/OBB, original game assets, RGD data, shader/water or other agent code touched. 

Separate T4 original seven-world cross-process CLR scope remains active; T1/T2/T3/T5 existing CI was checked and is not cancelled or copied. Owner's 5 Nov game artifact proved world save/reopen on its older source only. No later phone test exists in the CL snapshot at 520c4cf.

## Next

Write the narrowed code/test changes and capture exact CI SHA, outcome and limitations here before closing source-only work.

## Implementation checkpoint — source CI pending

- Production guard + tests final commit [1496971](https://github.com/alwansan/raf/commit/1496971df6f14335b5d479d8cc488d7636a998be) on permitted branch. Changes: AndroidSystemBarPolicy overload with explicit boolean Android main-window focus, runtime UI callback `Activity.hasWindowFocus` checked before accessing the window and immediately before modern/legacy bar hide, five additional direct C# policy negatives and one source test. Original identity, generation, and Android transient OS swipes remain preserved. No touch, .rgd, game project or heavy build changed.
- Exact final existing T4 original-managed CI [42227039188](https://github.com/alwansan/raf/actions/runs/42227039188) pending. GitHub intermediate push runs 42227033115 and 42227024068 were cancelled by queue behavior without T4 cancellation; they are not final test evidence. T1/T2/T3/T5 CI remains independent.
- Hypothesis from official [Android Activity.hasWindowFocus()](https://developer.android.com/reference/android/app/Activity#hasWindowFocus()): Activity main-window focus is separate from lifecycle callbacks. A non-focused Activity must not be used to hide OS bars even if Unity focus flag lags. Source-only expected safety; no device validation or claimed fixed phone visual.
- Experiment `prompt/coordination/experiments/T4/20261106T1334Z-T4-chat-windowfocus-m8v3.json`, work `prompt/coordination/work/INPUT-005/20261106T1334Z-T4-chat-windowfocus-m8v3-focused-window-guard.json`. Next: inspect actual full final CI result, update status with exact pass/fail, T5 signed candidate acceptance. INPUT-005 OPEN and project NOT_READY 0/3.

## Final exact original-managed CI result

- [Implementation commit 1496971](https://github.com/alwansan/raf/commit/1496971df6f14335b5d479d8cc488d7636a998be) on `feature/android-native-port` changes only immersive runtime, policy, C# policy negative controls and Python source test. Overloaded `CanApplyQueuedHide` rejects native `hasWindowFocus=false`, even if Unity focused=true and Activity identity/generation match. Real Activity focus queried on the Android UI thread before window access and again at modern/legacy hide operations. Existing stale epoch/identity checks retained; no Android Java object retained across threads. Swipe/Back/Home exits preserved; no settings, touch, .rgd or resources touched.
- **[CI 42227039188](https://github.com/alwansan/raf/actions/runs/42227039188) COMPLETED SUCCESS** on exact final source `1496971df6f14335b5d479d8cc488d7636a998be`, job `127923107752`: **10/10 Python tests** incl native main-window focus regression, **33/33 executable C# tests** (five new negative/positive cases), pinned original ZIP2 binary SHA gate, and genuine original Unity2021 managed AndroidJNI/Core compilation. Runner explicitly printed `AndroidPlayerBuilt=false DeviceVerified=false`. Intermediate pending 42227024068/42227033115 were cancelled in Actions queue, not T4 manual cancellation or final failure.
- Android API3+ official Activity.hasWindowFocus reports actual main-window focus independently of the Unity lifecycle callback. The new gate is source-valid; actual Android focus loss/reacquire and whether bars stay hidden without obstructing system navigation remain unverified until owner phone test. Same-user world save/reopen remains proven only for previous owner artifact `42058825739`, not post-fix candidate.
- Work `prompt/coordination/work/INPUT-005/20261106T1334Z-T4-chat-windowfocus-m8v3-focused-window-guard.json` source scope completed; experiment `prompt/coordination/experiments/T4/20261106T1334Z-T4-chat-windowfocus-m8v3.json`. INPUT-005 OPEN; LOCAL-005 OPEN; NOT_READY 0/3. Next: T5: one immutable signed Raft APK with matching OBB and source SHA/versionCode/hashes, hardware mouse+keyboard plus native/system window focus/notification panel/home/menu transitions; preserve OS swipe/Back/Home and verify same world save force-stop reopen. Only device evidence establishes OS bars or camera success.
