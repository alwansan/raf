# Original Blur partial constant-buffer member handoff — 2026-11-04

Client: raft-20261103T103610Z-4e91b2cd. Issue WATER-001 / RENDER-002, independent CPU-only follow-up to A12R structural reflection.

## Authenticated result

[Run 41742032440](https://github.com/alwansan/raf/actions/runs/41742032440), attempt 1, job 126285649840 **SUCCESS** at source [7bbc443c](https://github.com/alwansan/raf/commit/7bbc443c02b5a0169072ea67f773af06537af72b). Four local and CI test methods pass, including ambiguous bindings, invalid dimension/index/array, observed overlap and out-of-allocation negative controls. The workflow reassembled and SHA-verified the same 14 original owners (488,439,356 bytes) from immutable ZIP2 15964ea8f246b6e076ce26b60931ee2e1a9a2385, without LFS or Unity. Object SHA256 c9341848367eaedb12e551ce9061b1eea728f54f2069ef1a3c12c4a4a2e9bb52.

**New source fact:** all six original CB records explicitly have m_IsPartialCB=true. Seven serialized member records are present: four matrices and three vectors; array-size fields are all zero, numeric type fields all zero, no structs. Do not infer element types from the numeric type code alone.

| Original stage | Slot | Allocation bytes | DXBC declared bytes | Serialized member indices / dimensions | Candidate end bytes |
| --- | --- | --- | --- | --- | --- |
| Pass 0 vertex | 0 | 176 | 64 | matrix 0 / 4 | 64 |
| Pass 0 vertex | 1 | 368 | 336 | matrix 272 / 4 | 336 |
| Pass 0 fragment | 0 | 80 | 64 | vectors 32 / 1; 48 / 3 | 36; 60 |
| Pass 1 vertex | 0 | 176 | 64 | matrix 0 / 4 | 64 |
| Pass 1 vertex | 1 | 368 | 336 | matrix 272 / 4 | 336 |
| Pass 1 fragment | 0 | 80 | 80 | vector 64 / 2 | 72 |

The candidate calculation interprets index as a byte offset, vector dimension as four-byte lanes, matrix dimension as sixteen-byte rows, zero array count as one non-array element. Under that **unverified interpretation**, all seven member ends fit both original allocation and compiled declaration, and no adjacent member spans overlap. The numeric observations and partial flags are source facts; that interpretation and binding semantics are not yet proved. Metadata is partial, so unused/trailing allocation cannot be silently cut or treated as absent uniforms. No original names, HLSL, bytecode, game assets or .meta/GUID modifications were published.

## Deliverables and exact next step

- scripts/probe_original_blur_member_layout.py observes original numeric member records and compiled spans, without changing A12/W1 recovery implementations.
- tests/test_original_blur_member_layout.py; isolated 15-minute CPU workflow raft-blur-zip2-4e91.yml, cancel-in-progress:false, own report/artifact.
- [Aggregate artifact13282585907](https://github.com/alwansan/raf/actions/runs/41742032440/artifacts/13282585907), 667-byte archive, SHA256 e1a5a4f6e9f5dd4cf58d3243244054d67b35762a1e07724e68aedd2e585dadd5. Artifact archive hash is not an original-source fingerprint.
- Read together with [A12R reflection](A12R_ZIP2_ORIGINAL_BLUR_CB_DXBC_2026-11-04.md).

Next correlate actual DXBC constant-buffer operand register indices/component masks and translator SPIR-V/HLSL offsets with these private named members. Explicitly account for partial metadata and engine buffers before rebuilding named uniforms or ShaderLab. Do not re-run this observation unchanged.

This closes the member-observation experiment only. No HLSL rewrite, ShaderLab installation, GPU/Unity/Android proof, full-water/FFT/material-color fix or readiness claim. WATER/RENDER/FFT remain open, NOT_READY/0-of-3. Unrelated owner full native run41741108965 was already in progress when inspected; it was neither changed nor duplicated. Protected branches, request JSONs, scheduled tasks and existing Raft tree remain untouched.
