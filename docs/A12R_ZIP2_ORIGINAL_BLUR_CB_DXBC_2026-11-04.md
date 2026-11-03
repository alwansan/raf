# A12R — authenticated original Subsurface Blur constant-buffer reconstruction (ZIP2)

**Issue:** WATER-001; independent agent `raft-20261103T190657Z-9004f68d`, session `a12r-zip2-20261103T224242860Z-c7e6a9e8`; resumed from paused A12 without modifying the old session. Read-only ZIP2 pinned at `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.

## Restored original source

[SHA-pinned selected-file restorer e8f7be47](https://github.com/alwansan/raf/commit/e8f7be47233bed754735997df69ce67f2c45189b) restores **14 authentic original Shader-bearing serialized sources**, **488,439,356 bytes** in total, by reassembling exact ordered split parts in private CI temp and verifying each file SHA256 against original pin. [Isolated ZIP2 workflow 50aedc8b](https://github.com/alwansan/raf/commit/50aedc8b00506232b653d63902488ba2b31114fd) fetches the immutable source directly, does NOT pull Git LFS, and leaves protected branches, original .meta/GUIDs and game tree unchanged.

## Four original compiled stages

Original Shader `UltimateWater/Utilities/Blur (Subsurface Scattering)` object SHA256 `c9341848367eaedb12e551ce9061b1eea728f54f2069ef1a3c12c4a4a2e9bb52`. Its 2 passes/4 linked original vertex+fragment DXBC programs have **no RDEF** chunks. Bytecode is private; public report has only scalar counts, SHA commitments and numeric sizes. Authenticated serialized parameter-group names/sizes/slots agree privately with the original `m_ConstantBuffers` and `m_ConstantBufferBindings` in all 4 stages (6 total buffer bindings). Genuine original DXBC SHDR/SHEX `dcl_constantbuffer` declarations were decoded independently with [the 9-case parser 1bd5dec7](https://github.com/alwansan/raf/commit/1bd5dec74dd50295d17013f65fae30e086929dba).

| Pass/stage | Unity CB allocation per numeric slot (bytes) | Original compiled DXBC declared span (bytes) | Slots exact / compiled within allocation |
| --- | --- | --- | --- |
| Pass 0 vertex | 0=176; 1=368 | 0=64; 1=336 | Yes / Yes |
| Pass 0 fragment | 0=80 | 0=64 | Yes / Yes |
| Pass 1 vertex | 0=176; 1=368 | 0=64; 1=336 | Yes / Yes |
| Pass 1 fragment | 0=80 | 0=80 | Yes / Yes |

Original Unity CB definitions include **2 matrix member records in each vertex** and fragment CBs include **2 vector records in pass0** versus **1 in pass1**; one serialized texture parameter per fragment stage. These are genuine nonempty CB metadata despite zero numeric records in a different serialized parameter blob layout; they must never be silently dropped.

## CI proof and limits

Latest [CI 41736229248](https://github.com/alwansan/raf/actions/runs/41736229248) at [source d8162ba3](https://github.com/alwansan/raf/commit/d8162ba37c3ffb022c29dc57531683c7ac2b23f7) **COMPLETED SUCCESS** (job 126266034663): 18 CB/schema/metadata, 8 ZIP2 source and 9 DXBC opcode synthetic cases, **35/35**; 14/14 original owner SHA256 checks. All four compiled stages have identical register slot sets to Unity, with declared spans within original allocations, but **only one stage has byte-for-byte size equality of all CB declarations**. Numeric aggregate only: [artifact13278603109](https://github.com/alwansan/raf/actions/runs/41736229248/artifacts/13278603109). Earlier [CI41735231510](https://github.com/alwansan/raf/actions/runs/41735231510) independently showed all six private serialized name-size-slot matches, while [CI41735762982](https://github.com/alwansan/raf/actions/runs/41735762982) decoded all DXBC CB declaration lists.

Bounded compiled declarations **may** result from partial register use, but this is not proved, and not proof of parameter value/layout equivalence, actual HLSL or Vulkan reflection, material GUID mapping, ShaderLab construction/installation, GPU rendering, Unity build or Android test. No Unity/APK/OBB/XAPK workflow, Release or native request was started. No source shaders or private names were published.

**Next source engineering:** validate matrix/vector member offsets/types/arrays against original compiled bytecode and translator HLSL, reproduce exact resource+sampler bindings, then build a private original source-faithful ShaderLab wrapper and validate Vulkan with GUIDs preserved. WATER-001, RENDER-002 and FFT-FORMAT-009 remain OPEN, game NOT_READY and 0/3 complete candidate-SHA audits. Do not bypass genuine shader/kernel gates merely for a native build.
