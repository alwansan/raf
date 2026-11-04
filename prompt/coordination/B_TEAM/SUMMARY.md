# ملخص فريق B — مولد من السجلات

هذا فهرس أدلة، وليس إعلان جاهزية أو نسبة اكتمال اللعبة. النسبة الكلية غير معلومة.
يُجدد في كل checkpoint؛ ليس خدمة تعمل بين الجلسات.

| المشكلة | الأولوية | الحالة | المسار |
|---|---|---|---|
| [LOCAL-005 — العالم المحلي يتوقف بعد تحميل المشهد](issues/LOCAL-005.json) | P0 | OPEN | world-save |
| [RENDER-002 — الألوان البيضاء والخامات والتكستشر والمؤثرات](issues/RENDER-002.json) | P0 | OPEN | colors-materials |
| [WATER-001 — الماء وFFT وبرامج الشيدرات الأصلية](issues/WATER-001.json) | P0 | OPEN | water-fft |
| [ASSET-RESTORE-001 — اكتمال meshes/textures/Resources/روابطالأصل](issues/ASSET-RESTORE-001.json) | P1 | OPEN | resources |
| [INTEGRATION-001 — دمج الإصلاحات والتحقق وتسليم تشخيصي منسق](issues/INTEGRATION-001.json) | P1 | OPEN | integration |
| [PERF-007 — أداء وذاكرة تحت تدفق أخطاء الرسم](issues/PERF-007.json) | P1 | OPEN | integration |
| [SOURCE-ARCHIVE-001 — اعتماد payload الأرشيف الخاص مقابلZIP2](issues/SOURCE-ARCHIVE-001.json) | P1 | OPEN | source-integrity |
| [AUDIO-REGRESSION — الصوت يعمل بحسب تجربة المالك](issues/AUDIO-REGRESSION.json) | P2 | OWNER_CONFIRMED | regression |
| [DISPLAY-003 — Settings مستقر بحسب تجربة المالك](issues/DISPLAY-003.json) | P2 | OWNER_CONFIRMED | regression |
| [INPUT-005 — التاتش والأزرار واللاي آوت مؤجلة](issues/INPUT-005.json) | DEFERRED | DEFERRED | deferred |

## الموارد ذات السجل المفصل

لكل مورد مراحل منفصلة؛ UNKNOWN لا يعني نجاحاً ولا فشلاً.

- [B10 — reproducible ShaderImporter GUID sidecars for newly added vendor-only shader fallbacks](resources/B10-generated-vendor-shader-metadata.json): acquisition=EXISTING_PINNED_VENDOR_SOURCES_NO_NEW_DOWNLOAD; extraction=NOT_APPLICABLE; reconstruction=GENERATED_META_SCHEMA_SOURCE_FIXED_SYNTHETIC_TESTED; binding=SOURCE_META_GUID_COLLISION_GUARDED_NOT_REAL_EXPORT_VERIFIED; integration=PRODUCTION_HELPER_INTEGRATED_CPU_CI_PASS_22_22; device=NOT_TESTED
- [B45 — authenticated original Subsurface Blur one-texture ShaderLab property preservation](resources/B45-blur-original-property.json): acquisition=SHA_PIN_VERIFIED; extraction=SHA_PIN_VERIFIED; reconstruction=CPU_VULKAN_NUMERIC_AND_PRIVATE_SHADERLAB_VERIFIED; binding=NOT_VERIFIED; integration=GATED_NATIVE_STAGING_WIRED_NOT_EXECUTED; device=NOT_TESTED
- [إصلاح cleanup في دالةBlur الأصلية — دليل سابق محفوظ](resources/blur-original-cleanup.json): acquisition=VERIFIED; extraction=VERIFIED; reconstruction=CPU_TESTED; binding=NOT_APPLICABLE; integration=MANAGED_TESTED; device=UNKNOWN
- [B08 original FFT ComputeShader one-name/twenty compiled-program aliases](resources/fft-original-name-registry-b08.json): acquisition=VERIFIED; extraction=VERIFIED; reconstruction=UNKNOWN; binding=UNKNOWN; integration=UNKNOWN; device=UNKNOWN
- [Original FFT 10 source-selector/compiled-slot candidate pairs (not runtime kernel IDs)](resources/fft-original-selector-compiled-candidate-b48.json): acquisition=VERIFIED; extraction=VERIFIED; reconstruction=UNKNOWN; binding=UNKNOWN; integration=UNKNOWN; device=UNKNOWN

## الأحداث

- [2026-11-04T21:20:45.386Z / B03](events/B03/20261104T2119Z-render-material-result.json): Implemented read-only exported Renderer→Material identity integrity checker; 17 synthetic CI tests pass, no actual full export or device-color evidence; RENDER-002 remains OPEN.
- [2026-11-04T21:22:00Z / B02](events/B02/20261104T2122Z-texture-semantics-safety.json): Pinned AssetRipper importer SRGBTexture uses ColorSpace.Linear, opposite B02 initial guess; unsafe repair path fully disabled, read-only dual interpretation and 12/12 safe CI. No game assets modified; RENDER-002 OPEN.
- [2026-11-04T21:24:00Z / B05](events/B05/20261104T2124Z-uv-fidelity-result.json): B05 extended original Material texture PPtr lineage validator with UV m_Scale/m_Offset finite and drift checks; CI41915604221 SUCCESS (14 synthetic tests). Two transient fixture migration failures diagnosed and closed. No original material or device proof.
- [2026-11-04T21:24:00Z / B11](events/B11/20261104T2124Z-gamut-integration.json): B11 bounded original gamut check and optional exact-field repair wired into native transient export with candidate recheck; 12/12 synthetic local tests; actual Raft export/device unknown, RENDER-002 remains OPEN.
- [2026-11-04T21:24:00Z / B07](events/B07/20261104T2124Z-world-callback-trace-sourceintegrated.json): Verified 3 original GameManager.OnWorldRecieved SaveGame branches and exact SHA-pinned Android operation trace, preserving original body/exception propagation. CI41915466470 SUCCESS 8/8 probe + 7/7 wrapper cases and private original instrumentation; no Unity/device/.rgd evidence. LOCAL-005 remains OPEN.
- [2026-11-04T21:27:28.998Z / B24](events/B24/20261104T2126Z-start.json): B24 selected independent GameManager world-callback instrumentation parity: native path instruments GameManager; cheap managed candidate skips trace-only original GameManager. Patching fail-closed, source-pinned coverage without changing real game behavior.
- [2026-11-04T21:29:00Z / B07](events/B07/20261104T2129Z-world-callback-managed.json): B07 production Android callback tracing compiler-executed through synthetic .NET10 C# project under UNITY_ANDROID: 3 SaveGame branches, 3 begin/end events, 1 thrown/rethrown exception and finally failure marker. CI41916347469 SUCCESS; exact original source probe still passes privately. NOT Unity/device/.rgd proof, LOCAL-005 OPEN.
- [2026-11-04T21:30:35Z / B08](events/B08/20261104T2130Z-start.json): B08 joins independent original FFT typed kernel-name/variant registry identity proof; B48 candidate compiled slots are not assumed Unity runtime kernel IDs. Audio and Settings preserved; touch deferred.
- [2026-11-04T21:31:48.375Z / B10](events/B10/20261104T2132Z-start-vendor-meta.json): B10 active P0 shader export metadata lane: native41741108965 reported two missing .shader.meta after authenticated TMP fallback additions; repairing only newly generated vendor shader metadata, original GUIDs untouched.
- [2026-11-04T21:32:00Z / B13](events/B13/20261104T2132Z-start.json): Start LOCAL-005 Android offline adapter failure-atomicity source repair; maintain original CSharp/metas and no touch, FMOD or Settings edits.
- [2026-11-04T21:32:10.807Z / B24](events/B24/20261104T2131Z-result.json): B24 source-integrated SHA-locked GameManager callback instrumentation in original offline compile. 6 B24 synthetic controls and original managed compilation+local RPC CI successful; no Unity/device or world-save closure.
- [2026-11-04T21:33:06.790Z / B14](events/B14/20261104T2131Z-start.json): Registered WATER-001 path-provenance source repair; sidecar/Assets symlink acceptance is the specific hypothesis, not a claim of restored water.
- [2026-11-04T21:33:58.649Z / B12](events/B12/20261104T2132Z-start-stats.json): B12 joins distinct LOCAL-005 SaveGame StoreStats boundary: APK86 proven steam_api64 DllNotFound after world loaded; current SHA-pinned adapter protects SteamID but not this call. Will guard optional Steam stats only for Android local sessions, preserve .rgd writes/Windows/callbacks; tests required.
- [2026-11-04T21:34:30Z / B22](events/B22/20261104T2134Z-scalar-start.json): Registered distinct P0 same-instance Material m_Floats/m_Ints VALUE fidelity investigation; not another W2 census or B44 color check.
- [2026-11-04T21:36:00Z / B08](events/B08/20261104T2136Z-fft-registry-result.json): Authenticated original FFT ComputeShader pathID2456 has 20 compiled DXBC slots but one distinct serialized kernel name (all slot positions 0..19 alias). 11 synthetic controls and original ZIP2 SHA/order checks passed in B08 CI41917369953. Reject 20 independent runtime FindKernel ID hypothesis; source/runtime integration remains unproven and WATER-001 OPEN.
- [2026-11-04T21:36:19.755Z / B24](events/B24/20261104T2135Z-foam-stage-start.json): B24 moves to unowned Foam/Global original two-pass pass-program conversion gap; source-bound, private original DXBC-stage translation instead of repetitive pass census, maintaining authentic gates.
- [2026-11-04T21:37:03Z / B19](events/B19/20261104T2137Z-start.json): B19 joined LOCAL-005 for independent original SaveAndLoad source path backup integrity; avoid B12/B13 common adapter, preserve .meta and real .rgd, no device claims.
- [2026-11-04T21:37:39.145Z / B14](events/B14/20261104T2137Z-result.json): Water scanner source-integrity fix for linked project/Assets/shader/compute metadata: integrated at cfb97bf and verified at CI41917493634 with 10/10 source-only tests; no authentic water/device claim.
- [2026-11-04T21:38:14.359Z / B09](events/B09/20261104T213740Z-spectrum-start.json): B09 joined WATER-001 to isolate original Spectrum/Water Spectrum six-pass authenticated source-to-native staging; complements B24 Foam, B45 Blur and B48 FFT; no game build or shader claim.
- [2026-11-04T21:38:37.770Z / B10](events/B10/20261104T2138Z-vendor-meta-integration.json): Production vendor shader fallback path now generates stable collision-checked ShaderImporter .meta sidecars with rollback and preserves original .meta bytes. Exact earlier native missing-meta paths unproven; source/CI only. B10 isolated CI22/22 and A3 transaction CI9/9 success.
- [2026-11-04T21:40:00Z / B30](events/B30/20261104T2140Z-B30-water-start.json): B30 registered independent original FFT serialized variantMap and keyword selector investigation after B08/B48; no Unity runtime or device proof claimed.
- [2026-11-04T21:40:24.035Z / B14](events/B14/20261104T2139Z-local-start.json): Started staged Unity original SaveAndLoad/Android offline adapter root redirection safety repair after completed WATER scope; no RGD or Steam semantics changes.
- [2026-11-04T21:41:00Z / B17](events/B17/20261104T2141Z-start-spectrum.json): B17 registered original Spectrum shader per-pass texture/sampler descriptor provenance track. Independent of B24 Foam/B45 Blur/B08 FFT, no game code changed, authentic source and device not yet tested.
- [2026-11-04T21:42:00Z / B38](events/B38/20261104T2142Z-start-material-texenv.json): B38 registers independent P0 Material texture/UV YAML duplicate-key safety gap; B05 prior work complete/paused, B44 color verifier separate; no phone/build claim.
- [2026-11-04T21:43:25Z / B19](events/B19/20261104T2143Z-result.json): Original SaveAndLoad C#/.meta backup staging and verified rollback integrated; isolated CI41918301442 SUCCESS (10 synthetic tests, private SHA-pinned original 16 path expressions, 14 .NET path checks). No gameplay/device claim.
- [2026-11-04T21:43:48.860Z / B14](events/B14/20261104T2144Z-local-result.json): Two existing offline original source adapters now reject symlinked project/backup roots and ancestors; 32/32 source-only tests in isolated GitHub Actions 41918579185 SUCCESS; no .rgd device claim.
- [2026-11-04T21:44:30Z / B22](events/B22/20261104T2144Z-scalar-result.json): Source-integrated original Material m_Floats/m_Ints per-instance binary32 parity guard; 14 synthetic CI tests PASS 41918404573; real export and device not tested, RENDER-002 still OPEN.
- [2026-11-04T21:46:00Z / B13](events/B13/20261104T2146Z-result.json): Offline source adapter backup rollback fixed and restored after lost-tree regression; B13 CI 16/16 twice; world/device still unverified.
- [2026-11-04T21:47:35.699Z / B12](events/B12/20261104T2148Z-scene-shader-result.json): B12 integrated a bounded Android scene shader/material-status diagnostic (3s delayed, max512 active renderers; counts null, unsupported, zero-pass, error shader, color-space/lighting) without mutating Materials or touching audio, Settings, touch, .rgd, original assets. Source-policy CI41919089409 SUCCESS, original managed integration CI41918822038 SUCCESS. This observes future real device state only; source graphics restoration and phone white-material cause still OPEN.
- [2026-11-04T21:47:37.589Z / B09](events/B09/20261104T2140Z-spectrum-source-result.json): Committed a SHA-pinned private Spectrum DXBC pass-stage extraction/variant pairing tool, 10/10 local synthetic tests passed, and an isolated ZIP2-only CI workflow. Actual original Shader result and workflow conclusion unknown; no water shader reconstruction or device fix claimed.

بصمة المدخلات: 27d03b17736594c1573cd93204c36688e0dd0d297ca6e700b6c8fd427a949957
