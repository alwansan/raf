# Owner correction, permanent resume and recovery helper — 3 November 2026

Read [current owner requirements](CURRENT_OWNER_REQUIREMENTS.md), `AGENTS.md` and [prompt/STATUS.md](../prompt/STATUS.md) first. They supersede older contradictory instructions.

## Reviewed evidence

Read the supplied `الجلسة2.txt` completely: its final checkpoint is source`f4df907d3c017810cf758a5e280ad68ea54a2e1b`, matching live GitHub before this work. `الجلسة1.txt` was not available to the session and has not been read. Reviewed the current DirectX handoff, relevant latest device/FFT findings, source/CI workflows and current touch code. Original source probe41545664983 succeeded. No Unity/APK was started by this session.

Original evidence and open graphics/audio/world limits remain in [the DirectX handoff](WORK_SESSION_HANDOFF_2026-11-03_DIRECTX_TO_WORK.md) and [FFT inventory report](ORIGINAL_WATER_LFS_COMPUTE_INVENTORY_2026-11-03.md). Do not replace original field/index dataflow with guessed math or equate translated shader validation with phone correctness.

## Owner's correction: LEFT touch

The earlier request for right-click was a wording mistake. Current touch outside interactive UI synthesizes **left mouse / Mouse0**, retains one-update short-click pulses and500ms held drag until release/cancel/pause/focus loss. Original UGUI and controller/editor surfaces retain touch ownership; physical right mouse remains physical input.

Renamed authored identifiers and files: `AndroidRightTouchPointer`→`AndroidTouchPointer`, `RightTouchGesture`→`TouchPointerGesture`, `RightTouchButtons`→`TouchPointerButtons`, with neutral command names and test directory `Tests/TouchPointer`. Updated runtime bootstrap, original MyInput alias, candidate source staging, full-workflow source list and cheap-CI triggers. **No full-workflow dispatch or request JSON change.** Original assets and GUIDs unchanged; these authored runtime types are dynamically added, not original serialized game types.

`Input.simulateMouseWithTouches` remainsfalse in original startup and authored pointer: enabling it would create automatic left-click duplication in addition to the explicit pointer and interfere with controller touches. The explicit left path is covered by source assertions and an actual-method C# harness verifying left button output, Mouse0 merging, untouched physical right/other keys, release and absent-device behavior. Pure gesture/pulse timing tests remain. Actual InputSystem/Unity/phone behavior is still unverified.

Older historical RIGHT/Mouse1 descriptions in the prior append-only history are labelled superseded at each affected document's top; they describe previous code/commits and must not be followed as current requirements. Historical CI results are not rewritten as tests of this correction.

## Permanent session transfer

The owner no longer needs to request a handoff message each time. `prompt/CONTINUE_RAFT_AR.md` is the stable ready-to-copy message; `prompt/STATUS.md` links the current evidence and next step; `prompt/README.md` explains their use. `AGENTS.md` requires future sessions and repair tasks to update these after meaningful results and before ending a session.

## Additional scheduled work

The latest owner message authorizes **one additional recovery/research automation** without Unity/APK production. Keep the existing hourly task unchanged. The extra task must perform independent bounded source/resource fixes and CPU-only experiments, avoid duplicate concurrent work, inspect HEAD and use expected-SHA writes, preserve branch/source constraints, and update the permanent prompt/status. Its actual creation result and schedule will be recorded after the scheduler confirms success. A recurring task runs in scheduled cycles; it is not continuous execution between runs.

## Validation

At preparation:14 touch policy,8 offline startup and11 render/audio/source checks passed locally. Additional mapping/gesture C# execution and original managed compatibility compile pending automatic cheap CI. Build hold remains active. Follow results and update this handoff and prompt/STATUS.md; do not ask for a fresh APK test to proceed with independent engineering.


## Confirmed left-input CI and scheduler result

Correction source [6aafa9f4](https://github.com/alwansan/raf/commit/6aafa9f4594954710281e52a48a3a93e6c11895b): [platform41548465582](https://github.com/alwansan/raf/actions/runs/41548465582), [actual original Android source41548465622](https://github.com/alwansan/raf/actions/runs/41548465622), [preflight41548465581](https://github.com/alwansan/raf/actions/runs/41548465581) and runner41548465563 all COMPLETED SUCCESS. Executed22 gesture/pulse checks and53 extracted actual-method mapping checks: syntheticButton=left, legacyKey=Mouse0, physical devices preserved. The mapping harness uses strict doubles; original-source compilation adds real managed API compatibility, neither executes a Unity input loop or proves phone interaction.

Scheduler confirmed creation/enabled state of **Raft — استعادة الموارد والتجارب**, hourly at minute40, timezoneAsia/Baghdad. This is the one additional owner-requested task; the original task and its minute10 schedule/prompt/status were not changed. New task reads permanent prompts/current requirements each cycle, performs independent resource/source fixes/CPU experiments, coordinates leases and avoids duplicate work, never builds Unity/APK, and updates the checkpoint. No guarantee of activity between scheduled runs.

## Original FFT seed dataflow — source-proven local result, remote CI pending

The earlier scanner searched only inside Dx11FFT and could not find an assignment to its selector seed. The genuine SHA-verified GpuFFT base source contains the matching protected int field, initialized in its constructor as **truncate(log(r)/log(2))** via original Mathf floating-point arithmetic. The original derived constructor forwards its second argument (int size) unchanged into the base constructor's first int. This is original source dataflow, not replacing the seed with a guessed exponent.

New `scripts/probe_original_fft_inherited_seed.py` verifies original Dx11FFT SHA8aa32937... plus GpuFFT SHA2f866cbe58836da8260461fe6406793f35d868eba94e816e593209544b4ba704, exact protected-field hash, inheritance, constructor forwarding, unique original logarithm assignment, no extra writes and existing fourth-bool +10 branch. Five corruption/visibility/guard/forwarding/privacy tests pass. Local run on the previously decrypted manifest-verified original CSharp9 files passed. Existing original-source CI now reruns this using fresh ILSpy output from the original managed DLL, without LFS/Unity or proprietary-source publication.

Algebraic examples n5..9 map to pairs0/1..8/9 and10/11..18/19. These examples do not prove actual runtime resolutions, Mathf float rounding, Unity kernel-index interpretation, GPU limits, image formats/bindings or numerical equivalence. Strict water gate remains blocked and all game/shader assets are unchanged. Next record remote CI, then correlate source-derived selectors with typed compute resource semantics and validate original output behaviour before authoring a restoration candidate.


## Final verified inherited-seed CI — 3 November 2026

Source [2074cc1a](https://github.com/alwansan/raf/commit/2074cc1ae454cd107553d5612e5e6556286ac1d3), [original-source CI41548942077](https://github.com/alwansan/raf/actions/runs/41548942077), job125631346478: **COMPLETED SUCCESS**. Fresh ILSpy CSharp9 recovery of the original managed DLL passed all existing caller/selector tests and five new inherited-seed tests. The genuine original source report confirms `inherited_seed_dataflow_verified=true` and unchanged int constructor forwarding, with original GpuFFT SHA2562f866cbe58836da8260461fe6406793f35d868eba94e816e593209544b4ba704. No LFS, Unity or device execution, shader mutation or raw source publication. This supersedes pending-status statements above for this probe only. Runtime kernel lookup, actual dimensions/Mathf rounding and resource/numerical behaviour remain unverified; the strict water gate remains blocked.

The left-click correction's four CI lanes are green, including22 gesture tests and53 actual-method mapping checks. The new hourly minute40 task is enabled; original task preserved. Permanent copy-ready message: [prompt/CONTINUE_RAFT_AR.md](../prompt/CONTINUE_RAFT_AR.md); current state: [prompt/STATUS.md](../prompt/STATUS.md). CL/img,lf,logfox root hashes match previous reviewed evidence. Published APK80 remains the older11-asset release; no new native request, build or release was produced. `الجلسة1.txt` was unavailable; only `الجلسة2.txt` was read, not inferred contents of the missing file.


## Continued recovery: compiled FFT register/image dataflow (local proof; fresh CI pending)

Owner explicitly says to ignore unavailable session1/text attachments and continue, reiterates LFS authorization and points to six original game archive parts. No dependency on the unavailable attachments remains. Found six archive identities named Raft-SteamRIP.com.zip.001..006 (five524288000-byte parts and one15257605-byte part); these are identified files, not yet inspected content or recovered shader source.

Added `scripts/probe_original_fft_resource_bindings.py` and seven executable synthetic corruption/privacy/dataflow tests. Locally correlated the previously SHA-manifest-verified original FFT typed metadata with exact original Dx11FFT CSharp9 SHA. All20compiled entries have the same two read-image resource-name hashes at t0/t1 and one output-image hash at u0 (2D, no sampler); these match each pass's three original SetTexture literal hashes. Both passes reuse the same butterfly expression, and the first output expression is exactly the second input expression. Two dispatches use adjacent relative offsets0/1 and the same height expression with1x/1z groups. Original program order/workgroup verification and inherited seed proof remain prerequisites in the new single-run CI.

The existing no-Unity original FFT array-provenance workflow now authenticates/hydrates only sharedassets0.assets115978112bytes, decompiles original managed sources privately and runs all these checks together. It publishes only hashes/roles, not resources or code. This adds genuine metadata/source binding evidence; it does not prove runtime image aliasing, storage formats, Unity kernel enumeration, numerical FFT output or phone execution. Strict water gate and all game/shader data remain unchanged. Seven new local tests passed; remote CI pending. Next inspect original archive index and advance numeric/format verification, not guess an index or ship dummy kernels.


## Independent FFT caller size-source probe — 3 November 2026

After the inherited GpuFFT logarithmic seed was authenticated, the actual size supplied by WavesRendererFFT remained unproven. A new SHA-pinned read-only lexical probe follows the unique original Dx11FFT constructor's second argument, masks comments/strings, records only declaration types/lines, bounded assignment operators, RHS categories/hashes and numeric constants. It fails on source drift/ambiguous constructors and never publishes private source, identifiers or shader bytes. Five synthetic tests passed locally in an isolated helper harness; the real repository imports and original CSharp9 SHA still require cheap CI. This is NOT a type-resolved value, runtime FFT size, kernel index mapping, Unity compilation or device test. No Unity/APK/native request, no LFS transfer. Inspect CI output, then follow the authenticated size field and actual serialized source before any shader changes.


### Verified source-only caller size survey; alias-origin follow-up

[41551414117](https://github.com/alwansan/raf/actions/runs/41551414117) and runner guard41551414174 completed SUCCESS. The original SHA-pinned WavesRendererFFT has exactly one Dx11FFT constructor at line451. Its second argument is a simple reference with two lexical `int` declarations at lines226/450, and both assignments refer to the same original identifier hash; neither is a numeric constant. This narrows the next investigation to that identifier's origin, but lexical same-name matching does not establish CSharp scope/type or runtime size. Added one-hop, SHA-only alias declaration/write tracing with a sixth synthetic test. Fresh original-source CI pending. No private source, shader bytecode, Unity or APK publication.


### Final original FFT caller-size CI and next blocker — 3 November 2026

Source [a2c16ddf](https://github.com/alwansan/raf/commit/a2c16ddf52b6cede4e604a54811689dc9b50f1d6), [original managed source CI41551662918](https://github.com/alwansan/raf/actions/runs/41551662918), job125640484408: **COMPLETED SUCCESS**. Six synthetic tests and private SHA-pinned CSharp9 source execution passed. One `new Dx11FFT` call at line451; size argument is a simple identifier with lexical `int` declarations at lines226 and450. Both assignments reference the same identifier SHA256609a6259..., and a bounded one-hop search finds no matching declaration or assignment for that referenced identifier in the pinned WavesRendererFFT source. This is evidence that direct local assignment tracing has reached its limit, not proof of the external member's type/value or that 32..512 are actual runtime sizes. The next test should inspect original member/property declaration or caller dataflow with source fingerprint checks; retain the strict kernel-identity gate. Concurrent [authentic FFT resource-binding CI41551173277](https://github.com/alwansan/raf/actions/runs/41551173277) also completed SUCCESS, separately from this size probe. Neither is Unity/device validation. No proprietary source, native request, Unity, APK, OBB, XAPK, Release or LFS transfer.
