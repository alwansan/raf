# T5 scheduled evidence checkpoint
session_id: 20261110T0352Z-T5-scheduled-safearea-a9c7
origin: scheduled
resumed_from_sessions: 20261109T1949Z-T5-scheduled-r4-review-e7b2.md; 20261109T1459Z-T5-scheduled-obb-pair-a7c2.md
base_sha: 49ea17a11cc855e8470271f1fc15716507c5ee3c
scope_commit: 0add0a457ce1c2d0820df5df70f4491bf9c8019c
source_blob_sha: e1c52ea2e5d37a36eceb68ced3ff430f64e27c08
origin_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; original phone run 42058825739, source e9c358eda01785b65e4eb14f18723da426635628

## New source-level observation
Read current AndroidTouchUiPanel.cs directly through GitHub connector and independently evaluated all three AddRightButton call-site patterns: Show Xbox at inset=8,y=78,width=150; Xbox layout at 8,126,150; Test report at 8,174,150. Each occurs exactly once. SafeRoot anchors use Screen.safeArea normalized to Screen.width/height, the right helper uses (1,1) and (-inset,-y), and all three original callbacks remain. HUD touch blocker occupies y=0..70; buttons start at y=78 and have 48-unit spacing and 42-unit height. Thus the current SOURCE already includes the owner's requested right-side move. Do not duplicate or reintroduce an alternate button menu. This is a source audit, NOT proof of appearance or touch interaction on POCO F5 Pro.

## Evidence boundaries
The owner demonstrated world entry, save and reload for artifact 42058825739 only. Its signed APK/OBB SHA pairing is not established by this audit. LogRaft 220911-559 reports 57 presented-FPS estimates mean 22.29 and minimum 3.02; HUD screenshot reads 18.27 FPS and p95 82.82ms. Do not equate these to GPU time or compare across unmatched scenes. Newer device results and Resolution callback/persistence are not device-confirmed here. T4 owns actual mouse capture and click/wheel.

## Next steps
Check current full Unity candidate against current source, obtain signed pair manifest and device-safe-area screenshot from SAME build; run existing tests/test_t5_right_safe_area_buttons.py on a complete checkout or CI before claiming source test PASS; compare settings resolution selection, rendering scale and persistence on device. No CI dispatched, no game asset touched, no other agents blocked. status=completed_source_audit; device_pending=true; game NOT_READY 0/3.
