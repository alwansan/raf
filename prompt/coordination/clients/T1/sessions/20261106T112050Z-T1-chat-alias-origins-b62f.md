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

## Original-source validation — completed

- CI: [42209856944](https://github.com/alwansan/raf/actions/runs/42209856944) **SUCCESS** on source commit `1979568f7741872e6ac965fe7b73eee1d48f9331`; job 127865516249 completed all original SHA-pinned ZIP2 recovery, same-Vulkan FFT stages and private cleanup.
- New exact-source regression: `tests/test_t1_fft_spirv_alias_origins.py` **11/11 PASS**. Previous 16 CFG hazard tests also passed (and existing FFT tests passed). New tool: `scripts/t1_fft_spirv_alias_origins.py`.
- Authenticated original FFT slot0 report: **all X/Y source, butterfly1, butterfly2 alias pre-load categories = `indexed_access_static`**. Static alias-store count: source **4**, butterfly1 **4**, butterfly2 **8**. No exact-pointer-copy, dynamic-index, phi/select categories observed on those pre-load paths in this source fixture.
- Static index nature is not the literal index, memory-component identity or proof of the value that reaches the sampled coordinate. `full_reaching_definition_proven=false`, `original_integer_origin_proven=false` for all queried lanes.
- Prior result [42208932160](https://github.com/alwansan/raf/actions/runs/42208932160) narrowed direct writers to 1 per lane but exposed `alias_store`; current run explains its pointer shape, **not** actual correct X/Y integer values. No authored Unity kernel identity, numerical Vulkan↔Unity parity, or Android phone water fix claimed.
- Experiment: `prompt/coordination/experiments/T1/20261106T112050Z-T1-chat-alias-origins-b62f.json`; canonical event: `prompt/coordination/B_TEAM/events/T1/20261106T112050Z-T1-chat-alias-origins-b62f.json`; work record: `prompt/coordination/work/WATER-001/T1-20261106T112050Z-T1-chat-alias-origins-b62f.json`. No private payloads or SSA IDs published; audio, Settings, deferred touch and others' files unaffected. No new Android/XAPK build.

## Session handoff

- origin: chat
- status: **completed** (scoped original alias pointer classification)
- run_urls: https://github.com/alwansan/raf/actions/runs/42209856944
- next_step: create separate investigation of **component-specific** OpAccessChain static-index writes for each original butterfly X/Y coordinate lane, using original SPIR-V with private constant values retained only in runner. Distinguish original int carrier versus float bit interpretation and source code lowering without unsafe rewrite. Then controlled same-input Vulkan/Unity numeric parity, ultimately Adreno/device acceptance. WATER-001 stays OPEN.
