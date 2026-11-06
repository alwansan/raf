# T1 | 20261106T103645Z-T1-chat-storewriters-b4a7

- session_id: 20261106T103645Z-T1-chat-storewriters-b4a7
- origin: chat
- status: active
- resumed_from_sessions: 20261106T101340Z-T1-chat-2f6a; 20261106T1009Z-T1-scheduled-k7m2
- base_sha: 13e03d803b7820d3fabe31cd502abadf20c97be2
- work_id: prompt/coordination/work/WATER-001/T1-20261106T103645Z-T1-chat-storewriters-b4a7.json
- scope_commit: 9939983d9978a3703b6b6bc8228a53b56a4f5ac6
- issue_id: WATER-001
- intended_files: scripts/t1_fft_local_store_writers.py; tests/test_t1_fft_local_store_writers.py; .github/workflows/raft-t1-fft-vulkan-roundtrip-isolation.yml; this session; T1 experiment; T1 event
- experiment_key: water001-t1-original-fft-slot0-spv-local-store-writer-census-base-13e03d8-distinct-from-42196835754-42198180194
- resource_key: t1-fft-vulkan-roundtrip-isolation-ubuntu-24.04-no-shared-unity

## Proven restart

The authenticated Vulkan-vs-Unity trace comparison 42196835754 and promoted-only 42198180194 both found 252/256 site-1 X and 64/64 site-2 coordinate mismatches; source-only integer rewrite fixed site-0 coordinates, but not butterfly coordinates. Site 1 X and site 2 X/Y require further producer provenance. The scheduled 20261106T1009Z evidence-gate CLI hardening is separate; do not touch it. Latest branch had no queued or in-progress Actions at scope time. Owner phone result 42058825739 entered, saved, reopened world; water errors remain. No device water restoration proven.

## Plan recorded before edit

Add bounded direct Function OpStore candidate census at leaf OpLoad coordinate lanes of original FFT slot-0 SPIR-V. No raw SPIR-V IDs, constants, traces, shader bytes, or values in public result. Counts are static, not proof of reaching definitions or authored Unity kernel identity. Source-free adversarial tests and one isolated original Vulkan roundtrip workflow run; no Unity build, mouse/buttons/Settings/audio changes.

## Result

Pending implementation and exact-source validation.

## Next step

Implement audit + tests, check original private workflow output, record bounded site-1 X/site-2 X/Y candidate writer outcomes, do not mutate butterfly coordinate operands without valid evidence.
