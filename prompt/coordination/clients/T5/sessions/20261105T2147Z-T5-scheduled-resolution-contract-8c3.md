# T5 scheduled — Android Resolution integration boundary

- session_id: 20261105T2147Z-T5-scheduled-resolution-contract-8c3
- origin: scheduled
- resumed_from_sessions: 20261105T2045Z-T5-scheduled-ui-right-a71; 20261105T2055Z-T5-chat-obb-pair-9f2d; 20261105T2110Z-T5-chat-retain-delivery-a6f8
- base_sha: 188ad293b69ac8b3fc906130563dbdf3dbad325b
- work: prompt/coordination/work/DISPLAY-003/20261105T2147Z-T5-scheduled-resolution-contract-8c3.json
- hypothesis: existing Settings guard and dynamic resolution scale are separate owners; changing desktop resolution on Android would regress landscape, while disabling DynamicResolution blindly would be unsupported.
- published plan: 654fb2598bb03b74bbe34d7d44f94abcf3aa0998
- evidence document: docs/T5_RESOLUTION_ANDROID_POLICY_REVIEW_2026-11-05.md commit 50d588b245539066ef096280981b9e5427c11737
- findings: authenticated original GraphicsSettingsBox SHA e1854d74, SetResolution line565; DynamicResolution SHA69f9ab87, ResizeBuffers lines37/55. Existing Android Settings early-return is not a lower-resolution option. No explicit GraphicsSettingsBox DynamicResolution reference in prior bounded source scan CI41561621297. Right buttons already moved by prior scheduled T5; retained original delivery CI42110297871 SUCCESS, no duplicate 6GB download.
- limits: no original option-binding/persistence path examined; no production Settings edit, Unity build, new APK/OBB pair, device performance result or GPU metric. Owner-confirmed world/save/reopen remains true only for 42058825739. Water/FFT and visual effects unresolved; NOT_READY 0/3.
- next: source-authentic private managed CIL probe of existing GraphicsSettingsBox dropdown option binding and persistence; then narrow aspect-preserving Android render-scale change with executable tests. Keep T4 physical mouse and T1–T3 rendering untouched. No Action cancelled or dispatched.
- status: completed_source_analysis; DISPLAY-003 still open.
