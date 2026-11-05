# T4 → T5 / LOCAL-005: next native-candidate observables

T4 source-integrated `save/Load.caughtException` on original `SaveAndLoad.Load<T>` catch, without modifying original return, Deserialize, world flags, save bytes, audio/Settings or deferred touch. This is not an exception suppressor or success flag.

- Exact new original proof: [CI41939908432](https://github.com/alwansan/raf/actions/runs/41939908432), 16/16 tests and pinned original private loader, `Deserialize=1, catch=1, Binder assignment=0`. [Report](../../../../docs/T4_ORIGINAL_RGD_LOAD_COMPAT_2026-11-05.md).
- Actual original managed C# compile after source injection: [CI41939846508](https://github.com/alwansan/raf/actions/runs/41939846508) PASS `exit=0`, 14 original sources. This is NOT Unity native/IL2CPP or phone.
- T5 native build coordination: inspect Actions first and **never cancel** any existing workflow; create separate workflow/job if needed, consume the newest canonical branch and immutable ZIP2 provider. Preserve original `.rgd`, Steam stats guard and local-host/SaveWorld semantics. APK86 is obsolete for testing new fix.

The first relevant device session needs `WorldHasBeenLoaded.firstMoveNext`, `OnWorldRecieved` begin/end/exception, `SaveGame`, `SaveUser`, `SaveWorld`, `Load` begin/end, new **`Load.caughtException`**, and the physical `.rgd` save path (redact personal file names if needed). Capture new world creation, save, clean restart and actual load to playable state, with persistent bytes/hash evidence; do not treat operation end, no exception or an UI message alone as success. If caught-loader marker occurs, inspect original error stack and version/type binder only then; B37's historical seed version mismatch alone cannot justify schema migration.

LOCAL-005 OPEN; NOT_READY 0/3. This is a handoff note, not an authorization to interrupt running jobs or change T5 ownership.
