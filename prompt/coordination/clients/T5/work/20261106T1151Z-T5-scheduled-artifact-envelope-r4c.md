# T5 independent scope — artifact envelope provenance
session_id: 20261106T1151Z-T5-scheduled-artifact-envelope-r4c
origin: scheduled
issue_id: DELIVERY-014
status: active
baseline_sha: c2863950848a470aae5d6795a13740c586f554ff
resumed_from_sessions: 20261106T1046Z-T5-scheduled-pair-success-q6f8.md; 20261106T1130Z-T5-chat-applycallers-c6e1.md
intended_files: this unique work file; unique clients/T5/sessions/20261106T1151Z-T5-scheduled-artifact-envelope-r4c.md
hypothesis: signed checkpoint and delivery artifact envelopes remain available with distinct digest and sizes, despite publish failure. Their ZIP archive digests must NOT be confused with APK/OBB payload digests.
experiment_key: T5-42058825739-artifact-envelope-metadata-20261106-v1
resource_key: read-only Actions 42058825739 artifact metadata; no Unity, no binary download, no shared runner
coordination: chat T5 owns Resolution original IL, T4 owns mouse, T1 FFT, T2 water, T3 rendering. No overlap; no CI dispatch.
next: inspect actual archived payloads/manifest in authorized isolated environment and run signed-pair validator; record hashes only.
