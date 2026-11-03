# A5 — HAPTICS-008 source investigation

- Session: A5-20261103T100200Z-541ecd0b; started 2026-11-03T10:00:33.759Z; base HEAD 0310e94d5c8d257c555acb0307cc670362d01e7c.
- Branch: feature/android-native-port ONLY. CL read-only. No Unity/Android/APK/OBB/XAPK/release; no automation changes.
- Read mandatory live prompts, owner requirements, AGENTS, coordination protocol/templates, and other clients' state/work/experiments. Existing A2 works DISPLAY-003; paused A1 works FFT-FORMAT-009; no discovered HAPTICS-008 competing plan.
- [CL 205608 report](https://github.com/alwansan/CL/blob/main/raft%20log/lf/LogRaft-20261102-205608-054/session-summary.json) reports 35 haptics path lookup failures from installed older game; exact resource failure and impact are not yet proven.
- Next: inspect exact raw CL lines, current source and staging, then test a scoped hypothesis. Do not infer old APK behavior from later source.

## Root-cause evidence — 2026-11-03T10:09:03.465Z
- Read exact CL raw segment blob cf26b883707d1bacceade526ff08498e0e6cf3f3: 35 DirectoryNotFoundException lines in HapticAudio.CreateAudioSources for /jar:file:...main.80...obb!/assets/Haptics/*.wav, comprising 29 distinct WAV names. All 29 names exist as tracked original StreamingAssets/Haptics files; not proven missing assets.
- Immutable APK80 source 9462f8edd8cdb5becbccb96521f2876ef9924410 lacked both the HapticAudio archive-reading adaptation and AndroidStreamingAssets class. Current source includes exact-SHA-pinned single File.ReadAllBytes replacement and production ZIP reader supporting /jar:file URI; no re-release since APK80.
- Planned independent tests link the actual C# reader; test-owned WAV-like bytes only, with named negative controls. They do not establish Android vibration or newer APK success.

## A5 final checkpoint (2026-11-03T10:17:46.997Z)
- Raw CL blob cf26b883707d1bacceade526ff08498e0e6cf3f3: 35 old APK80 DirectoryNotFoundExceptions across 29 distinct original Haptics WAVs; tracked sources present, on-phone OBB access unverified. Read A3 HAPTICS-008 coordination note and manifest CI41616535073.
- Original HapticAudio source SHA ac0ac86f62d05c774cb8b24cc8454df2b5356e50c6720395137df1730430fe9c; later exact adapter unbuilt for phone. New production jar: transport hardening and CPU tests source 387be6460bd914a6ba05e53eb31c4316b28c66d6.
- CI41617621699 completed SUCCESS: four Python checks, 69 C# assertions/58 synthetic ZIP reads, no LFS/Unity/Android; previous first runs41617107530 and41617439909 diagnosed/repaired. HAPTICS-008 real-device runtime remains OPEN. A5 work completed.
