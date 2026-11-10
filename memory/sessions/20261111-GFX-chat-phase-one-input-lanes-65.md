# 20261111-GFX-chat-phase-one-input-lanes-65

role=GFX-LAB; origin=chat; resumed_from=20261111-GFX-chat-signature-component-width-64; base_sha=dcdb17e2253d1bcad5a386f6e39796c983d39ed5.

Owner requests sustained first-phase work through a test APK and actual phone acceptance. Closure governed by gfxlab/SHADER48_MODEL_PHASE_CLOSURE_AR.md; no transition to water/fire. GFX092 inspects exact actual input candidates; in addition audit whether compressed original ShaderSubProgram records retain unparsed resource metadata. No claim of restored Shader48.

## GFX092 verified; GFX093 decisive correction in progress
GFX092 CI42921521714 completed SUCCESS on c56a4a86a85ea6b2ac28adfa04a69a46fb769562; 883 tests, 12 actual input candidates and 427 authenticated dynamic reads. Safe artifact13812810626. No shader or phase completion.

Independent source inspection found `m_ParameterBlobIndices` for all 14 stage tables and nonempty `m_CommonParameters`. UnityPy1.25.4 `ShaderProgram` treats all 1656 records as GPU programs, although 381 are separately linked ParameterBlobs. Prior audits tested m_Parameters on PlayerSubProgram and RDEF but omitted these two sources. GFX054 absence claim is superseded, not evidence of unavailable original metadata. Previously classified unreferenced GL-family records also require withdrawal/reassessment; actual 1275 linked DXBC proofs remain separate.

New strict parser follows AssetRipper41d464112b99132f02df99e5f46e7f4eefa79c60 ShaderBlob/ShaderSubProgram.cs ReadParameters and entry boundaries. Local source-private evidence: 381 ParameterBlob records, 1435 stage links, merged 3642 texture bindings all found in corresponding original SHDR t/s declarations, 6562 CB bindings all found in source b declarations; 1852 property-to-t/s witnesses and 3344 property-to-b/member-byte witnesses (occurrences, not unique properties). 89 common/variant CB size differences explicitly retained; envelope is NOT runtime CB size, actual DXBC declaration remains authoritative. No original names/bytes/indices in public reports.

Next GFX093 CI independent replay, then translated original-stage Android compile/link matrix APK to test actual Adreno driver. This will not close model/rig/PC-pixel gates. Owner asked for APK and will return test logs; implement automated export to Download/Games/cl/test/g/.

## 11 Nov 2026 — current verified phase-one state (GFX092–096)

Session: `memory/sessions/20261111-GFX-chat-phase-one-input-lanes-65.md`.
**Read `gfxlab/PHASE_ONE_CURRENT_PLAN_AR.md` first.** Owner requests continuing phase one through an APK, phone evidence and full gates; no water/fire transition and no new general worker.

- GFX092 [42921521714](https://github.com/alwansan/raf/actions/runs/42921521714) SUCCESS,883 tests:12 actual source first-lane syntactic uses; not full component value/SSA parity.
- GFX093 [42922411580](https://github.com/alwansan/raf/actions/runs/42922411580) SUCCESS,893 tests: **corrects missing source parameter assumption**. 381 of1656 compressed records are separate ParameterBlobs, not unreferenced GL programs; `m_CommonParameters` also supplies original bindings.1435 stage links,3642/3642 t/s and6562/6562 b declaration witnesses;1852 property t/s and3344 property b/member-byte occurrences. GFX054 absence and unreferenced GL-family conclusions are superseded;1275 authentic linked DXBC proofs remain valid.89 common/variant CB size disagreements retained explicitly.
- GFX095 [42923520045](https://github.com/alwansan/raf/actions/runs/42923520045) SUCCESS,905 tests:7 material slots/6 unique materials;23408 exact float32 member writes/readbacks (17283float+6125color),167132 known material-byte occurrences;10201380 runtime byte occurrences remain unknown. No GPU payload upload.
- GFX096 [42924121842](https://github.com/alwansan/raf/actions/runs/42924121842) SUCCESS,910 tests:original builtin Standard name/editor/fallback plus27/27 property name/type/defaults and7 runtime pass names agree with official Unity2021.3.45f2 source after excluding2 editor META passes. Official ZIP SHA256 `5cb0f9c4d022d6054d179778b9b50a0301d6748eaf4abdedd21c93f0c30b10c5`. **Not yet recompiled DXBC or pixel identity**.
- GFX094 native Android compiler probe:285/314 stages emitted and128/157 pairs offline-linked;29 vertex stages explicitly unavailable because SPIRV-Cross rejects BaseInstance in GLES. Package `com.alwansan.gfx094`; exports entire ZIP automatically to `Download/Games/cl/test/g/`. First runs42922946685(translator exception),42923520011(javac LambdaMetafactory),42923838868(rg absent after successful signing) failed with purge; fixes committed. Current build42924333794 must be verified before APK delivery. No Unity/game/OBB rebuild.

NEXT: obtain GFX094 phone ZIP; independently recompile official Standard via Unity `ShaderData.Pass.CompileVariant` with exact original pass/keywords/tier, compare private DXBC SHDR/signatures before enabling a source-authenticated Standard material mode. Restore actual saved properties, original texture/normal/color-space semantics and shared identities; rig/geometry and PC/phone pixels still open. Do not continue tiny statistics while ignoring these larger gates. `originalShaderRestored=false`, `phase_closed=false`.


## GFX094 delivered — actual APK verified, owner Adreno test pending

[CI42924333794](https://github.com/alwansan/raf/actions/runs/42924333794) completed SUCCESS, including signing, APK ZIP/asset hashes and private-source purge. Immutable build SHA `66b2968673f410cbf58d5b255216c5e3c9c175ef`.

- APK `GFX094-Original-Shader48-Driver-Probe.apk`, package `com.alwansan.gfx094`,531851bytes.
- SHA256 `da7ae7fe39ad155f51e83e30f2c051e0c8992194f202b211a9db2e7df1b76030`.
- [Artifact13812833945](https://github.com/alwansan/raf/actions/runs/42924333794/artifacts/13812833945), expiry2026-11-17T23:35:49Z. Independent download verified artifact/APK CRC,APK SHA/size,314-stage manifest with285 available source-derived stages, and every packaged shader SHA against manifest.
- Saved for the owner as Library `libfile_22d8c2b2851c8191a78a42f8fc39f44b`. Opens landscape, no network; automatically tests157 representative pairs, including explicit CPU-unavailable29 BaseInstance stages; expects285 actual stage compile attempts and128 fully available pair link attempts. User should keep app foreground until logs saved. UI counters include unavailable pairs among failed pairs; inspect CPU_translation_unavailable vs compile/link events, never call those29 Adreno driver failures.
- Complete private test ZIP auto-exports to `/storage/emulated/0/Download/Games/cl/test/g/`; EXPORT ALL LOGS can retry/snapshot. No screenshots or manual clipboard logs are needed for this compiler-only probe.
- Owner should return one `GFX094-ALL-TEST-LOGS-*.zip`. This APK draws only a background and test progress; it does not render original models or bind original Unity runtime payloads. `originalShaderRestored=false`, `phase_closed=false`.

Next source work is exact official Standard recompilation and original property/texture/rig/PC-device proof in `gfxlab/PHASE_ONE_CURRENT_PLAN_AR.md`; the owner phone test is needed to resolve the actual Adreno compiler/linker gate. Do not claim phase closure from this APK. All authorized engineering edits are on our branch only; no T-team modifications or full-game builds.

