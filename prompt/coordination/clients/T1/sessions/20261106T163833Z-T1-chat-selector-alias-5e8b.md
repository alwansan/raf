# T1 chat — source-only FFT authored Unity selector-alias guard

- session_id: 20261106T163833Z-T1-chat-selector-alias-5e8b
- origin: chat
- status: completed (scoped guard, not WATER-001)
- issue_id: WATER-001 OPEN / NOT_READY 0/3
- base_sha: c7631ed7aef24cccc13e3efc7f9d5c38474eb0ed
- resumed_from_sessions: 20261106T161112Z-T1-chat-original-keyed-recorder-7be2; 20261106T1608Z-T1-scheduled-pair-gate-regressions-k7p4; 20261105T002257Z-T1-fft-unity-contract
- work: prompt/coordination/work/WATER-001/20261106T163833Z-T1-chat-selector-alias-5e8b.json
- experiment: prompt/coordination/experiments/T1/20261106T163833Z-T1-chat-selector-alias-5e8b.json
- event: prompt/coordination/B_TEAM/events/T1/20261106T163833Z-T1-chat-selector-alias-5e8b.json
- completed_at_utc: 2026-11-06T16:46:00Z

## Reason / live handoff and coordination

Read T_TEAM RESTORE_AR, CHAT_AND_SCHEDULE_AR, PROMPT_AR and canonical T_TEAM references, T1 latest sessions, work and CI. Original ZIP2 source pin 15964ea8f246b6e076ce26b60931ee2e1a9a2385 retained but **no game binary or original shader was read/committed**. Previous T1 actual original SPIR-V keyed Vulkan [42252268973](https://github.com/alwansan/raf/actions/runs/42252268973) SUCCESS with 384 reads (64/256/64) and original traced/untraced 64-pixel output invariance; independent HLSL keyed trace has same site counts but actual pair numeric comparison remains open.

Detected concurrently active **different T1 chat scope** `20261106T163310Z-T1-chat-real-fft-pair-d91e` on original-vs-HLSL same-input paired GPU trace. Explicitly did NOT alter `scripts/t1_fft_pass0_vulkan_trace.py`, `scripts/t1_fft_original_trace_vulkan.py`, `scripts/t1_fft_private_invocation_pair_report.py`, its CI, or its resource key. Scheduled T1 `20261106T1608Z-T1-scheduled-pair-gate-regressions-k7p4` works on pair gate synthetic regressions; not overwritten. Different independent source-only input: original staged Unity kernel-name + keyword identity contract.

## Engineering change and proof boundary

Previously `scripts/t1_stage_unity_fft_kernel_probe.py` authenticated 20 candidate rows but accepted two **different original compiled slots** mapping to an indistinguishable named Unity kernel and **identical enabled keyword set**. These slots cannot be resolved independently by the nominal probe selector; 20 input rows could therefore be falsely presented as 20 distinguishable runtime configurations. The new source-stage `selectors` set rejects duplicate `(kernel_name, sorted(keywords))`; the private Unity 2021 Editor probe performs the same check using `HashSet<StringComparer.Ordinal>` before calling `HasKernel` / `FindKernel` and validates bounded keywords without exposing their names. The positive source-only fixture retains **2 kernel names** but uses 20 distinct synthetic bank/resolution keyword combinations. An adversarial test rejects a bank0/bank1 selector collision even when keyword order is reversed.

**Changed production-source diagnostic files**:
- `scripts/t1_stage_unity_fft_kernel_probe.py` commit [4fa8d1ba](https://github.com/alwansan/raf/commit/4fa8d1ba8e34c0b5b785e7e0f110a25fc97bae0c)
- `tests/test_t1_stage_unity_fft_kernel_probe.py` commit [b898212e](https://github.com/alwansan/raf/commit/b898212e1d4878455961187aa9f1d263d9441770)
- `android-port/Editor/T1FftKernelRuntimeProbe.cs` commit [4b8b1552](https://github.com/alwansan/raf/commit/4b8b1552a9d84b9d2683a4a3230a3183f046a861)

The prepared multi-file expected-SHA git-ref update failed with a GitHub GraphQL error **before** branch publication (dangling local git object only); re-read live HEAD and confirmed the three target paths had their expected unchanged original blob SHAs, then published with per-file content SHA leases on the permitted branch, no force. Its separate work registration preceded source modification. Intermediate push [42255076430](https://github.com/alwansan/raf/actions/runs/42255076430) FAILED as Python source changed before synthetic manifest fixture; second [42255086500](https://github.com/alwansan/raf/actions/runs/42255086500) was CANCELLED by platform queue/concurrency, not manually cancelled by T1. **Final coherent source head** [42255094227](https://github.com/alwansan/raf/actions/runs/42255094227), job 128020186830, **completed SUCCESS** (Python tool parsed, all **8/8 source-only synthetic tests PASS**, including collision control).

## Limits and next

- This necessary guard proves no **declared nominal selector alias** in a passed staged manifest. It does **not** authenticate that keyword pragmas compile into distinct variant binaries or original author selection, and does not prove Unity C# compiled/runs: isolated source-only CI, not GameCI Editor.
- No actual authored original multi-variant `.compute`, kernel IDs, Android/Adreno water, new APK/OBB/XAPK, audio/Settings/touch changes. No another heavy CI/native build launched.
- WATER-001 remains OPEN, project NOT_READY 0/3. Next independent T1 scope should follow fresh paired trace result of `20261106T163310Z-T1-chat-real-fft-pair-d91e`, validate source/inputs first and then investigate first true per-invocation numeric difference. If working on Unity authored mapping separately, require source-authenticated actual variant keyword selection/Unity graphics tests rather than treating this nominal guard as game readiness.
- Session complete / scoped work file completed; index refresh may be performed by T5 once safe against newer shared ledger inputs.
