# DIAG-010 — shutdown write / wake dispose race potential

Client: raft-20261103T105250Z-12695739; observed in source review 2026-11-03T10:58:40.653Z. Status: **SOURCE_FIX_VALIDATED; device acceptance unknown**.

## Mechanism

The previous `PersistentDiagnosticLog.Write` read `stopping` before `pending.Enqueue` and `wake.Set` without synchronizing with `Dispose`, which set stopping and disposed the `AutoResetEvent`. A concurrent logging callback could pass the check, then invoke `Set` after disposal, potentially throwing `ObjectDisposedException`. No evidence in APK80 confirms this race actually occurred, and the fix is not in that binary.

## Repair and validation

[Source e70dd94d](https://github.com/alwansan/raf/commit/e70dd94d9ea0309718f523352edb24299960c15d) serializes the stop check and event signal with the disposal transition. Added actual C# stress tests; [run41623238332](https://github.com/alwansan/raf/actions/runs/41623238332) succeeded with 256 checks. Same-source platform and original managed integration runs succeeded; [3d30429e](https://github.com/alwansan/raf/commit/3d30429e52a67869b79adf0c5669f3aaa36c33fb) removed duplicate platform execution because a dedicated logger workflow already existed.

## Limit

No Android instrumentation/new APK, no phone proof and no graphical or gameplay readiness claim. Do not close project-wide PERF-007/LOCAL-005/WATER-001/RENDER-002 based on this narrow repair.
