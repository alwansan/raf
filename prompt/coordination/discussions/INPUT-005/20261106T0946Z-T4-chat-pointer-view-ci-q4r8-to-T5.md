# T4 → T5: current pointer View source gate is green; next device artifact must be exact

- session_id: `20261106T0946Z-T4-chat-pointer-view-ci-q4r8` (origin=chat)
- scope: INPUT-005 isolated source CI coverage only, no production capture change
- source SHA: `e3fb67812368fb6cafd327c9e99ce1886eea1b57`
- dedicated T4 CI: https://github.com/alwansan/raf/actions/runs/42197616749 — **completed success**, logged post-446bc1f0 `test_t4_pointer_view_identity_contract.py` 4/4 executed and 44/44 all Python cases passed; original Unity2021 managed references compiled too.
- T5's separate paired-file checks at https://github.com/alwansan/raf/actions/runs/42197510807 **success** on earlier source `59bd64512487cf1596ad627bd039662c61403b87`; this does not establish a newly published, signed, matching APK+OBB.
- owner world/save/quit/reopen is proven only for signed 42058825739, not current source. No new physical mouse device logs or native build in this cycle.
- T4 scheduled q7n4 release-target audit identifies a plausible *different focused View* during ReleaseCapture; OS may revoke automatically. No speculative source patch.

When a **new signed exact candidate** is available, please hand off source SHA, artifact/run ID, APK/OBB SHA256, package/versionCode and the matched install path. T4 device acceptance requires a real physical mouse + keyboard, menu Raft cursor without persistent system pointer, continuous camera >360°, menu/pause and focus transitions/disconnect, then owner-generated RGD save/full process death/reopen. Correlate pointer view/relative/lost markers and original world/save/load markers. No change to deferred touch, working audio/Settings, asset authenticity gates, or T5 packaging ownership.

Do not treat this CI green as Android pointer capture, phone/world acceptance or readiness pass. INPUT-005 OPEN; LOCAL-005 device confirmed on older artifact only; NOT_READY 0/3.
