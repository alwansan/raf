# T2 independent source-free DUP regression
session_id: 20261109T1116Z-T2-scheduled-dup-contract-r8q2
origin: scheduled
issue_id: WATER-001
base_sha: 70ca4e1b5fad32c79533aff9bf19fe13a8f0bc39
status: completed
intended_files: scripts/tests/test_t2_foam_dup_source_contract.py; prompt/coordination/work/20261109T1116Z-T2-scheduled-dup-contract-r8q2.md; prompt/coordination/clients/T2/sessions/20261109T1116Z-T2-scheduled-dup-contract-r8q2.md
experiment_key: foam-cecil-backtrace-dup-ambiguous-source-contract-v1-program-9afeaf26
resource_key: none; source-only, no Unity or original binaries
hypothesis: source regression for ambiguous DUP should fail closed and never claim typed Texture instance; validate the actual C# implementation without private game assets.
coordination: T3 shader/effects, T1 FFT, T4 mouse, T5 Resolution/packaging untouched. No CI dispatch.
updated_at: 2026-11-09T11:16:00Z

## Result
Added two actual Mono.Cecil SelfTest DUP fail-closed cases to Program.cs and restored the previous synthetic stream before downstream getter assertions. Source commits 52bdb32b95cb7f7cc391ef90cebeb367d9cb6cb6 and 3d5afd9521a170ee1030a8199c3b5b57e6fc823b. Source-level review only: dotnet selftest and CI not yet run; do not claim PASS. No game assets, T3, Unity, or device modified. Next: execute dotnet --project android-port/Experiments/T2/FoamBlitOriginalProducers -- --selftest using established workflow and verify original-safe report.
