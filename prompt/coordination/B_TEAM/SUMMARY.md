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

- [B45 — authenticated original Subsurface Blur one-texture ShaderLab property preservation](resources/B45-blur-original-property.json): acquisition=SHA_PIN_VERIFIED; extraction=SHA_PIN_VERIFIED; reconstruction=CPU_VULKAN_NUMERIC_AND_PRIVATE_SHADERLAB_VERIFIED; binding=NOT_VERIFIED; integration=GATED_NATIVE_STAGING_WIRED_NOT_EXECUTED; device=NOT_TESTED
- [إصلاح cleanup في دالةBlur الأصلية — دليل سابق محفوظ](resources/blur-original-cleanup.json): acquisition=VERIFIED; extraction=VERIFIED; reconstruction=CPU_TESTED; binding=NOT_APPLICABLE; integration=MANAGED_TESTED; device=UNKNOWN
- [Original FFT 10 source-selector/compiled-slot candidate pairs (not runtime kernel IDs)](resources/fft-original-selector-compiled-candidate-b48.json): acquisition=VERIFIED; extraction=VERIFIED; reconstruction=UNKNOWN; binding=UNKNOWN; integration=UNKNOWN; device=UNKNOWN

## الأحداث

- [2026-11-04T21:01:00Z / B02](events/B02/20261104T2101Z-start.json): B02 registered independent P0 texture sRGB/Linear importer provenance check; explicit original/export identity required, no guessed GUID or value overwrite.
- [2026-11-04T21:01:00Z / B49](events/B49/20261104T2101Z-water-pass-guard-result.json): Source-integrated per-pass ShaderLab gate correction; independent synthetic+existing CI11/11 success; WATER-001 still OPEN, no GPU or original program restored.
- [2026-11-04T21:02:00Z / B50](events/B50/20261104T2102Z-local-cheat-steamid-sourcefixed.json): Original ZIP2-pin-backed Cheat.AllowCheatsForLocalPlayer SteamUser.GetSteamID() call uses Android-local stable managed CSteamID only, Windows path preserved; six private source-probe negative controls and final original managed compilation CI pass; phone world create/save/reload still unverified.
- [2026-11-04T21:02:14Z / B04](events/B04/20261104T2102Z-start.json): Register independent original game Linear ProjectSettings parity and guarded transient-export repair
- [2026-11-04T21:02:53.792Z / B03](events/B03/20261104T2101Z-archive-start.json): Started exact canonical-byte SHA-verified archive source transport verification; private wrapper hypothesis not yet proven; ZIP2 fallback retained.
- [2026-11-04T21:04:07.263Z / B43](events/B43/20261104T2104Z-B43-start.json): Joined B43 as new identity; selected independent material shader keyword/variant export fidelity lane after live Actions/release/owner priority review.
- [2026-11-04T21:05:00Z / B47](events/B47/20261104T2105Z-compute-kernel-contract.json): B47 integrated source-only ComputeShader kernel pragma-to-numthreads-entrypoint validation; CI 41912450062 PASS (8 new +5 existing); authentic FFT kernel identity and device unknown.
- [2026-11-04T21:05:00Z / B01](events/B01/20261104T2105Z-start-fft.json): B01 joined water-FFT source kernel/dispatch binding validation; preserve owner-confirmed audio and Settings and defer touch.
- [2026-11-04T21:05:46Z / B48](events/B48/20261104T2105Z-fft-candidate-result.json): Authentic original CSharp selector and 20 SHA-verified compiled FFT programs agree structurally for 10 candidate two-pass operations (original workgroup x=2*resolution). 15/15 tests and real-data CI pass. Runtime kernel mapping not proven; WATER-001 OPEN.
- [2026-11-04T21:07:00Z / B44](events/B44/20261104T2107Z-material-colors-tested.json): Added safe SHA-pinned Material m_Colors fidelity source-vs-export comparator and 10 synthetic positives/negatives. CI run 41912783093 success on f1dd7fcc; actual Raft export value comparison not yet executed, so RENDER-002 OPEN.
- [2026-11-04T21:07:26.584Z / B06](events/B06/20261104T210726Z-B06-fmt6a2-start.json): B06 begins complementary original GpuFFT storage-format/RenderTexture binding investigation; no device, Unity or game build validation yet.
- [2026-11-04T21:10:00Z / B45](events/B45/20261104T2117Z-blur-source-cpu-result.json): Authenticated original Subsurface Blur property serializer fixes post-raster wrapper failure; both genuine passes regenerate private 23068-byte ShaderLab with zero per-pixel color/depth error on six CPU Vulkan positive comparisons and all 12 mutations detected; Unity/phone not tested.
- [2026-11-04T21:10:20.156Z / B04](events/B04/20261104T2110Z-colorspace-integrated.json): SHA-authenticated original Linear project color space is guarded and conditionally restored after AssetRipper export; copied Unity candidate is read-only verified. Isolated CI success; no native/device proof.
- [2026-11-04T21:11:45.687Z / B03](events/B03/20261104T2111Z-archive-result.json): Added strict SHA-pinned raw/singlepart multipart source staging intake; 16 synthetic CI tests pass; real private archive payload remains unverified and issue OPEN.
- [2026-11-04T21:12:00Z / B02](events/B02/20261104T2112Z-import-guard-result.json): B02 source guard for original TextureImporter Gamma/Linear fidelity completed (synthetic 11/11, CI41913145660), with exact original SHA pins; no real exported mapping/asset repair/Unity/device evidence.
- [2026-11-04T21:12:00Z / B07](events/B07/20261104T2112Z-joined.json): B07 joined LOCAL-005 to verify original world completion and callback failure semantics independently of B50 Steam patches, with no fake world flags.
- [2026-11-04T21:13:18.875Z / B03](events/B03/20261104T2115Z-render-material-start.json): Investigate missing/incorrect exported Renderer.m_Materials identity separately from Shader and texture checks; no changes to original assets.
- [2026-11-04T21:14:08.582Z / B06](events/B06/20261104T210726Z-B06-fmt6a2-fft-capabilities-sourcefixed.json): Added startup-only original FFT format/render-target random-write + compute-group capability logging to AndroidRuntimeLog; real C# logger compiled and executed against synthetic failure controls, CI SUCCESS. No Unity/device claim.
- [2026-11-04T21:14:58.288Z / B04](events/B04/20261104T2118Z-asset-mesh-safety-start.json): Investigate Mesh vertex restoration source path safety, especially symlinked .asset/.meta; preserve original .meta/GUID and fail closed
- [2026-11-04T21:15:00Z / B05](events/B05/20261104T2115Z-source-contract-result.json): Integrated SHA-pinned-original-aware Material m_TexEnvs-to-same-export pointer fidelity verifier and 11 synthetic controls; CI41914198631 SUCCESS, no source or device rendering claim.
- [2026-11-04T21:15:00Z / B44](events/B44/20261104T2115Z-color-guard-11-ci-pass.json): B44 Material m_Colors same-instance export fidelity guard hardened against duplicate YAML keys; 11 synthetic controls and independent GitHub CI41913494314 SUCCESS. Source tool integrated to branch, original Raft/full export comparison still unknown; no device fix or closure claimed.
- [2026-11-04T21:15:00Z / B11](events/B11/20261104T2115Z-gamut-start.json): Independent gamut parity scope: original [0] authenticated by B04; actual export unknown; device whiteness not attributed.
- [2026-11-04T21:15:00Z / B45](events/B45/20261104T2117Z-blur-native-wiring.json): Bounded private ShaderLab recovery plus exact-candidate SHA, exported target/GUID backup rollback logic added to explicitly requested native workflow; 9 synthetic installer/staging tests pass. Native Unity import has not executed and strict WATER/FFT gates remain enabled.
- [2026-11-04T21:16:00Z / B01](events/B01/20261104T2116Z-fft-lexical-result.json): Source-level FFT CSharp scanner now masks comments and strings before discovering compute calls; negative tests added. Final managed CI not yet complete, no kernel restoration/device claims.
- [2026-11-04T21:17:00Z / B46](events/B46/20261104T2117Z-render-texture-links-ci.json): B46 authored source checker and negative fileID controls, integrated into isolated CI; 21 checks PASS on source 04d7e05. Real game export/device not verified and RENDER remains OPEN.
- [2026-11-04T21:17:00Z / B45](events/B45/20261104T2117Z-blur-private-stage-result.json): Private exact Blur source SHA 5886dc36... staged successfully in isolated CI from authenticated ZIP2 with six zero-difference color/depth comparisons and all raster mutation guards. Source not published; external native project not modified; Unity/Adreno acceptance pending.
- [2026-11-04T21:17:51.568Z / B04](events/B04/20261104T2120Z-asset-mesh-source-integrity.json): Mesh source path guard rejects linked YAML/.meta/providers/snapshot; isolated 6-test CI success; original game/device geometry still unverified.
- [2026-11-04T21:17:54.375Z / B43](events/B43/20261104T2117Z-B43-keyword-tests.json): Original-to-export Material keyword/pass state verifier and synthetic YAML/meta controls completed; CI 17/17 PASS; no real export/device claim.
- [2026-11-04T21:18:03.365Z / B06](events/B06/20261104T210726Z-B06-fmt6a2-dispatch-lexical-sourcefixed.json): Hardens secondary authenticated FFT resource Dispatch shape parser against comment/string false positives using shared B01 executable-only masking; 8/8 synthetic tests passed; original-private/Unity/device pending.
- [2026-11-04T21:20:00Z / B01](events/B01/20261104T2120Z-fft-source-verified.json): SHA-pinned managed CSharp FFT callsite scanner corrected and validated in successful GitHub CI; 64 synthetic tests and numeric oracle pass; no device/Unity water claim.

بصمة المدخلات: feb72314022c05c1ed536b8c09783d05d60476ff4ff8b8342d846878ba697aeb
