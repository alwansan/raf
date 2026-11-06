# T1 scheduled checkpoint — 20261106T051300Z-T1-scheduled-nunit-suite-c8e1
origin: scheduled
issue_id: WATER-001
resumed_from_sessions: 20261106T041100Z-T1-scheduled-gate-f9c2.md; 20261106T024340Z-T1-chat-84f0c6.md
base_sha: f9d54ab4c3b0b00de4fa999f46edd614b130e49f
scope_commit: 54f4952eacb9fbe06093da9f2ffcb55fe5bd57fb
source_commit: 348668d609ff82a6cdb2f6e41ddef1efcfce2de0
regression_commit: e88c739225da06d585d8545821aa79514594be9b
origin_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; owner run 42058825739 proves world/save/reopen for artifact only; CL 220911 pass 23884/kernel 3850 and 230108 pass 39132/kernel 6026. Kernel index 6 is not identified.
new_live_evidence: T1 private Unity original-derived FFT run 42160755558 completed success (GitHub run and job conclusion). This is workflow success, not yet independently verified numeric parity or Adreno water proof. Earlier Unity failures 42152199100 and 42152295025 are historical and should not override this newer run.
engineering: source NUnit gate now rejects nested failure/reason nodes anywhere in report and failed test-suite nodes even when root and both expected cases claim Passed. Added synthetic adversarial regression. Avoids false-positive source authenticity/Dispatch classification on contradictory NUnit tree. Tests NOT executed in repository due container GitHub DNS resolution failure; no new CI run, phone test, original pixel parity or FindKernel mapping asserted.
next_step: run python3 -m unittest tests.test_t1_fft_unity_gpu_result_gate on actual repository; inspect private 42160755558 redacted gate output and manifest, then capture first original FFT pass divergence Unity vs Vulkan and bind verified kernel identity/dispatch. Preserve T4 mouse and T5 resolution/button scope.
status: completed source guard only; WATER-001 OPEN; NOT_READY 0/3.
