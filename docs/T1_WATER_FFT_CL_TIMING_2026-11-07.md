# T1 WATER-001 — CL timestamp correlation (2026-11-07)

Source: owner phone report `docs/DEVICE_FEEDBACK_42058825739_AR.md`; pinned CL tree `520c4cf409aa20a4db54ff80ed87d8807d9cba57`, files `raft log/lf/LogRaft-20261105-{220911-559,230108-327}/session-summary.json`. These are LogRaft category counts, not independent per-kernel trace samples.

| session | first invalid water pass (ms) | first invalid FFT kernel (ms) | FFT - pass onset | final invalid pass | final invalid FFT kernel | end-time delta (FFT - pass) |
|---|---:|---:|---:|---:|---:|---:|
| 220911-559 | 1793905782604 | 1793905782606 | +2 ms | 23884 | 3850 | -3 ms (1793905980413 - 1793905980416) |
| 230108-327 | 1793908926108 | 1793908926110 | +2 ms | 39132 | 6026 | -5 ms (1793909270700 - 1793909270705) |

Both categories start within **2 ms** in both sessions and continue to near session stop. This establishes **temporal co-occurrence only**; it does not identify the first faulty program, prove a causal relationship, or show a Vulkan-vs-Unity numerical divergence. The two sessions have different durations and cannot be compared by raw counts alone.

LogRaft's last performance sample undercounts the final grouped totals: 220911 pass 23608→23884 (+276), FFT 3804→3850 (+46); 230108 pass 38880→39132 (+252), FFT 5984→6026 (+42). Use final error groups for session totals; use first/last timestamps for onset. LogRaft warns OS ring-buffer losses are not fully detectable. Avoid treating these totals as exact GPU dispatch counts.

Next decisive test: extract **first distinct** raw Unity message for each category, its program/material/kernel name and frame context; join to the original compute resource and authenticated `.compute` mapping. Then run a source-pinned Unity `FindKernel` / `GetKernelThreadGroupSizes` / `SetTexture/SetBuffer` / `Dispatch` probe, and only compare Vulkan/Unity numeric traces when fixture, input, invocation and read-site provenance match. Preserve raw game assets and CL logs read-only; no phone/Unity execution claimed here.
