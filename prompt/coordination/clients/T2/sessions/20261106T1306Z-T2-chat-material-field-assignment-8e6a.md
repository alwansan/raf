# T2 — Chat: original Foam Material receiver field assignment provenance

- session_id: `20261106T1306Z-T2-chat-material-field-assignment-8e6a`, origin: `chat`, status: `active`
- base_sha: `33c72f721c5aab7fd2b6cfafaabdbf224f96f2ef`
- reservation: [work](../../../work/WATER-001/T2-20261106T1306Z-T2-chat-material-field-assignment-8e6a.json), commit `5779263f385b1c37117281b51b643a6af2e4873f`.
- resumed_from_sessions: `20261106T1250Z-T2-chat-CB0-fieldwriters-materialprefix-7b2e`; `20261106T122027Z-T2-scheduled-ci-reconcile-a7c2`.
- baseline original SHA-pinned [CI42220621927](https://github.com/alwansan/raf/actions/runs/42220621927) SUCCESS: one exact CB0 name first string formal to Material.SetVector; exactly three float original fields from one class feed original 4-float Vector4 ctor; three writes in one compiled original managed method; guarded preceding Material typed ldfld receiver.
- issue WATER-001 OPEN, neither Material.shader Foam identity nor full 160B CB0 Unity upload nor Android water rendering known. T1 FFT independent CI 42221700354 was in_progress at scope registration. No overlap with T1 or T5 assets or builds.
- hypothesis: identify and count source-authentic *same* `UnityEngine.Material` receiving field's compiled `stfld` writer sites, declaring-type relationship to three float fields and typed Material creation/Shader selection APIs in original writer methods, keeping any co-occurrence distinct from exact operand dataflow. Negative controls must fail closed for wrong receiver, branch into literal and non-Material fields.
- intended files: T2-owned `android-port/Experiments/T2/FoamCb0ManagedLiterals/Program.cs`, isolated T2 workflow, this session, scoped work, aggregate-only report/experiment/event.
- status: no source patches or new CI result claimed at initial checkpoint.
- next_step: implement and run source-authentic safe typed Material field assignment/producer census; stop at honest unknown if original managed reflection lacks a definitive shader association.
