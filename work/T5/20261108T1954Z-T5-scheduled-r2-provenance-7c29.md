# T5 independent scope — 20261108T1954Z-T5-scheduled-r2-provenance-7c29
origin: scheduled
base_sha: 91861e53beea14468479b160c1045d5afbe35680
experiment_key: T5-R2-MINI-PROVENANCE-20261108
files: this work record and clients/T5/sessions/20261108T1954Z-T5-scheduled-r2-provenance-7c29.md only
shared_resource: none; no Unity, no duplicate Mini dispatch
hypothesis: the newly completed r2 shared Mini artifact may not include latest T3 direct-launch UI and must be distinguished from source HEAD.

Evidence: owner phone report docs/DEVICE_FEEDBACK_42058825739_AR.md; 2026-11-08 CL report apk-for-testing/OWNER_FEEDBACK_2026-11-08_AR.md. Current HEAD 91861e53. Shared Mini run 42517104924 SUCCESS at c5100411c50ec3b663fa9262eb68c49c95180f3e, artifact 13631588625 (ZIP 89216 bytes, digest sha256:f7f3bf586ebcfc61c55495ba037d5cdaead377a917441b84306977c2c75de0dc, expiry 2026-11-22T19:52:14Z). This is ZIP digest, not APK digest.

Source compare c5100411..91861e53 shows 15 newer commits and UnifiedLabActivity.java changed (+12/-1). Commit bef7f88 adds six T3 direct-launch buttons AFTER built source c5100411; thus r2 Mini cannot contain those exact buttons. Earlier T3 tap-to-open improvements may be present; do not conflate. The latest T5 SAF source gate 42517141318 failed at step 'Assert shared Android host calls proven SAF stream' while Arabic portrait source gate 42517141319 SUCCESS. Investigate stale guard vs real missing integration before modifying source. No new Mini build dispatched; coordinate T3 need and T5 readiness first. Raft world save/reload only confirmed for 42058825739; no new device proof, no signed APK/OBB pair match or FPS measurement.

Next: inspect failing SAF gate assertions and compare actual Java call path; repair guard or implementation with isolated tests. For next Mini candidate, ensure T3 bef7f88 included and source gates PASS, verify signer/embedded SHA and avoid redundant artifact. Preserve T4 mouse ownership and T1/T2 water scope.
