## 11 Nov 2026 — GFX124 Android batch shell built; export verified by replay

Session `20261111-GFX-chat-forward-android-batch-89`, origin=chat. Write only `experiment/android-graphics-rootcause`.

GFX124 reuses the GFX120 controlled draw and adds manifest-driven material slots, per-texture mip dimensions and color space, streamed mip uploads, shared-depth M03 composition, and isolated per-case errors. One MediaStore ZIP under `Download/Games/cl/test/g/` contains a summary and all available captures. Five currently prepared tests: M00/0, M02/0, M03/0, M03/1 and M03 combined. Four controls per individual slot plus one composite produce 17 reference captures.

[Actions 43052941770](https://github.com/alwansan/raf/actions/runs/43052941770) built the asset-free shell; artifact 13869298795. The local private assembly validation used the older unsigned shell only as a ZIP test harness (114 entries and valid CRCs), so the new APK has not been signed or run on Android. The new auditor verified a full Mesa replay (5 cases/17 captures), and a replay with one injected case error (4 cases/13 captures). Legacy GFX120 owner ZIP audit still passes. Prior GFX123-triggered Windows WARP, source variant, and mip regressions all completed successfully. No private textures, binaries, screenshots or logs are in the public shell.

Next expand the reference and runner scope for original pass states, Windows coverage on new models, original animation, and original PC scene comparison. Keep phone tests in one signed owner APK when the consolidated scope is ready. `phase_closed=false`.

