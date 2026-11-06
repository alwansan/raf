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
