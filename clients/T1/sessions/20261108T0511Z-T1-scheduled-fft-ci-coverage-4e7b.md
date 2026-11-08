# T1 — 20261108T0511Z-T1-scheduled-fft-ci-coverage-4e7b
origin: scheduled
resumed_from: clients/T1/sessions/20261108T0411Z-T1-scheduled-fft-nul-guard-8d2f.md
base_sha: 2ed6b7d00ea11cb00f4ea8104b0cdfc12590362b
scope_commit: 7d4769193418993be8bc9bbcb23c6521bdc7c25e
code_commit: c1ede193453a8d951ba29cff7f2a48ba2e9f59b8
work: work/experiments/20261108T0511Z-T1-scheduled-fft-ci-coverage-4e7b.md
issue: WATER-001 (OPEN)

## Owner and CL evidence
Run 42058825739 artifact: owner entered world, saved, exited, and re-entered; release publishing failed. Source e9c358eda01785b65e4eb14f18723da426635628. CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57. Water pass / kernel errors: 220911-559 23,884 / 3,850; 230108-327 39,132 / 6,026. These counts do not prove index 6 maps to FFT. No new phone tests.

## Finding and engineering change
Existing T1 paired diagnostic workflow run 42445720118 completed successfully on 9a85ea92, but its YAML did not execute three recently added test modules: capture budget, NUL path, and dispatch coverage. Updated its existing sparse-checkout workflow paths and test step to execute scripts.test_t1_fft_capture_budget, scripts.test_t1_fft_capture_path_nul, scripts.test_t1_fft_dispatch_coverage on each relevant change. This is targeted source-only CI, not a Unity build. Did not duplicate an existing workflow dispatch.

## Verification limits and next
GitHub connector confirmed updated workflow blob 21d7ab134e03e90ff580fc94d94e058b16da2334. At immediate post-commit read, new workflow run was not yet listed; mark waiting_ci, do not claim tests passed. Next cycle inspect new run at commit c1ede193, read failed job logs if any, fix actual failures; then proceed to original ComputeShader GUID/kernel name and matched Vulkan/Unity capture. T4 mouse and T5 Resolution/buttons scopes untouched. NOT_READY 0/3, trial vote unchanged.
