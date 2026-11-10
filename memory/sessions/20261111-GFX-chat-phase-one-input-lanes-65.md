# 20261111-GFX-chat-phase-one-input-lanes-65

role=GFX-LAB; origin=chat; resumed_from=20261111-GFX-chat-signature-component-width-64; base_sha=dcdb17e2253d1bcad5a386f6e39796c983d39ed5.

Owner requests sustained first-phase work through a test APK and actual phone acceptance. Closure governed by gfxlab/SHADER48_MODEL_PHASE_CLOSURE_AR.md; no transition to water/fire. GFX092 inspects exact actual input candidates; in addition audit whether compressed original ShaderSubProgram records retain unparsed resource metadata. No claim of restored Shader48.

## GFX092 verified; GFX093 decisive correction in progress
GFX092 CI42921521714 completed SUCCESS on c56a4a86a85ea6b2ac28adfa04a69a46fb769562; 883 tests, 12 actual input candidates and 427 authenticated dynamic reads. Safe artifact13812810626. No shader or phase completion.

Independent source inspection found `m_ParameterBlobIndices` for all 14 stage tables and nonempty `m_CommonParameters`. UnityPy1.25.4 `ShaderProgram` treats all 1656 records as GPU programs, although 381 are separately linked ParameterBlobs. Prior audits tested m_Parameters on PlayerSubProgram and RDEF but omitted these two sources. GFX054 absence claim is superseded, not evidence of unavailable original metadata. Previously classified unreferenced GL-family records also require withdrawal/reassessment; actual 1275 linked DXBC proofs remain separate.

New strict parser follows AssetRipper41d464112b99132f02df99e5f46e7f4eefa79c60 ShaderBlob/ShaderSubProgram.cs ReadParameters and entry boundaries. Local source-private evidence: 381 ParameterBlob records, 1435 stage links, merged 3642 texture bindings all found in corresponding original SHDR t/s declarations, 6562 CB bindings all found in source b declarations; 1852 property-to-t/s witnesses and 3344 property-to-b/member-byte witnesses (occurrences, not unique properties). 89 common/variant CB size differences explicitly retained; envelope is NOT runtime CB size, actual DXBC declaration remains authoritative. No original names/bytes/indices in public reports.

Next GFX093 CI independent replay, then translated original-stage Android compile/link matrix APK to test actual Adreno driver. This will not close model/rig/PC-pixel gates. Owner asked for APK and will return test logs; implement automated export to Download/Games/cl/test/g/.
