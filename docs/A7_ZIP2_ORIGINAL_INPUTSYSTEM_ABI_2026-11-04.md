# A7 — authentic ZIP2 InputSystem ABI compatibility (CPU metadata only)

Date: 2026-11-03T22:54:21.305Z. Client `raft-20261103T224215Z-a7d93c52`, session `A7-20261103T224215Z-0c9d72f3`. Writable branch `feature/android-native-port`; original ZIP2 read-only commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.

## Why

Previous A7 INPUT-005 repairs extracted AndroidTouchPointer C# source into strict Unity event doubles, validating synthetic second-finger routing and 500ms LEFT Mouse0. They did **not** verify that the original Raft distribution's `Unity.InputSystem.dll` exposes the same public managed ABI. The user supplied the complete game in the ordinary-Git `zip2/Raft` provider. This experiment addresses that specific integration gap, without using Git LFS or a Unity build.

## Verified original provider

- Source file: `Raft/Raft_Data/Managed/Unity.InputSystem.dll`, a plain Git blob in ZIP2 (not split parts). ZIP2 immutable source SHA pin checked before reading file.
- Exact original size: **1,052,672 bytes**.
- Original manifest SHA-256: `032031efe7f85aec81e28f4af43be496be3cf83d8d20e314ba9de8ca95ebfc3f`.
- `ScriptingAssemblies.json` checked original SHA-256 `50becc5aca96c0287bd8e909cea80ffbb94e45631f8dbb45740c0614e00cbf20`; lists `Unity.InputSystem.dll`.
- Sparse partial Git checkout fetched only this original DLL and metadata manifests, no LFS pulls, no full game checkout or published original DLL/derived source.

## Live CI sequence

1. [Initial ABI run 41734239232](https://github.com/alwansan/raf/actions/runs/41734239232) **FAIL** in checker: it incorrectly assumed `TouchState.phase` is a public field. Original managed metadata reveals a public property backed by `phaseId`; source runner/pins were valid. Not a production gameplay defect.
2. [Corrected phase run 41734394488](https://github.com/alwansan/raf/actions/runs/41734394488) **FAIL** in checker: it incorrectly expected `InputSystem.onEvent` as a CLR event `add_onEvent`. Original API actually declares a public get/set `InputEventListener` property. Again, not gameplay failure.
3. Corrected checker at [source 24688691567ccc84177a8d97e3e699bac6de9d6e](https://github.com/alwansan/raf/commit/24688691567ccc84177a8d97e3e699bac6de9d6e); [final **CI 41734563980**](https://github.com/alwansan/raf/actions/runs/41734563980) **COMPLETED SUCCESS** on that exact source.

Actual final log:
`RAFT_A7_ZIP2_INPUTSYSTEM_ABI authenticated_source=true bytes=1052672 metadata_types=639 touchstate_fields=3 phase_property=true onEvent_property=true public_raw_state_api=true original_lfs_used=false unity_execution=false android_device_execution=false`

Confirmed public metadata members used by authored Android input adapter: generic `StateEvent.GetState`, `TouchState.touchId`, `TouchState.position`, `TouchState.phaseId` and public `phase` getter, `InputEventPtr.IsA` generic, `InputSystem.onEvent` public read-write property, `InputSystem.onBeforeUpdate` public add method, `Touchscreen` type. Negative controls: mutated original DLL failed SHA authentication; modified original manifest failed matching. Both were detected and rejected. These checks run on the actual original DLL rather than Unity doubles.

## Engineering limits / acceptance

This is genuine, SHA-authenticated *managed metadata compatibility evidence*, and it closes only the scoped ZIP2 InputSystem API verification question. It does not compile AndroidTouchPointer inside Unity Editor, prove runtime event ownership, validate virtual Xbox+UI simultaneous touches on an Android phone, or solve original water/shader/material/graphics problems. No Unity/APK/OBB/XAPK or Release created, and old published APK80 still predates the A7 runtime source fixes.

Global INPUT device acceptance remains pending. WATER-001/RENDER-002/FFT-FORMAT-009 and readiness **NOT_READY / 0 of 3 immutable candidate reviews** remain unchanged. No writes to `zip2`, `main`, `zip`, `Unity-Editor`, `CL`, original .meta/GUID assets, native request JSON or existing scheduled tasks.
