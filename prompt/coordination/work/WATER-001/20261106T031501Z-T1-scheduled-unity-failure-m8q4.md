# T1 WATER-001 scope — 20261106T031501Z-T1-scheduled-unity-failure-m8q4
origin: scheduled
base_head: 2764e46f70db7a7894c97e3c09034f52a6e0d0f2
experiment_key: T1-FFT-UNITY-FAILURE-42152295025
files: prompt/coordination/work/WATER-001/20261106T031501Z-T1-scheduled-unity-failure-m8q4.md; prompt/coordination/clients/T1/sessions/20261106T031501Z-T1-scheduled-unity-failure-m8q4.md
hypothesis: corrected private Unity FFT replay failed during Unity import/dispatch, not at provenance validation; retrieve private GameCI failure and distinguish import, FindKernel, dispatch and GPU readback before another equivalent run.
shared_resource: none; no CI launch; no original assets or runtime changes.
taken_over_from: T1 chat 20261106T024340Z-T1-chat-84f0c6.md; scheduled 20261106T020900Z-T1-scheduled-trace-a7c2.md.
status: investigation / waiting for actionable private logs; no overlapping T1 shader rewrite.
Evidence: https://github.com/alwansan/raf/actions/runs/42152199100 validation failed; https://github.com/alwansan/raf/actions/runs/42152295025 validation advanced and Unity execute step failed.
Next: inspect exact private GameCI step logs and sidecar candidate hashes, then isolate Unity import vs kernel discovery vs dispatch vs readback. Do not re-run identical workflow blindly.
