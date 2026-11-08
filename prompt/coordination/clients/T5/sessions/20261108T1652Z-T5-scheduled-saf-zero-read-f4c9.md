# T5 checkpoint 20261108T1652Z-T5-scheduled-saf-zero-read-f4c9

- identity: T5; origin: scheduled; session_id: 20261108T1652Z-T5-scheduled-saf-zero-read-f4c9
- resumed_from_sessions: 20261108T1541Z-T5-chat-large-saf-obb-sha-b73c; 20261108T1453Z-T5-scheduled-obb-telemetry-k8p2
- base_sha: 239d12d3bf826daa3051bd3b3b66abfe689b6962
- work: work/T5/20261108T1652Z-T5-scheduled-saf-zero-read-f4c9.md; issue DELIVERY-013 / T5 SAF large-file digest.
- scope reserved commit: 0553e4035849d7a1cf9269af306f22ea8eb3342e
- production commit: 869ba255b85d8b9cd258efd618106c1562597d23
- regression commit: 8b98dff0d371486aab03e3aae56f2422c1ad7a05
- hypothesis: malicious or broken SAF ContentProvider may return zero for nonempty bulk read indefinitely, leaving T5 digest stuck with no progress. Prior implementation continued forever; interruption check existed but a never-ending provider with no interruption still stalled.
- fix: reject after 16 consecutive zero reads with IOException, reset counter on actual data. Synthetic tests cover broken endless zero and three transient zero reads followed by valid data. No original game assets touched.
- CI: https://github.com/alwansan/raf/actions/runs/42502155293 pending at check (SHA 8b98dff0); earlier code-only https://github.com/alwansan/raf/actions/runs/42502134539 in progress (SHA 869ba255). Do not duplicate. Latest earlier passing https://github.com/alwansan/raf/actions/runs/42501358801 applies to prior SHA only.
- state: waiting_ci; tests not yet proven green. Next cycle check 42502155293 and repair any regression. Even if green, does not prove Android SAF provider behavior, signed game APK/OBB identity, Unity runtime, or phone acceptance.
- T4 mouse files untouched; no native Unity build or full XAPK dispatch. T5 mini APK 13624380481 is an older source build without this zero-read guard; if Android acceptance needs it, build a new mini APK only after source CI and scope review, not a full Raft build.
- owner baseline: 42058825739 world/save/reopen only, full NOT_READY 0/3.
