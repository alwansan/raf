# T4 chat — actual original 5-Nov owner World Save byte-for-byte parity 7/7

- session_id: `20261106T1014Z-T4-chat-owner-world-wire-parity-n7q3`
- origin: chat
- issue_id: LOCAL-005, status: bounded_original_managed_wire_parity_success_device_unverified
- baseline_sha: `35c9e3191d52da100212930c1177745578a61d66`
- resumed_from_sessions: `20261106T0946Z-T4-chat-pointer-view-ci-q4r8`; `20261106T0943Z-T4-scheduled-q7n4`; `20261106T0246Z-T4-chat-original-owner-save-roundtrip-j4q8`
- original evidence resumed: https://github.com/alwansan/raf/actions/runs/42153533612
- experiment_key: `T4-local005-CL520c-owner7-original-Save-Load-wire-exact-byte-equality-original-zip2-15964ea8-source-guard-v1`
- work: `prompt/coordination/work/LOCAL-005/T4-20261106T1014Z-T4-chat-owner-world-wire-parity-n7q3-authentic-wire-byte-parity.json`
- experiment: `prompt/coordination/experiments/T4/20261106T1014Z-T4-chat-owner-world-wire-parity-n7q3.json`
- canonical event: `prompt/coordination/B_TEAM/events/T4/20261106T1014Z-T4-chat-owner-world-wire-parity-n7q3.json`
- source candidate: `22ebebb0e0638d3a970475fcbcb506a88945307e`
- final CI: https://github.com/alwansan/raf/actions/runs/42201568118 — **COMPLETED SUCCESS**, source SHA exactly 22ebebb0, job 127837973923, completed 2026-11-06 10:18Z.

## Question and actual new result

Prior source-authenticated original CLR Save→LoadT [CI42153533612](https://github.com/alwansan/raf/actions/runs/42153533612) proved 7/7 original Save methods wrote a nonzero temporary RGD and the original LoadT returned the same CLR root type. **It did not compare saved file contents.** This new independent source-authentic experiment asks whether the original private Save rewrites the seven actual owner-generated 5-Nov World .rgd inputs byte-identically.

The actual final job log `T4_OWNER5NOV_ORIGINAL_SAVE_ROUNDTRIP` reports:
- Immutable seven CL Git-blob original World inputs + exact ZIP2 original compiled DLL and 151 managed siblings SHA-authenticated before historical BinaryFormatter.
- `sample_count=7`, `original_guard_passed=7`, `original_private_Save_invoked=7`, `original_saved_file_nonzero=7`, `generated_original_LoadT_matched=7`, `private_temp_cleanup_proven=7`.
- **`original_private_wire_compared=7`, `original_private_wire_exact_match=7`, `original_private_wire_differs=0`.** Thus 7/7 exact input/output byte equivalence for original private Save in **isolated .NET8 CLR**. This is stronger than prior type-only result for these bounded files, without semantic guesses or public raw bytes.
- Python verifier: 12/12 staging + 29/29 original guarded Save/report tests = **41/41 source-free controls**, including rejection of fabricated wire evidence and acceptance of honest authenticated inequality.
- The one-byte tampering negative control was refused before unsafe formatter and no report was created.
- All original data, temporary binaries, per-world paths and private compile logs stayed in the ephemeral runner; the aggregate counts are safe. No game/source original payload uploaded.

## Exact changes

1. `android-port/Experiments/T4/OwnerWorldRgdRoundtrip/Program.cs` ([59a09852](https://github.com/alwansan/raf/commit/59a09852d92d7ef6b65782e572b8fbcbc4aa6b6f)): after genuine original private Save wrote an output, bounded <=1MiB private byte equality check, symlink checks, no file content/hash/name published; original safety and original LoadT/cleanup untouched.
2. `scripts/t4_validate_owner_world_roundtrip.py` ([405f53bb](https://github.com/alwansan/raf/commit/405f53bbac92a595cfb54d07eeb95ae05547aee8)): exact report schema with two boolean fields, reject exact match without an actual comparison, comparison without original Save, fabricated success without comparison; inequality alone is not treated as world corruption.
3. `tests/test_t4_owner_world_roundtrip.py` ([235035ff](https://github.com/alwansan/raf/commit/235035ff01288263185f09e0e8131cbe51f28636)): five new synthetic positive/negative/privacy tests, real original hashes still pinned.
4. `.github/workflows/raft-t4-owner-world-save-roundtrip.yml` ([22ebebb0](https://github.com/alwansan/raf/commit/22ebebb0e0638d3a970475fcbcb506a88945307e)): aggregate 7/7 comparison/equality counters only; original game bytes or per-world fingerprints never output.
5. Only T4 work, experiment, own session, event and T5 discussion contain evidence; no Unity runtime, original .rgd, meta, game scenes, touch, Settings, audio, shaders or other agents' sources changed.

CI first two intermediate runs 42201415098 and 42201473831 failed on partially updated validator/test schema from incremental pushes; subsequent 42201526690 and the **final immutable full 42201568118** completed success. Do not conflate intermediate source/report staging with real data or Android failure.

## Exact limits and continuation

This validates unchanged original BinaryFormatter wire bytes for **those seven immutable owner World RGDs on .NET8 using original SaveAndLoad.Save**. It does not establish on-device Unity2021 IL2CPP serializer behavior, Android persistent storage, actual in-game save sequence, progress after process death, or newer native APK gameplay. Existing 5-Nov owner world/play/save/quit/reopen remains owner-confirmed only for signed artifact42058825739; graphics/water and physical mouse still require device proof.

T4 scheduled q7n4 owns the separate ReleaseCapture focus/View hypothesis; no overlapping mouse runtime code changed. T1/T2/T3 and T5 work continued without cancellation or force. Next: T5's one exact signed APK+OBB pair including appropriate current source and SHA, then owner phone full-process exit/relaunch same world, Save/Load diagnostics, physical mouse/keyboard focus and cursor/camera verification. If that fails while original CLR 7/7 is byte exact, investigate Android-specific I/O, IL2CPP, lifecycle and host ordering, not speculative .rgd schema migration or fake completion flags. LOCAL-005 OPEN for new native candidate; NOT_READY 0/3.
