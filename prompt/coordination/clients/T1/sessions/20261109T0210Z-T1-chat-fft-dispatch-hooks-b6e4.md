# T1 — SHA-original Android FFT direct Dispatch trace staged
session_id: 20261109T0210Z-T1-chat-fft-dispatch-hooks-b6e4
origin: chat
resumed_from_sessions: 20261109T0155Z-T1-chat-direct-dispatch-f7a2; 20261109T0142Z-T1-chat-fft-kernel-index-r4c8
issue_id: WATER-001
base_sha: 4ba06e08894e5b7a1267c9b408b354e625f66a96
work: prompt/coordination/work/WATER-001/20261109T0210Z-T1-chat-fft-dispatch-hooks-b6e4.json
experiment_key: t1-original-source-dx11fft-runtime-before-after-sha8aa32937-v1
resource_key: null

## Verified original and staged game-source patch
- Authentic PC Assembly-CSharp.dll Git blob: fc9d4ba920a178fdb89c970d9d772a01051dadc6 (3,211,776 bytes), previously independently source verified CI42519853981.
- Original ILSpy CSharp9: Dx11FFT sha256 8aa32937d4235f0f1ae0a180b8099fd647558689ad65208a9f37956c69e90fb0; inherited GpuFFT sha256 2f866cbe58836da8260461fe6406793f35d868eba94e816e593209544b4ba704.
- New scripts/t1_stage_original_fft_dispatch_trace.py only applies to exact original→adapt_android_render_lifetimes output, finds exactly TWO standalone original Dispatch statements, proves inherited protected exponent field, refuses extra/mismatched callsites/side effects, retains original numeric arguments, .meta and cleanup statements. Android conditional pre/post callbacks only.
- New android-port/Runtime/Platform/T1FftDirectDispatchTrace.cs logs first 16 original managed dispatch calls with source provenance prefix, actual numeric arg, observed inherited exponent, source-bank candidate (NOT measured constructor bool), session-local shader instance ID, group XYZ, frame and compute capability. It emits .before and .returned metadata (returned to caller is NOT GPU result success). Exceptions in diagnostics are swallowed, never original Dispatch errors.
- Integrated native CI step AFTER original render-lifetime repair in .github/workflows/raft-unity-editor-android-import.yml, before original startup adaptation; helper included in Unity source-copy set. Ordinary code push does NOT trigger main native build; this integration waits for T5/owner authorized next full build.
- T2 foam, T3 graphics, T4 mouse and T5 unified mini untouched; CL read-only; native request/votes not altered.

## Authentic source and CSharp proof
- Initial synthetic test CI42549999984 FAILED (one negative control asserted wrong rejection string); corrected test expectation with commit 4ac11c09c52f32ef94ceacc12edabf7ca15486f1, no gate relaxation. Failure preserved.
- Authentic original staged source CI42550062087 SUCCESS (14/14 source-only tests, authentic original managed ILSpy + lifetime-patched placement).
- After native staging integration CI42550189294 SUCCESS at ec5bf2f4568cc8baba247b709588860bd85d56de. Original Dispatch sites preserved 2, no FindKernel invented.
- Final CI42550454734 SUCCESS at source SHA 41559e96324b96293457ff578d5e069fe5a8bf53: 14/14 Python tests, CSharp9 helper compiled and executed on synthetic Unity ABI (.NET10), logger bounded at 16 calls and optional write failures nonintrusive, authentic original managed SHA ILSpy and two original site attachments verified. All tests were SOURCE/host synthetic; not real Unity Editor, Adreno or Raft device.
- Actual original Unity CSharp compilation/Android runtime occurrence remains UNKNOWN. No new APK/OBB/XAPK. No claim of restored GPU FFT/shaders/materials, WATER-001 OPEN, NOT_READY0/3, T1 shared Mini NO_BUILD.

## Handoff
- T5 integration note: prompt/coordination/discussions/WATER-001/20261109T0210Z-T1-chat-fft-dispatch-hooks-b6e4-to-T5-fft-runtime-trace.md
- Next authorized original Raft game build: preserve staged source and Unity2021 ABI proof, verify first water root error against first 16 matching .before and .returned logs, compare source numeric arg and registered original ComputeShader instance independently; can falsify Dx11FFT caller hypothesis.
- Never claim .returned = GPU completed, original index6 = compiled slot6, bank inference=actual bank flag, or app's GLES mini T1 PASS=original Raft water PASS.
