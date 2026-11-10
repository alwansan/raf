# GFX-LAB — 20261110-GFX-chat-owner-evidence-01

- session_id: `20261110-GFX-chat-owner-evidence-01`
- origin: `chat`
- resumed_from: `20261110-GFX-chat-passstate-material-binding-29`
- base_sha: `5e9b48312d3be4e6226d92b8e637db716cbf955d`
- experiment_key: `GFX-OWNER-001-user-provided-Android-six-model-channel-evidence-and-closure-gates`
- issue: `RENDER-002`
- owner_archive_sha256: `adc08713ad67a987d0b30ac01b1b6e9004342b359aeb97ed1ee61866fecc4238`
- original_source_sha: `ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- target_apk: `GFX026 CI42748792585` / `8fef68d82748cd214b1f5f5f9c0b3903a80f343513ccb15fc35e12649c02ad52`
- scope: independently inspect supplied screenshots, 13 device COPY LOG snapshots, report and cached Android shader binaries; classify current source art vs authentic Shader48 restoration gates. Do not upload owner screenshots or cached proprietary shader bytes.
- status: `EVIDENCE_REVIEW_UNDERWAY`

## Initial safe observations
- User supplied `test model(1).zip` (9.0MB ZIP): 16 JPEG screenshots (2400×1080), `text 3.txt` with 13 concatenated JSON reports, one last `multi-report.json`, ten compiled UnityShaderCache entries, and IL2CPP app data. ZIP CRC check passed.
- All six models M00–M05 present in COPY LOG, both ALBEDO and Standard PBR approximation observed; 13/13 have `errors=0` and no `firstError`. All 13 captured channel/probe states are BASECOLOR/RGB/SOURCE_COLORSPACE; image captures show Normal/Metallic preview but do not provide exact JSON pairing, R/G/B/A or FORCE_LINEAR logs.
- Current source view build `GfxMultiAndroidBuilder.cs` uses Shader.Find(\"Standard\") and `Hidden/GfxLab/ChannelProbe`, and hardcoded `_Glossiness=.45`; PBR metallic importer `sRGBTexture=role==\"basecolor\"` differs from original Texture2D Metallic m_ColorSpace=1 (sRGB) proven GFX024. Difference is not proof PBR runtime must be altered blindly; it proves source fidelity not closed.
- Shader48 original GPU compilation not proven. Seven original Shader48 Passes / 524 exact keyword-tiers, missing RDEF/parameters; GFX029 only partial ZWrite material float link. Exact shader closure `OPEN`.

## Next
- Create safe, reusable ZIP log auditor with independent negative tests. Publish closure checklist and work plan for repeatable worker later, but **do not create worker** until owner supplies design and gates are actually met.
