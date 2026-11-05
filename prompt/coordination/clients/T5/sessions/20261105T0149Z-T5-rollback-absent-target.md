# T5 session 20261105T0149Z-T5-rollback-absent-target

Identity T5; resumed_from_session=20261105T0046Z-T5-rename-failure-review; prior status paused_ci_pending, no confirmed simultaneous T5 session in fetched state. Baseline previous code 46adaa1d7f7cbc2b8a104630a307aa36819600cf; new HEAD must be rechecked before writes.

CI41943856117 job immutable-original-owner completed SUCCESS (all steps including synthetic controls and three authentic SHA-pinned ZIP2 owner hydration). This run predates the newest regression test commit 46adaa1, therefore it does NOT validate that test. Source-only; no Unity/device proof.

Plan: add distinct negative regression for second publication failure when first target was initially absent; verify cleanup removes newly created first target and second pointer is preserved, with no temporary files. Keep production code unchanged until failure is demonstrated. Trigger isolated T5 path workflow, then record result. Do not touch T1–T4, legacy, audio, Settings, touch, Unity builds.
