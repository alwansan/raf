# T1 — original-authenticated FFT-derived ComputeShader import under licensed GameCI Unity 2021

Date: 2026-11-05, owner T1, issue WATER-001 OPEN, readiness NOT_READY 0/3. This report belongs to isolated session `20261105T104500Z-T1-private-gameci-import` and deliberately does not claim any original author's Unity runtime kernel IDs or Android water fidelity.

## Why this is different from earlier failed Unity runs

T1 previously produced **20/20 original SHA-verified DXBC→SPIR-V→HLSL50→SPIR-V** private single-kernel Unity `.compute` candidates at [CI41957549770](https://github.com/alwansan/raf/actions/runs/41957549770), but the direct `unityci/editor:ubuntu-2021.3.45f2-base-3` manual-license Docker invocation failed even on a source-free project [CI41959712898](https://github.com/alwansan/raf/actions/runs/41959712898).

A distinct official `game-ci/unity-test-runner@v4` path successfully activated the same Unity 2021.3.45f2 version and ran one public NUnit EditMode test [CI42010878771](https://github.com/alwansan/raf/actions/runs/42010878771). After adding a synthetic author-written `.compute` canary, [CI42011720822](https://github.com/alwansan/raf/actions/runs/42011720822) **SUCCESS** with **2/2 EditMode tests** and real Editor `AssetDatabase.LoadAssetAtPath<ComputeShader>`, `SystemInfo.supportsComputeShaders=true`, `HasKernel`, `FindKernel`, and `GetKernelThreadGroupSizes=(64,1,1)`. Those do **not** execute original shader bytes.

This source-free success identifies a valid licensing/Unity test execution route, but the GameCI Action prints Unity's raw Editor output into public Actions logs, so **it must never run on proprietary reconstructed HLSL**. A private capture boundary is essential.

## New private-execution implementation

- `scripts/t1_gameci_private_result_gate.py` parses only bounded NUnit `test-run` attributes and exact expected test-case identities; it refuses wrong names, nonzero exit, skipped/failed cases, malformed XML and missing reports. Never prints the XML body, private log, shader text, private compiler messages or original identifiers.
- `tests/test_t1_gameci_private_result_gate.py` has eight adversarial source-free groups, including false-positive pass rejection and redaction of private test failure messages.
- `android-port/Experiments/T1/T1PrivateFftImportTests.cs` is **only staged privately** under a temporary Unity `Assets/Tests/Editor` folder, not in the playable game. It reauthenticates the candidate source hashes and serialized original FFT object SHA, demands twenty unique source-compiled slots, requests actual Editor ComputeShader imports, each candidate's generated `main` via `HasKernel` and `FindKernel`, and original slot-local workgroup sizes. NUnit passes only if every one of twenty does. A generated `main` is an import handle, not the author runtime kernel name/variant selector.
- `.github/workflows/raft-t1-private-gameci-original-fft-import.yml` pins the **actual proven GameCI CLI v0.1.72** from official release SHA256 `1de550a620ee92e05e920b6db7d431621440b60b2577f04b4a997dc92a58cb0a`; it invokes the same Unity 2021.3.45f2 `unityci/editor` Linux IL2CPP image as positive synthetic CI via direct CLI. Every CLI call redirects stdout/stderr into disposable runner-private logs that are never printed/artifacted. First runs original-free source canary under that exact pinned CLI and validates only numeric XML counts. **Only if the synthetic gate passes** does it recover immutable ZIP2 original owner SHA, transform authentic compiled programs privately and invoke Unity on the twenty candidates.
- The workflow shares `raft-native-engine-${{ github.ref }}` concurrency, `cancel-in-progress:false`, 60-minute budget, read-only GitHub permissions, SHA-proven download, no native game build request, no modifications to owner working audio/Settings/touch, no artifacts/release, and `if: always()` cleanup of shader/Unity logs and original asset directories.

## Actual execution and acceptance interpretation

[CI42013637262](https://github.com/alwansan/raf/actions/runs/42013637262) is in progress at this initial checkpoint; it successfully completed private NUnit controls, and CLI SHA verification before the source-free CLI test. Do **not** treat this as an import PASS until the actual original stage completes and the XML gate reports `original_derived_twenty_compute_import_groups_verified=true`.

Even if all 20 generated candidates import, that would prove **original-compiled-data-derived rewritten shaders can load individually under Editor** (and only their declared groups), NOT that the original authored multi-variant `.compute` was recovered, original Unity `FindKernel` index maps to a compiled slot, image resource names and CB uploads match the original game, water/wave pixels match, or Qualcomm Adreno can execute it. Those blockers remain. WAVES and Foam ShaderLab restoration handled with T2/T3 and integration/device planning T5.

Next: inspect source-free quiet GameCI gate and actual private twenty-candidate import results, fix precisely observed errors without disclosing shader source, record new evidence and coordinate true integration with T5; keep WATER-001 OPEN until actual game/phone evidence.
