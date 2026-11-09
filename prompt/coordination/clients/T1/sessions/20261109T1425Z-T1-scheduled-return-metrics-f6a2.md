# T1 scheduled checkpoint — Dispatch return outcomes
session_id: 20261109T1425Z-T1-scheduled-return-metrics-f6a2
origin: scheduled
resumed_from_sessions: 20261109T1407Z-T1-scheduled-dispatch-result-4d91 (previous reported); 20261108T2022Z-T1-chat-fft-source-gate-d8b4
base_sha: b8ccc5f6f787b362e4b246961af5786d140f79ca
issue_id: WATER-001

## Owner evidence first
Read docs/DEVICE_FEEDBACK_42058825739_AR.md: owner entered/saved/re-entered world from run 42058825739 Artifact, while package publishing failed; source e9c358e. CL pinned 520c4cf has water-pass/kernel errors (session 220911: 23884/3850; 230108: 39132/6026), not GPU kernel identity. Newer 8-Nov session separately reports 74359 pass and 11165 kernel6 errors; never add these sessions. The original C# numerical 6 is conditional and NOT runtime kernel identity.

## Scope and change
work: prompt/coordination/work/20261109T1425Z-T1-scheduled-return-metrics-f6a2.md
code: 109e9436f93d30ad967cbd3cd7afd91dea3cd94e — add paired_count and failed_return_sequences; preserve returned_count as observed AFTER event count, including explicit failures.
tests: f292aa9a1cbb73ebac6612cf951a9df11abdfd32 — two synthetic regression cases (one failure and mixed outcomes).
Hypothesis: returned_count alone overstates successful paired calls. Explicit failed-return field distinguishes this without claiming GPU execution.

## Verification and limits
Reviewed source and tests via GitHub connector. Local git/network DNS unavailable; tests newly written but not executed. No Unity, Android, CL write, native build, or new GPU evidence. Actions listing latest observed completed CI 42607763178 T2, not this change. Mouse/Resolution owned by T4/T5 and not changed. WATER-001 OPEN / NOT_READY 0/3.

## Next
Run python -m unittest tests.test_t1_fft_dispatch_pair_audit tests.test_t1_fft_dispatch_pair_jsonl from repo root (or discover runner module layout); inspect actual Android trace schema and test FindKernel/Dispatch linkage, then obtain first numeric Vulkan-vs-Unity divergence from identical authenticated inputs.
