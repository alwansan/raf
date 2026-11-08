# T1 / WATER-001 — original LogRaft first raw water/FFT context (source-pinned)

**Scope:** owner-collected phone **raw Logcat** and a separate **collector summary**. Neither is Unity shader source, a GPU dispatch trace, a causal attribution or proof of restored water. **WATER-001 OPEN; full game NOT_READY 0/3.**

**Owner session:** `LogRaft-20261108-164850-270` targeting `com.alwansan.raft.androidtest` on POCO F5 Pro, Android 15. **CL read-only commit:** `61f71ceb3b9e6f16c8fb300656f6e6baf32b33e8`. **First Logcat segment:** `raft-20261108-164850-270-00001.log.txt`, **33,549,006 bytes**, exact Git **blob SHA1** `bf5db2607e3b46165d39142aa28f6596ed0715d4`. **Full collector summary SHA256:** `941d37d4b18a2bf11471098bd0668029add11913d76b0a97086dd9fb185e7ff7`. Do not interchange the SHA1 Git object digest and SHA256 of JSON.

## First times: independent data paths, no invented clock synchronization

| Source and observation | Unix milliseconds | Baghdad UTC+03 |
| --- | ---: | --- |
| First **Spectrum classified invalid-pass** line in original raw Logcat first segment | **1794145757552** | **16:49:17.552** |
| First other **water invalid-pass** raw line (material identity not proved by fallback classifier) | **1794145757609** | **16:49:17.609** |
| **Collector's** first water invalid-pass recorded in full-session summary | **1794145757579** | **16:49:17.579** |
| **Collector's** first invalid compute-kernel-index6 recorded in full-session summary (**not located in first raw segment**) | **1794145757581** | **16:49:17.581** |
| First world-loaded message recorded in same collector summary | **1794145822065** | **16:50:22.065** |

The raw first water timestamp is **27 ms earlier** than the collector's first-observed water message and **64,513 ms before** the world-loaded milestone (which is itself from the collector). The previously published collector-only differences remain **64,486 ms** for first water and **64,484 ms** for first invalid kernel before world-loaded. A strict exact timestamp equality would be false; this analysis preserves both clocks and permits only a **±250 ms correlation gate**, recording the 27 ms difference and declaring exact same-event/clock alignment **NOT_PROVEN**. Correlation does not mean identity.

## First 33.5 MB lexical observations (not the entire 206 MB session)

- 332,507 source lines with year/date `2026-11-08`, high-precision fractional seconds, and no parsed canonical Android threadtime PID/TID fields. Do not infer thread ownership or a C# stack chain from adjacent lines.
- **4,048** lines classified by the existing conservative water-root script as `pass_spectrum`; **8,096** as `pass_other_water`. The latter label must **not** be silently renamed to FoamGlobal without matching its actual raw token. Raw first-segment classified count is 12,144, **not** all 74,359 session water errors.
- **2,024** lines contain literal `Dx11FFT`, but that count is **only string token presence**, not confirmed dispatch calls, unique stack traces, original kernel owner or unique errors.
- **No literal `kernel` token nor a parser-recognized `kernel_index_6` root was found in this first raw segment**. That is a deliberately narrow **segment/source-format** observation. The authenticated full-session collector separately records **11,165** invalid compute kernel-index6 errors. Do **not** conclude the kernel errors did not happen, nor infer that all 2,024 `Dx11FFT` token lines caused them.
- **No literal `ComputeShader` token** was located in this first segment. Thus there is no corroborated raw `ComputeShader.Dispatch` or `ComputeShader.FindKernel` callsite in this lexical scan. Actual original in-game return values and bindings remain absent.
- Timestamp precision in the original LogRaft raw export exceeds 3 decimal digits; the first draft rejected them. Fixed ISO-date parsing truncates to integer milliseconds without rounding and refuses overlong fractions. Earlier red CI runs reflected test/parser flaws, not Android GPU testing failures.

## Verifier, falsification, privacy

`scripts/t1_water_first_raw_context.py` authenticates the entire original first-segment Git blob (Git header + bytes), enforces exact bounded size and no symlink/FIFO, checks the source-pinned JSON SHA256, and emits only fixed category names, booleans, numeric aggregate counts and redacted time provenance. It never prints proprietary log lines, source paths inside the logs, original shader/compute code or stack text. Same-PID/TID adjacency is not emitted as a fact where threadtime parsing is unavailable. Input files live only in GitHub runner TEMP and are deleted; no artifact is uploaded. `tests/test_t1_water_first_raw_context.py` includes synthetic wrong SHA/size, symlink/FIFO, malformed oversized lines, cross-thread false-context rejection, duplicate confidence checks, ISO-date precision/truncation and timestamp correlation controls. Workflow `.github/workflows/raft-t1-water-first-raw-context.yml` stays separate from T5 APK/OBB/XAPK.

The source is validated **only as far as real CI executed**. The final Actions run and test counts should be recorded in T1 session and experiment after the current source+workflow gate terminates. Never replace a failing gate with a fabricated root or arbitrary +27ms offset inserted into raw data.

## Next discriminating engineering step

Only a runtime trace tied to the **same authenticated Raft game build and actual original Unity Shader/GUID** can map an invalid integer index 6 to a kernel name:

1. Capture the actual original FFT caller and ComputeShader GUID/source fingerprints while retaining original private game bytes and GUID/meta unchanged. The C# trace must distinguish failed `HasKernel(name)/FindKernel(name)` from subsequent `SetTexture`, `SetBuffer`, and `Dispatch(index,x,y,z)` failures.
2. Record original callsite identity, returned index and kernel group sizes **at the first failed call**, then compare with source-authenticated original serialized compiled candidates. Numeric index 6 is **not** automatically `compiled_slot=6`.
3. Compare same-fixture input/output hashes, first divergent FFT stage and true Unity/Adreno image result only after original identity is validated. T2 independently examines original Spectrum/Foam Material→ShaderLab pass indices.

**Current mini APK:** one shared T1–T5 Actions Artifact ZIP [42509945996](https://github.com/alwansan/raf/actions/runs/42509945996) exists; T1 latest shared round r2 **NO_BUILD**. These are read-only evidence tools, not a reason to restart a Mini build or the game XAPK.
