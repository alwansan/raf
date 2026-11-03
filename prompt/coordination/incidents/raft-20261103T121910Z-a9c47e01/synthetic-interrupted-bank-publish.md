# A9 synthetic original asset partial copy, now guarded

Reporter: A9 `raft-20261103T121910Z-a9c47e01`, 2026-11-03T12:31:14.674Z; AUDIO-004. **Synthetic reproduced source defect, not an observed installed APK failure.**

Before source fix, `shutil.copyfile(source,target)` could expose a partial final `VO_npc_english.bank` or `VO_logs_english.bank` after an OSError/changed bytes. [Red CI 41634964894](https://github.com/alwansan/raf/actions/runs/41634964894) had 2/2 actual test failures. Initial guarded copy retained temporary under StreamingAssets, shown by [red CI 41635663572](https://github.com/alwansan/raf/actions/runs/41635663572); an abrupt exit could leave this path eligible for Unity packaging.

Source [44af18c72390b0193a3ee8f9bf068b76feb771d5](https://github.com/alwansan/raf/commit/44af18c72390b0193a3ee8f9bf068b76feb771d5) now copies at project root outside Assets, verifies temporary size+SHA256 before exclusive final hard-link, never replaces already-existing final files and removes temp on ordinary error. [Final CI 41635870775](https://github.com/alwansan/raf/actions/runs/41635870775) 4+11 tests success. Genuine bank bytes, OBB on phone and actual kill tests unverified; hard kill may leave an orphan outside Assets. Limited source integrity incident resolved, AUDIO-004 and RENDER/WATER readiness remain open, NOT_READY/0-of-3.
