# B24 — Original world callback managed-compilation parity (2026-11-04)

## Gap and safe change

The active Unity native workflow instruments each original in `config/runtime-operation-traces.json`, including `GameManager.OnWorldRecieved`. The existing no-LFS original managed candidate selected only the offline adapter's `PINS` list; its trace manifest additionally names `GameManager` but its actual original C# was omitted. This could allow an instrumented GameManager compile regression to pass the cheap preflight. The B07 standalone callback probe is necessary lexical evidence but not a full managed-assembly compilation.

B24 commit [5cfd0544af9808dbd0326a7394a99283846d7ed4](https://github.com/alwansan/raf/commit/5cfd0544af9808dbd0326a7394a99283846d7ed4) includes **SHA-pinned, fail-closed selection of trace-only original C#** before the late write/install stage, plus final original-digest validation and a targeted six-case negative-control suite. It changes only the private candidate preflight behavior; native gameplay source, original assets/GUIDs, sound, Settings and touch code are untouched.

## Evidence

- [B24 synthetic run 41916497807](https://github.com/alwansan/raf/actions/runs/41916497807): SUCCESS, **6/6** cases (source mismatch, duplicate, post-selection mutation, unregistered trace, SDK homonym and metadata integrity).
- [Existing original managed integration 41916497902](https://github.com/alwansan/raf/actions/runs/41916497902): SUCCESS at the exact commit, including ILSpy source recovery, local RPC harness and complete adapted original C# compilation. The configured original `GameManager` hash is `8eb76bcf22028ace2394afe96051ae1e3e59e44f8243c2a68d6b163d80802306` from the authenticated original B07 trace manifest.

## Not yet established

This is original managed **source/compile** evidence only, not Unity Editor/IL2CPP or on-device runtime execution. The last published Raft APK86 predates the change; its `SteamUserStats.StoreStats` failure and invalid FFT passes/kernelCount0 remain separate open blockers. Do not set `WorldHasBeenRecieved` artificially or mark LOCAL-005 closed. The next actual native candidate requires real device create → save .rgd → reload observation.
