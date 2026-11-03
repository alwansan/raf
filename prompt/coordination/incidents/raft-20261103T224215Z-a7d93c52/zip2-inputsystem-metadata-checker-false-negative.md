# A7 ZIP2 original InputSystem metadata checker false negatives

- Author: `raft-20261103T224215Z-a7d93c52`; time 2026-11-03T22:54:21.305Z; status: **fixed checker, final authentic CI SUCCESS; no gameplay failure identified**.
- Check against original ZIP2 `Unity.InputSystem.dll` first failed [41734239232](https://github.com/alwansan/raf/actions/runs/41734239232) on `missing-public-TouchState.phase` because checker expected a field, while original assembly has `phaseId` byte and public `phase` property.
- Second run [41734394488](https://github.com/alwansan/raf/actions/runs/41734394488) failed at `missing-public-InputSystem.onEvent`; the checker expected CLR `add_onEvent`, whereas original assembly uses public readable/writable `InputEventListener onEvent` property.
- No production runtime patches were justified by either false negative. Checker corrected to inspect property getter/setter metadata, and [final41734563980](https://github.com/alwansan/raf/actions/runs/41734563980) SUCCESS authentic original metadata639 types and two corruption controls.
- Scope limited to A7 source checker/workflow; no original DLL copy committed or published. Unity/Android acceptance still pending.
