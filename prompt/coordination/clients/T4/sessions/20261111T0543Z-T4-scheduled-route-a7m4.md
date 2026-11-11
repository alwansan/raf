# T4 scheduled checkpoint 20261111T0543Z-T4-scheduled-route-a7m4
origin=scheduled
baseline=6ebe24010efe2ab98e73f830ad41b36b96061b88
work_plan_commit=362778c843c68fb46747b3e7eeb963afa8d26a30
source_test_commit=3e0bb4ed6f114d86dccc3ea250a8aa8687263ed6
scope=INPUT-005 captured callback semantics only; no overlap with T5 Resolution/unified mini.

## Owner evidence and restored context
- docs/DEVICE_FEEDBACK_42058825739_AR.md: artifact 42058825739 source e9c358eda01785b65e4eb14f18723da426635628: owner created, saved, exited and reopened world on phone. This is limited confirmed device behavior; preserve original .rgd and LOCAL-005 open.
- apk-for-testing/OWNER_FEEDBACK_2026-11-08_AR.md: physical mouse captured camera improves; LEFT RIGHT MIDDLE and scroll do not work in game. INPUT-005 open.
- Existing T4 MEMORY documents authentic 20 original Legacy Input calls in 12 source files, staged adapter and source-only CI42518143297 success. Do not mistake source CI for game runtime.
- Live HEAD before work 6ebe24010efe2ab98e73f830ad41b36b96061b88, 2026-11-11 05:34 UTC T3 commit. Recent Actions 42965476038 T2 source-only SUCCESS. No heavy CI requested or cancelled.

## Concrete work
Added tests/test_t4_capture_callback_semantics.py: four source-only tests of nonmove callback forwarding without consuming, scroll-only axis read, epoch-gated buttonWheel recording without fake InputSystem/keyboard events, and Unity Legacy keyboard axis preservation. No Android/Unity game source edits. Test file has not yet run in CI or phone; status SOURCE_ADDED_UNVERIFIED.

## Next
Run python3 -m unittest discover -s tests -p 'test_t4_capture_callback_semantics.py' -v in a checkout, repair failures if any; wire to existing cheap T4 CI after inspecting workflow overlap. Then obtain actual game callback vs legacy reader evidence on the same signed build for captured LEFT RIGHT MIDDLE V/H wheel, release/reacquire and keyboard; coordinate one shared mini through T5 only if needed. Do not claim device fix. Preserve settings, audio, original world save, touch, camera and T5 resolution scope.
