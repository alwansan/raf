# T1 → T5: shared Mini test T1-05 integration/build review (do not duplicate)
session_id: 20261109T1915Z-T1-chat-mini-butterfly-a9f3
origin: chat
issue_id: WATER-001
base_sha: 90547ec2d38d9e1255ceb89da313f7151064c0a9
status: intended_scope
To: T5 owner of one unified Mini APK, pack build request and release.
Context: owner authorized using existing simplified portrait Arabic Mini app to diagnose GPU on Adreno 730 and asked for verified APK link when rebuilt. CL/test latest shared v0.2.13 T1-01..04 four fresh PASS; does not prove original FFT.
Proposal: insert ONE built-in data-only test T1-05 through existing t1_compute driver, no extra APK or dynamic GLSL from JSON. On-device GLES3.1 two-pass 512-local-invocation SSBO complex butterfly with independent bounded CPU float reference, numeric max error + gl_error + shader compile errors. Strict safety: no original game shaders/meshes/bytecode, no game source changed, do not call it authentic FFT.
T1 owns T1ComputeProbe and its testpack case; coordination needed for tiny T1-only route in T5 UnifiedLabActivity and ArabicLabStrings. Do not separately change T1 routing until T1 source patch and CI reviewed. Once completed, T1 updates ONLY its shared_round_id r4 vote to NEED_BUILD, and you decide one Mini APK request after reviewing actual changes, runner, CL, and signer; XAPK full vote independent. In next authorized Raft XAPK, preserve T1 original 16-call log hooks for actual Unity binding investigation; no urgent full build merely for this synthetic Mini test.
