# T1 — distinct FFT coordinate-zero vs float32 FTZ private diagnostic

- session_id: `20261106T1837Z-T1-chat-ftz-trace-89ac`
- origin: **chat** (this conversation, not scheduled)
- status: **completed scoped source-only test**; WATER-001 remains **OPEN / NOT_READY 0/3**.
- base_sha: `57d32472a8a70fbaca982fd7c661f1c5d4404a60`
- resumed_from_sessions: `20261106T181000Z-T1-chat-carrier-report-gate-4c7d` (last chat verified), `20261106T1808Z-T1-scheduled-unity-carrier-gate-m4k8`, `20261106T174500Z-T1-chat-phimerge-opengl-g6k2`.
- source provider: `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`, original binary **not accessed** this cycle.
- work: `prompt/coordination/work/WATER-001/20261106T1837Z-T1-chat-ftz-trace-89ac.json`
- experiment: `prompt/coordination/experiments/T1/20261106T1837Z-T1-chat-ftz-trace-89ac.json`
- canonical result event: `prompt/coordination/B_TEAM/events/T1/20261106T1837Z-T1-chat-ftz-trace-89ac.json`
- trial round `trial-20261106-r1`: **T1 لا يحتاج**, existing vote remains accurate, **no rewrite**. T4 previously needs; 5/5 not present.

## Evidence recovery and non-overlap

Read the current RESTORE_AR, CHAT_AND_SCHEDULE_AR, PROMPT_AR, T_TEAM README, TRIAL_BUILD_POLICY_AR, TRIAL_BUILD_READINESS.md, owner requirements/AGENTS/current device feedback, ZIP2 policy, latest chat and scheduled T1 work, original paired-Vulkan and synthetic Unity carrier C# outcomes. Source-only CI [42254539826](https://github.com/alwansan/raf/actions/runs/42254539826) authentic original-vs-translated Mesa Vulkan keyed fixture passed 384 reads, but separate Unity OpenGLCore genuine original-derived FFT [42198180194](https://github.com/alwansan/raf/actions/runs/42198180194) has major butterfly coordinate divergence. Prior Unity synthetic [42129683073](https://github.com/alwansan/raf/actions/runs/42129683073) reported subnormal-carrier 63/64 mismatches, while different bitcarrier and Phi sourcefree GPU tests [42261467757](https://github.com/alwansan/raf/actions/runs/42261467757) and [42264618337](https://github.com/alwansan/raf/actions/runs/42264618337) passed 320/320 each. These facts are not contradictory without exact identical shader instruction context and input.

Read T1 work and Actions. Initial branch HEAD `57d32472a8a70fbaca982fd7c661f1c5d4404a60`; independently active LOCAL-005 runner later terminated (and unrelated). Source-only T2/T3 workflows were active later on disjoint code. Reserved this work before changing files, session origin=chat, no collision with separate T1 scheduled original Unity investigation, no Unity engine resource key, no native request/cancellation or other team file changed.

## Actual engineering result

Created `scripts/t1_fft_private_unity_ftz_diagnostic.py` ([cec94bc](https://github.com/alwansan/raf/commit/cec94bc0e6c1490df02a3d8eb14fcf2b35812cc7)): private original-vs-candidate Unity declared pair-gate consumer. It composes existing SHA256-verified exact byte length, independent trace-file/role/site-count, same declared input SHA and dispatch SHA with keyed two-trace decoding. New aggregate per-site classification separates:
- nonzero source coordinates mapped to zero vs other coordinate drift, by axis;
- signed `float32` subnormal sample bits mapped to either signed zero **only for identical sample coordinates**;
- other same-address bitwise value mismatches;
- missing/extra invocation keys and skipped value comparison where coordinates differ.

Outputs only bounded counts and explicitly **false** authenticity, backend, FTZ causality, authored runtime mapping, Android-water/Adreno flags. In particular, unsigned producer declarations are not proof Unity executed the asserted program.

Added `tests/test_t1_fft_private_unity_ftz_diagnostic.py` ([4bcdd060](https://github.com/alwansan/raf/commit/4bcdd060e1b00cc044325d4aa48a260e18fa5cc1)) with 16 Python synthetic controls: exact match, x->0 collapse, y nonzero drift, positive/negative subnormal FTZ, non-subnormal float32 delta, signed-zero bit delta, value suppression when coordinate changes, missing/extra invocation IDs, wrong Unity role, mismatched SHA input/dispatch, altered digest, duplicate invocation key, hardlinked/symlinked private files, duplicate manifest key, public report redaction.

Extended T1-owned existing source-only `.github/workflows/raft-t1-fft-invocation-pair-gate.yml` with paths and exact test execution commit [04d1315](https://github.com/alwansan/raf/commit/04d1315be1021775480d68a8fecb9f9c660ec32d). Existing `ubuntu-24.04`, `cancel-in-progress:false`, 4min sourcefree CI budget and prior T1 tests preserved.

**Actual GitHub Actions result:** [42272859383](https://github.com/alwansan/raf/actions/runs/42272859383) at source SHA `04d1315be1021775480d68a8fecb9f9c660ec32d`, job `128081621126` **COMPLETED SUCCESS**. Inspected full job logs: **new 16/16 tests PASS**, previous T1 paired-trace tests and privacy step PASS. This is **true Python CI execution**, not merely static inspection. No original game data, shader, Unity GPU dispatch or phone were included.

## Limits, safety, handoff

No original SHA-private Unity keyed trace exists yet as a valid sample for this new tool; **no claim** of confirmed FTZ, root cause, shader repairs, water appearance, GPU output, original runtime kernel mapping, Android/Adreno execution or a new trial APK. The green source-only gate proves the diagnostic code's synthetic boundary and safe aggregation, not actual paired-game correctness. The original game Android APK tested by owner remains source `e9c358eda01785b65e4eb14f18723da426635628`, build artifact run [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739): owner entered/saved/reopened world, visuals and water still need work. Do not regress that result.

**Next step:** on a separate authorized licensed Unity 2021 OpenGLCore runner, acquire SHA-authenticated original FFT and exact original-versus-Unity same-input **real per-invocation trace**, including kernel name/FindKernel/group/texture binding/variant and dispatch evidence; run the private diagnostic on those two buffers plus trusted provenance and publish only taxonomy. Use result to decide whether to investigate FTZ lowering, coordinate SSA/CFG or texture binding; do not speculate and patch original game shader beforehand. No redundant CI/native build until that input is available. Keep T1 trial vote **لا يحتاج**, and coordinate with T5 for real platform test after a substantial integrated improvement.
