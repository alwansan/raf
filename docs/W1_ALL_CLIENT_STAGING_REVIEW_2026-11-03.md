# W1 staged Depth Copy integration and experimental XAPK review — 2026-11-03

Owner's latest explicit request authorizes an experimental XAPK incorporating available A1–A15 and W1–W3 work. This supersedes W1's earlier no-full-build scope for this preview only. It does not turn unresolved source blockers into solved ones or authorize dummy kernels, skipped authenticity checks, or a READY claim.

## Source change
Code c7513a1944c748c752a5790b440fa98767887dec adds the pinned private ShaderLab output option and exact-name single-target installer. Regeneration authenticates both original owners and the original Depth Copy object. Installer independently pins reconstructed output SHA256 0a7e11f750cac17ecc25cb7179c0a29850d6fb91fa983618f12e6bd8782ed1ea, rejects missing/duplicate targets and unsafe metadata, backs up outside the Unity project, preserves exported .meta bytes, and restores original shader bytes after a partial write. Only shader source is replaced. Export identity/path and material GUID are never invented.

The existing native workflow now invokes regeneration and installation before the original strict built-in/water gates. Until a real export passes this stage, production installation is NOT verified. Preserving an exported GUID does not itself authenticate the export's origin/completeness. The controlled pre-build staging process must not run concurrent writers within the same private project.

## Review boundaries and peer inclusion
The accompanying JSON records 52 live client-state files and 48 complete last_commit SHAs. GitHub compare verified all 48 are ancestors of c85042acb1282b5eeacc7feae25a7b9ead73caa5 (ahead, behind=0). W2's malformed descriptive last_commit is not treated as a SHA; its successful 8130cda612ffc3c6e48394264f78e5227a81e8f3 CI and live ancestor chain are separately identified. One older client uses a nonstandard client_id/state schema. This is an ancestry inventory, NOT proof that no later code superseded a change or that all experiments ship.

| Clients | Work present in branch | Delivery significance |
| --- | --- | --- |
| A1 | FFT translation/dataflow and CPU Vulkan numerics | Numerical evidence, unresolved format/Unity kernel integration |
| A2 | Settings/scaler/layout source studies | Source evidence; Android layout acceptance pending |
| A3 | Haptics source pin and ZIP/reassembly fixes | Production staging and delivery checks |
| A4 | CI/performance and diagnostic corrections | Runtime/tool changes; actual device memory unresolved |
| A5 | Haptics ZIP reader and final OBB audit | Production adapter and packaging gate |
| A6 | Save-path/link safety and shader include parsing | Production adapter/source restore safety |
| A7 | LEFT Mouse0 gesture and packet routing fixes | Runtime input changes; phone acceptance pending |
| A8 | World readiness and diagnostics/audio probes | Source audit plus diagnostic changes |
| A9 | Profile/session identity, source pins, shader restore safety | Runtime/staging changes |
| A10 | Original save-source selection and lexical extraction | Production source adaptation |
| A11 | Export inventory scope integrity | Audit tool; no shader source recovery |
| A12 | Original/vendor shader identity intersection | Audit evidence; no replacement by itself |
| A13 | Material links and export coverage | Audit evidence |
| A14 | Built-in backup write recovery | Restore-tool correction |
| A15 | Restore rollback and render lexical guard | Restore/audit correction |
| W1 | Depth Copy recovery, arithmetic/raster checks and new staging | Exact target production staging now wired; genuine export result pending |
| W2 | Global Linear, mixed sRGB/linear flags and material statistics | Original configuration evidence; no assumed new color fix |
| W3 | Full original material/texture/shader/keyword topology | Recovery input/evidence; no mass material replacement |

## Tests and unresolved results
26 local W1 tests passed, including 8 new staging/rollback cases. Original-data wrapper run41687161175 SUCCESS. Initial stage41687161400 FAILED on an authored synthetic fixture containing literal backslash-n in metadata, after successful source regeneration; this was not a shader mismatch. Fixture fixed in37268a58a56929ad355d695a795e8dde891a3d8c; rerun41687431767 COMPLETED SUCCESS on37268a58; regenerated pinned wrapper installed into synthetic export with GUID intact. Other same-code platform/preflight CI still pending when this report was prepared.

Latest A1 run41686164808 FAILED with 0 executed pairs and invalid_executor_result, not numerical differences. A concurrent peer has independently fixed canary/workload handling at9cd002eec0b3fe623d1e58a570320251a6d51176; run41687345468 pending. No peer workflow was changed or cancelled.

Known real pre-build blockers remain: prior complete export had zero built-in identity matches; authentic water/FFT source and Unity format/binding contracts are unresolved. Global Linear original settings and per-texture flags are proven input constraints, not a verified current Android rendering result. Do not remove gates to get an XAPK. No full compatibility review passed, readiness remains NOT_READY, full immutable reviews0/3. Any requested native run must be labelled an owner-authorized incomplete experimental attempt; only actual signed successful APK+OBB+XAPK output is a deliverable.

CL raft-log root identities rechecked read-only, no new phone evidence inferred. No original sources or derived HLSL/DXBC/SPIR-V published. No scheduled tasks/protected branches changed.
