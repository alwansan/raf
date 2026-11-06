# T1 — Original private FFT alias-store pointer origin diagnosis

- session_id: 20261106T112050Z-T1-chat-alias-origins-b62f
- origin: chat
- status: waiting_ci
- issue_id: WATER-001
- resumed_from_sessions: 20261106T110543Z-T1-chat-cfgreach-f4d9; 20261106T103645Z-T1-chat-storewriters-b4a7
- base_sha: b99ef9265be8acbc5f0618789be04831c27f513a
- work: prompt/coordination/work/WATER-001/T1-20261106T112050Z-T1-chat-alias-origins-b62f.json
- scope_commit: bdddc28635ac5a19dc4cd0ab2872498bbb259abb
- source_commit: b5ae0d1e0582a90d929ef2ed4ce1f9a7c679ba21
- test_commit: a556219077fe65333e53ad64753046a2e5cdb551
- workflow_commit: 1979568f7741872e6ac965fe7b73eee1d48f9331
- run_urls: https://github.com/alwansan/raf/actions/runs/42209856944

## Restart evidence

Prior original FFT CI 42208261641 narrowed three source/first-butterfly direct stores to one reachable per load and eight second-butterfly direct stores to one; original CI 42208932160 passed 16/16 source controls and showed `alias_store` on X/Y in all three sites. This means no complete reaching-definition or original integer-coordinate proof. Audio, Settings and deferred touch remain outside scope; no changes to T2–T5 files or native builds.

## Registered plan and implementation

`scripts/t1_fft_spirv_alias_origins.py` classifies pointer alias write forms (exact OpCopyObject same pointer type, static/dynamic indexed OpAccessChain, OpPhi, OpSelect), and identifies the category of alias stores that may precede each source-authenticated coordinate load using bounded per-function CFG. The reporter emits only safe aggregate categories and may-path labels; no private SSA IDs, constants or shader assets. Added `tests/test_t1_fft_spirv_alias_origins.py` with 11 synthetic/negative controls and appended both to the isolated non-Unity original FFT Vulkan workflow. No shader/asset/game source rewritten.

## Evidence pending

Actual exact-source run 42209856944 triggered by workflow commit 1979568. At checkpoint, queued. Do not treat source-only results as original Unity kernel ID, numerical pixel parity or Android water fix.

## Next step

Check run and read only allowlisted RAFT_T1_FFT_ALIAS_POINTER_ORIGINS marker, identify whether site1 X/site2 X/Y remaining pre-load aliases are exact-pointer copies, indexed component writes or conditional merges. If tests fail, repair minimal defect with checked latest blob SHA. End with complete event/experiment/work and session result.
