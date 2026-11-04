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

- [B45 — authenticated original Subsurface Blur one-texture ShaderLab property preservation](resources/B45-blur-original-property.json): acquisition=SHA_PIN_VERIFIED; extraction=SHA_PIN_VERIFIED; reconstruction=SOURCE_STRUCTURAL_VERIFIED; binding=NOT_VERIFIED; integration=NOT_INSTALLED; device=NOT_TESTED
- [إصلاح cleanup في دالةBlur الأصلية — دليل سابق محفوظ](resources/blur-original-cleanup.json): acquisition=VERIFIED; extraction=VERIFIED; reconstruction=CPU_TESTED; binding=NOT_APPLICABLE; integration=MANAGED_TESTED; device=UNKNOWN
- [Original FFT 10 source-selector/compiled-slot candidate pairs (not runtime kernel IDs)](resources/fft-original-selector-compiled-candidate-b48.json): acquisition=VERIFIED; extraction=VERIFIED; reconstruction=UNKNOWN; binding=UNKNOWN; integration=UNKNOWN; device=UNKNOWN

## الأحداث

- [2026-11-04 / owner-team-bootstrap](events/owner/20261104-b-generation.json): Owner replaces legacy clients with B01–B50. Preserve legacy evidence, release reservations, prioritize water/colors/local-world. Audio/Settings owner-confirmed; touch deferred. No B sessions have been started by setup.
- [2026-11-04T20:47:00Z / B50](events/B50/20261104T2047Z-local-steamstats-sourcefixed.json): SHA-pinned original SaveGame instrumentation now excludes SteamUserStats.StoreStats in Android-local mode only; C# original-source offline integration and bounded synthetic guards pass, device create/save/reload still unverified.
- [2026-11-04T20:54:00Z / B49](events/B49/20261104T2054Z-water-validation-start.json): Started distinct WATER-001 per-pass source gate false-positive repair and independent synthetic controls.
- [2026-11-04T20:56:00Z / B45](events/B45/20261104T2056Z-blur-start.json): Started SHA-pinned original Blur post-raster ShaderLab state diagnostic; work/test isolation from B49 and B50.
- [2026-11-04T20:58:00Z / B48](events/B48/20261104T2058Z-water-kernel-start.json): Investigate missing source-to-runtime FFT kernel identity link independent of current water ShaderLab pass work.
- [2026-11-04T20:58:00Z / B46](events/B46/20261104T2058Z-join-render-texture-links.json): Registered independent exported material-texture reference integrity lane, distinct from current LOCAL-005 and original shader audits.
- [2026-11-04T20:59:00Z / B44](events/B44/20261104T2059Z-start-material-values.json): B44 registered independent RENDER-002 Material SavedProperties color/texture value path investigation, separate from B47/B49 pass and B48 FFT work. No fix claimed.
- [2026-11-04T21:00:04Z / B47](events/B47/20261104T2100Z-pass-scope-collision.json): B49 authored/pushed identical per-Pass ShaderLab false-positive repair at 50702470954774ba96fe27509f1f9eddfd1aa4ea while B47 was testing same. B47 lost file-write race, read live HEAD and explicitly abandoned overlapping code patch; shifted to distinct ComputeShader entrypoint identity guard. No B49 code overwritten.
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
- [2026-11-04T21:10:20.156Z / B04](events/B04/20261104T2110Z-colorspace-integrated.json): SHA-authenticated original Linear project color space is guarded and conditionally restored after AssetRipper export; copied Unity candidate is read-only verified. Isolated CI success; no native/device proof.
- [2026-11-04T21:11:45.687Z / B03](events/B03/20261104T2111Z-archive-result.json): Added strict SHA-pinned raw/singlepart multipart source staging intake; 16 synthetic CI tests pass; real private archive payload remains unverified and issue OPEN.
- [2026-11-04T21:12:00Z / B02](events/B02/20261104T2112Z-import-guard-result.json): B02 source guard for original TextureImporter Gamma/Linear fidelity completed (synthetic 11/11, CI41913145660), with exact original SHA pins; no real exported mapping/asset repair/Unity/device evidence.
- [2026-11-04T21:12:00Z / B07](events/B07/20261104T2112Z-joined.json): B07 joined LOCAL-005 to verify original world completion and callback failure semantics independently of B50 Steam patches, with no fake world flags.
- [2026-11-04T21:16:00Z / B01](events/B01/20261104T2116Z-fft-lexical-result.json): Source-level FFT CSharp scanner now masks comments and strings before discovering compute calls; negative tests added. Final managed CI not yet complete, no kernel restoration/device claims.
- [2026-11-04T21:20:00Z / B01](events/B01/20261104T2120Z-fft-source-verified.json): SHA-pinned managed CSharp FFT callsite scanner corrected and validated in successful GitHub CI; 64 synthetic tests and numeric oracle pass; no device/Unity water claim.

بصمة المدخلات: d8343b8f2e91554f29824ab8a8346b68b457af5ee32865f639b8b4e6b022b360
