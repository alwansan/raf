# T2 chat — SHA-original Foam pass1 callee reachable-return CFG topology

- session_id: `20261109T0155Z-T2-chat-original-cfg-topology-a8f5`
- origin: `chat`
- branch: `feature/android-native-port` (only writable)
- started_utc: 2026-11-09T01:55Z
- base_sha: `81f2eff9e0b677395b38aad4db959a36d04e5f03`
- resumed_from_sessions: `clients/T2/sessions/20261109T0141Z-T2-chat-cl-fourcase-ci-r6p2.md`, `clients/T2/sessions/20261108T1956Z-T2-chat-pass1-source-kind-4d6a.md`
- issue_id: `WATER-001` OPEN; no full Raft water acceptance.
- experiment_key: `T2-ORIGINAL-FOAM-PASS1-CALLEE-REACHABLE-RET-PREDECESSOR-CFG-SHA15964EA8-20261109`
- work: `work/experiments/20261109T0155Z-T2-chat-original-cfg-topology-a8f5.md`
- changed_source: `android-port/Experiments/T2/FoamBlitOriginalProducers/Program.cs` only, plus own scope and session records.
- goal: a separate reachable CFG topology category for SHA-original Foam pass1 called Texture method; no promotion of static type to runtime texture instance and no private original source leaking.

## What changed and verified (initial checkpoint)
1. Registered intended scope before source edits (commit `044296d60d7eb03d52334de305450aa10fdc76dd`). Confirmed no in-progress or queued Actions before modifying; T1/T3/T4/T5 own distinct files.
2. Added bounded, read-only return topology audit `ReachableReturnTopology`, from original Mono.Cecil managed method in private CI, max 128 IL instructions. Builds CFG for direct branch, conditional, switch, returns, throw and fall-through; rejects detached targets, invalid fall-through and exception-handler regions; classifies **syntactic immediate predecessors only** across reachable return sites, never dataflow or object identity. Only fixed categories logged; no original method/field names/offsets/IL emitted. Old original safe JSON unchanged.
3. Added synthetic fixtures for matching/mixed two-branch returns, direct return jumps, multi-edge merge, malformed branch/switch, exceptional method. Source commit `43340cb5a26e1cb439eb867f2623bbaf32b751fa`.
4. First CI [42548298389](https://github.com/alwansan/raf/actions/runs/42548298389) compiled Mono.Cecil and passed source-free Python but synthetic selftest BLOCKED prior to authentic private source staging. Review found selftest incorrectly expected two predecessors when a branch had only one return incoming edge; corrected the fixture to model an actual two-edge ret merge. Fix commit `615e8981c909b981a1afad7caf4087ec5ab9dc16`.
5. Second CI [42548419872](https://github.com/alwansan/raf/actions/runs/42548419872): source-free regressions, .NET compile+selftest, immutable ZIP2 source SHA + original managed DLL/staging all SUCCESS at last inspection; stage extract original Foam Shader name in progress. **Original method topology result pending until completion**. Job ID `128938373231`.
6. In parallel T5 wrote distinct shared Mini files; no cancellation or force; no modified T3 missing-event ledger issue (earlier CI42547293865) and owner T3 received separate coordination notice. Shared Mini T2 vote NO_BUILD, XAPK unrequested.

## Proof limits, next
- Even if original returned classification identifies a direct typed field, this is **syntactic CFG topology** only. It cannot establish live object instance alias, receiver identity, CB0 texture binding, original ShaderLab, Unity GPU or Android phone rendering.
- When run 42548419872 completes, inspect source-authenticated job and redacted `T2_FOAM_PASS1_CALLEE_CFG_TOPOLOGY` line. On failure check first failed stage and fix only T2-owned source, never bypass SHA or safety gates. On success record exact category, update this session/work, then plan actual return operand producer dataflow/receiver identity.
- Don't repeat CL-test 4-case gate (CI42547038822 SUCCESS, 15/15 Python + all 4 Git-verified owner logs) or create a duplicate Mini APK.

## Final result — source-original CI success

- **Run:** [CI42548419872](https://github.com/alwansan/raf/actions/runs/42548419872), source SHA `615e8981c909b981a1afad7caf4087ec5ab9dc16`, job `128938373231`, completed **SUCCESS** after the corrected source-free fixture.
- 17/17 Python tests PASS, Mono.Cecil synthetic selftest PASS, source immutable ZIP2 `15964ea8` and exact 3,211,776-byte original Assembly-CSharp SHA verified, 115,978,112-byte Shader-owner reconstruction SHA verified, original scan passed, original private source/symbols purged before safe artifact.
- Redacted original classification: **`T2_FOAM_PASS1_CALLEE_CFG_TOPOLOGY cfg_mixed_syntactic_return_predecessors`**. Pass0 `not_call_return_source` as expected (typed field). Prior original pass1 body family `original_method_branch_flow` remains valid; reverse source type `Texture typed_call_result steps=21 void_calls=1` unchanged.
- **Conclusion:** Original callable Foam Pass1 return has multiple syntactic immediate predecessor families across reachable `ret` sites. This is a higher-resolution structural observation, *not* proof the returned object is non-null, a RenderTexture, or same instance as pass0 target; no field/receiver/local aliases or pixel accuracy proven.
- Source code and regression: `android-port/Experiments/T2/FoamBlitOriginalProducers/Program.cs` only. New report: `docs/T2_FOAM_SHA_ORIGINAL_RETURN_CFG_2026-11-09.md` at commit `0df01dd7b144d4473b17bd627b4a2e7718ca4ffa`. Own work record now `completed_scoped_original_cfg_diagnostic`.
- Earlier failed [CI42548298389](https://github.com/alwansan/raf/actions/runs/42548298389) was only a new synthetic fixture edge-count expectation, **not** authentic source failure. Fixed in `615e8981`, verified by new successful run; do not cite failing run as completed proof.
- **Handoff:** The next original source experiment is a **bounded path-sensitive CIL return stack/local/receiver def-use analysis across branches and joins** with fail-closed EH and virtual dispatch. Only if a unique original instance alias is proven, compare pass0 destination with pass1 source; then CB0/sampler/ShaderLab/Unity pixel steps. Do not rerun generic GLES Mini, do not request a new XAPK without group gates, keep WATER-001 OPEN and T2 shared Mini **NO_BUILD**.
