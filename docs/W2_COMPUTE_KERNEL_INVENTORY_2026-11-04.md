# W2 compute-kernel inventory — all 9 original ComputeShader providers, 42 kernels — 4 November 2026

Client W2 `raft-20261103T152008Z-92502b76`. Direct continuation of the
WATER-001 lane: W4's compute-provider note left kernel identity open —
*"serialized kernel tables read as zero ...; kernel identity must come
from the compiled program records"*. Direct typetree inspection proves the
host-side dispatch inventory is recoverable CPU-only from the serialized
`variants[].kernels` rows, without touching any compiled blob
(`scripts/probe_w2_compute_kernel_inventory.py`, 8/8 fail-closed tests,
workflow `.github/workflows/raft-w2-compute-kernel-inventory.yml`; three
owners identity-verified against committed objects).

## The complete recoverable dispatch inventory (42 kernels / 9 providers)

| provider (owner) | kernels | distinct names | serialized CBs | notes |
|---|---:|---:|---:|---|
| `DX11 FFT` (sharedassets0 @ pathID 2456) | **20** | 1 (`Butterfly`) | **0** | the FFT gate's dispatcher: one kernel name, 20 serialized kernel rows (indices matter for Dispatch), no serialized CB |
| `Blurs` (resources @ 905) | 12 | 4 (`BlurSSSX`, `BlurSSSY`, `BlurX`, `BlurY`) | 1 | the SSS/blur replication bundle W4 flagged |
| `RenderTextureToBuffer` (905) | 1 | 1 (`Full`) | 1 | |
| `Gauss` (905) | 2 | 2 (`Gaussian_Horizontal`, `Gaussian_Vertical`) | 1 | |
| `Ripples - Simulation` (905) | 1 | 1 (`Simulation`) | 1 | |
| `Ripples - Transfer` (905) | 2 | 2 (`HorizontalTransfer`, `VerticalTransfer`) | 1 | |
| `Ripples - Setup` (905) | 2 | 2 (`MultiSetup`, `Setup`) | 2 | only provider with 2 serialized CBs |
| `EyeHistogram` (905) | 1 | 1 (`KEyeHistogram`) | 1 | |
| `ConvertDepthToArray` (sharedassets29 @ 577) | 1 | 1 (`CSMain`) | 1 | |

Every kernel row resolves with exactly one variantMap entry and **zero**
global/local keywords — nothing keyword-flagged, so a restored host can
bind every dispatch by name alone (no variant permutations needed).

## Why this completes part of FFT-FORMAT-009 (bounded)

- The host-dispatch surface (which names, how many kernels, which
  provider) is now fully mapped from original data: any rebuilt
  `Shader.Find`/`FindKernel` sequence in a port can be verified against
  this table before a device run — e.g. the water gate's FFT chain
  (`DX11 FFT` with 20 `Butterfly` rows and its serialized-CB-0 shape) and
  SSS/blur replication (`Blurs` 4 names × 3 counts) become concrete.
- Still out of W2 scope (per doctrine): the compiled DXBC program
  contents and per-thread group sizes — blob parsing stays with the
  device/native lanes (A12/W1/W5).

## Boundaries

- Names and counters only; no payload bytes, path IDs, or keyword strings.
- No engagement with running lanes (W5 Blur rebinding, W4 trial build
  41812889049); no Unity/APK; `.meta`/GUID/CL untouched.
- WATER-001 / RENDER-002 / FFT-FORMAT-009 remain OPEN; NOT_READY;
  reviews 0/3.
