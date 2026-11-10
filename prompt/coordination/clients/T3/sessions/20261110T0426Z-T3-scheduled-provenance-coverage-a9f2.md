# T3 scheduled session — 2026-11-10 04:26 UTC
session_id: 20261110T0426Z-T3-scheduled-provenance-coverage-a9f2
origin: scheduled
resumed_from: 20261110T0333Z-T3-scheduled-original-provenance-source-gate-b7q2
read_head: c26c0c8c16c5306d51a294d11a441fde5b73e161
scope_commit: f625b32d314de005883be5ca3ab51e67f5726a33
scope_file: prompt/coordination/work/RENDER-002/20261110T0426Z-T3-scheduled-provenance-coverage-a9f2.md
status: RENDER-002 OPEN; NOT_READY 0/3

## Evidence checked
Read 5 November device feedback before priority selection, AGENTS, owner requirements, STATUS and T_TEAM protocols, T3 state/memory, most recent scheduled session and validator/tests. Latest listed CI 42747722414 T1 succeeded, 42745684716 and 42745684704 succeeded; T3 synthetic regression 42728727179 succeeded. HEAD at read c26c0c8. No queued/running jobs in last 12 shown; that window is not a global guarantee. CL device links preserved from the owner report; no new pixel-level finding claimed.

## Actual work
Reviewed source of scripts/t3_smoke34_location_provenance_gate.py and all 14 tests. Verified the tool intentionally cannot authenticate provenance: a well-shaped arbitrary mapping can pass STRUCTURAL_INJECTION_ONLY. Rather than duplicate CI or change source blindly, published exact private def/use evidence contract at f625b32d. This cycle produced a reproducible acceptance boundary but no new original source extraction, shader change, or device repair. Previous same-export bounded material UV/RGBA parity remains valid only for its original 41-material scope.

## Resume
Implement an isolated SHA-pinned private smoke34 DXBC def/use tracing experiment against authenticated ZIP2 source and matched SPIR-V. Fail closed for optimization ambiguity; publish only counts and hashes. Compare original render-state/material alpha after evidence, then test against owner CL screenshots. Do not alter T4 mouse or T5 resolution scopes. No Actions started or cancelled.
