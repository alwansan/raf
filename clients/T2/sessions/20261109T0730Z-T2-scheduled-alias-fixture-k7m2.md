# T2 scheduled — conservative Foam alias fixture
session_id: 20261109T0730Z-T2-scheduled-alias-fixture-k7m2
origin: scheduled
branch: feature/android-native-port
baseline_sha: 3160a7a8ccd6b3d8b0dda55d9aba23242c437f09
resumed_from: clients/T2/sessions/20261109T0620Z-T2-scheduled-return-join-a91c.md; clients/T2/sessions/20261109T0212Z-T2-chat-return-value-flow-n7x3.md
work: work/experiments/20261109T0730Z-T2-scheduled-alias-fixture-k7m2.md
issue_id: WATER-001 OPEN; game NOT_READY

Owner phone evidence read: docs/DEVICE_FEEDBACK_42058825739_AR.md, artifact 42058825739 world enter/save/re-enter confirmed, water/FFT errors remain. Newer 8 Nov shared mini-lab policy in AGENTS/PROMPT applies. T4 owns physical mouse; T5 owns Resolution; no changes to those files. T3 effects scope untouched.

Published work reservation at 918ef428dc2f94d2be57d6a9babcce07e24b9f9f. Added source-free Python regression reference in android-port/Experiments/T2/alias_identity_reference_test.py at cc85cb65fb777419dcbb2a177a9cb27671bc80e1. Eight isolated unit tests pass locally using python unittest. The oracle intentionally rejects field-token/receiver equality alone as object identity; even distinct fields/receivers may alias. A proven immutable allocation identity is needed; CFG joins with disagreeing/unknown paths become UNKNOWN. This corrects a dangerous false proof possible in the planned CIL analysis.

This is synthetic reference only: no original CIL scanned in this cycle, no ShaderLab changes, no GPU/device or Unity test, no APK, no CI dispatch, no CL writes. Original Foam pass1 remains value_mixed_or_joined and no pass0/pass1 texture object alias is established. Next: implement receiver/object allocation identity tracking in the T2 Mono.Cecil scanner, add these fixtures as C# regression tests, run SHA-pinned original private scan with fail-closed branches, then bind verified Foam/Spectrum/Blur resources and CB0 before ShaderLab integration.
