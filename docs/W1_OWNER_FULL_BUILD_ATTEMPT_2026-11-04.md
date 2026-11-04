**Final actual outcome:** native41741108965 FAILED beforeUnity at strict builtin0/142matches; noAPK/OBB/XAPK. See [follow-up source proof](W1_NATIVE_FAILURE_AND_ENGINE_REFERENCE_PROOF_2026-11-04.md). Historical in-progress observations below are superseded.

# W1 owner-authorized full delivery attempt — 4 November 2026

Latest explicit owner request asks to continue engineering and attempt a complete project/XAPK build through the existing native workflow. This authorizes this single experimental attempt despite historical build-hold instructions. It does not close any readiness blocker: **NOT_READY, 0/3**.

Implementation source: [a2e143246](https://github.com/alwansan/raf/commit/a2e143246ff29dfdfb9f2a68301d3aae6a38eeeb).

- Native scene acquisition now reuses the authenticated full14 ZIP2 owner cache, plans only missing files, and reassembles pinned ZIP2 input if necessary. The three original scene owners are staged only after their SHA/size also match the feature branch's original LFS pointers. No new selected-three LFS fetch; remaining graphics hydration provider is unchanged.
- A read-only aggregate audit inventories actual exported Material Shader PPtrs across .mat/.asset/.unity/.prefab documents, resolving exported Shader .meta references and separately counting internal E/F engine pointers. It rejects null/malformed/unsupported references and duplicate Shader GUIDs in its report. Its diagnostic outcome never substitutes for internal-pointer authentication or original Material association proof.
- The real water source report is captured before the existing strict builtin gate, so a failure there no longer hides water source evidence.
- Both existing strict builtin and water gates are unchanged. No source substitution or authenticity bypass. The water verifier still requires genuine identity evidence and cannot be cleared by pass-count-only stubs.

Validation: **45/45 local W1 tests PASS**, including8 new read-only graph/negative-control tests. Workflow YAML and embedded Python parsed; feature pointer regex exercised. No actual Unity/game/phone result is inferred from those checks.

One full native/device delivery request follows this source checkpoint. It must run on its immutable request commit, serialize on the existing native mutex, and retain existing original-data/FMОD/compilation/signature/packaging gates. No active/queued runs were observed before requesting. No cancellation, scheduler modification or protected-branch write.

Expected useful evidence is the actual full-export Material graph and water report. Existing original built-in zero-loose-file gate can still stop before Unity, and WATER-001/RENDER-002 remain open. Do not repeat an identical attempt; use the new evidence to repair the demonstrated blocker. If the job exceeds10 minutes and only waiting remains, provide the exact run link per owner preference.

Actual run: [41741108965](https://github.com/alwansan/raf/actions/runs/41741108965), immutable source `2cb893434d7c819f085d52b34fad1e6568db4ae8`, **IN_PROGRESS at last observation**. Explicit request gate steps succeeded. Code-source independent reconstruction preflight41740993327, platform41740993260, runner guard41740993213 and A5 OBB CPU contract41740992797 all **SUCCESS**. Native result/XAPK not yet available. Session paused per owner's long-build wait preference; job continues independently in GitHub Actions. First continuation action is inspect this exact run, not request another.
