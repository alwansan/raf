# T4 scheduled checkpoint — 20261111T2140Z-T4-scheduled-reset-gate-p4m8
origin: scheduled
session_id: 20261111T2140Z-T4-scheduled-reset-gate-p4m8
branch: feature/android-native-port
start_head: e4701cf1af80c3685e7feb765d180f4818f13f4d
scope_commit: 09919e5f29c160dd9389f31f98509e3606fe1808
source_commit: 3e0cc3c9a9b21be935e8e0eb4b1a8f86266d2912
test_commit: d96f8ff6b0039ec5211dcdf5eff9217bd7ae739c
work: prompt/coordination/clients/T4/work/INPUT-005/20261111T2140Z-T4-scheduled-reset-gate-p4m8.md

## Evidence
Read owner phone report first: signed artifact 42058825739 world entered, saved, exited and reopened, while package publication failed. This is a limited original .rgd device success, not a current release acceptance. Latest 8 Nov owner mouse camera works; buttons and wheel fail in game. Existing authentic source bridge CI42518143297 succeeded, while CL native evidence is uncaptured (captured=false), not gameplay proof. Current HEAD at start e4701cf1. Recent T5 source CI43098774015 succeeded, T1 CI43101033840 failed, and CI43098764336 queued when checked; none is evidence of phone input.

## Work
Identified a real integrity gap: t4_capture_reader_summary.py already exports callback_counter_decreases and reader_counter_decreases, but gap classifier ignored reset metadata, allowing a 'both_grew' classification spanning process/epoch counter reset. Registered isolated scope, added fail-closed reset gate to scripts/t4_capture_gap_classifier.py, and added three regressions for callback reset, reader reset, and malformed reset values in tests/test_t4_capture_gap_classifier.py. Historical summaries without reset fields default to zero for compatibility. Source and tests committed to writable branch. No Unity/game code, .rgd, keyboard, touch, audio, Settings, or T5 Resolution/button layout changed. No CI run dispatched, no APK built, no phone test. Source-level change is NOT an INPUT-005 device fix. Local container could not resolve github.com for git clone, so tests were not executed in this run; next step run existing Python test suite through available source CI or local checkout when available.

## Next
Compare same signed game build/process Android capture ON epoch (captured=true, physical button and scroll), frame latch and original Raft legacy consumers; fix demonstrated boundary. Coordinate with T5 for shared Mini testpack and Resolution, without duplicate builds. Preserve LOCAL-005 limited success, INPUT-005 OPEN, NOT_READY 0/3.
