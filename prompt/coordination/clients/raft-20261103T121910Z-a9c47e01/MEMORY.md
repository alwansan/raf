# A9 — original StreamingAssets interrupted copy recovery

Registered 2026-11-03T12:19:10.900Z. Resumed from prior completed A9 RENDER-002 scope; no earlier identity reused. Read live owner requirements/prompt/AGENTS/STATUS/coordination/handoff, HEAD/commits/Actions/Release and historical CL. Game remains NOT_READY/0-of-3, older APK80 does not prove source-only fixes.

Previously considered original local RPC method scanner but A10 began active edits to the same `verify_android_offline_candidate.py` file; A9 did not commit that scope or overwrite A10. Prior unsuccessful SHA-lease attempts for an unregistered proposed LOCAL-005 ID created only detached Git objects and no branch files. Current unique scope AUDIO-004 affects only `scripts/stage_original_streaming_assets.py` and new A9 tests/workflow, not A10, A1, A2, A3 or A6 files.

Source defect hypothesis: direct `shutil.copyfile(source, target)` into final StreamingAssets bank/r.g.d file leaves partially written final target when copy interrupts; next invocation treats it as conflict, breaking recovery. Synthetic failure injection and robust per-file checked temp+no-overwrite publish; unchanged source bytes/sha256/.rgd schema/.meta/GUID. No LFS downloads, native Unity/APK/XAPK/OBB/release/tasks.
