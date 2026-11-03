# A5 continuation — original WAV/ZIP reader verification

- New identity: raft-20261103T105730Z-a5e8b126, session 20261103T105730Z-b9430a2c, resumed_from completed raft-20261103T100200Z-a5c842e1.
- Started 2026-11-03T10:57:41.720Z on HEAD `d01f4c4bfab342dc2eba35c569151cac9b292973`; only `feature/android-native-port` writable. CL read only. No Unity/APK/OBB/XAPK/build/release, scheduled task edits or cancellation.
- Re-read required prompts and coordination. Previous A5 source reader guard commit 387be646 and CI41617621699 success (29 names/58 synthetic roundtrips). Historical CL 205608: 35 old APK80 HapticAudio `/jar:file:` failures across 29 WAV names; no new phone report. Latest old game release APK80/source9462f8e.
- A3 resumed `raft-20261103T105031Z-4b175384` with active staging completeness task. Do not touch their staging script/tests, metadata or manifests. Different experiment will read 29 *actual* original WAV payloads ephemerally, assemble private test ZIP and feed production C# reader, with SHA-256 comparisons; no raw payload published.
- Existing HAPTICS-008 old-source fixes not on phone. Keep NOT_READY/0-of-3 and runtime acceptance OPEN.

## A5 final checkpoint — 2026-11-03T11:05:04.577Z
- Source `76589b5d731b3f7f2323061487c2a633bd1d0ff0` adds separate authentic original WAV data CPU lane, never modifying original assets or A3 staging. Shared A3 staging gate subsequently confirmed CI41623215003; its source script remained outside A5 changes.
- [Actions 41624251634](https://github.com/alwansan/raf/actions/runs/41624251634), job125877475706, COMPLETED SUCCESS. Log: 4 Python adapter tests; 58 synthetic ZIP reads and69 assertions; source manifest29/29 Git WAV/32733104 bytes; **58 original-byte ZIP reads** via actual production AndroidStreamingAssets for jar:file and /jar:file, with byte equality and SHA256 equality; corrupt-but-valid ZIP byte difference detected by **test hash comparison**, not runtime WAV authentication.
- Recording: [A5 experiment](../../experiments/raft-20261103T105730Z-a5e8b126/authentic-haptic-wav-zip-roundtrip.json) and [coordination discussion](../../discussions/HAPTICS-008/20261103T110330Z-raft-20261103T105730Z-a5e8b126-authentic-zip-results.md). Exact passed CI must not be described as published OBB or phone proof.
- Scope completed. **HAPTICS-008 remains OPEN, NOT_READY/0-of-3** due to pending installed APK+OBB mounted-path and haptics acceptance, plus unrelated water/render blockers; no full Unity/APK/OBB/XAPK/Release or automation created.
