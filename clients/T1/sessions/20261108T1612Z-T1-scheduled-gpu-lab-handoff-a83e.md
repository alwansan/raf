# T1 WATER-001 — GPU mini-lab handoff and CI verification

session_id: 20261108T1612Z-T1-scheduled-gpu-lab-handoff-a83e
origin: scheduled
base_sha: 2361fb998c03d4d88910a308ed102f223db9ae3d
resumed_from: clients/T1/sessions/20261108T1538Z-T1-chat-gles31-probe-7e4a.md; clients/T1/sessions/20261108T1506Z-T1-scheduled-trace-ci-8f2c.md
issue_id: WATER-001
experiment_key: t1-gles31-ssbo-v0.1.1-37182f0e-device-pending
status: waiting_device

## Independently verified in this cycle
- Owner Nov 5 report docs/DEVICE_FEEDBACK_42058825739_AR.md: world entry/save/exit/reentry worked from run 42058825739 Artifact; packaging release failed. This supersedes historical APK86 failure, not evidence for latest HEAD.
- Owner Nov 8 report apk-for-testing/OWNER_FEEDBACK_2026-11-08_AR.md: latest CL session LogRaft-20261108-164850-270 counts 11165 FFT invalid kernel, 74359 water invalid pass, 7372 cursor warnings. Mouse movement improved but clicks/wheel fail (T4 scope).
- T1 paired source tests run https://github.com/alwansan/raf/actions/runs/42493143730 completed SUCCESS on 11b69e69cc31608316949e30e76b32877c130ffd. Earlier waiting_ci resolved; do not rerun identical job.
- T1 GLES3.1 mini-lab https://github.com/alwansan/raf/actions/runs/42497767712 completed SUCCESS, source 37182f0e9d38c0c38f3e78e7e5c21463eeaac8d9; APK Artifact 13624141881, SHA256 d177634c7ee7d71117005000fa904db03e825a43ba63dbe921ddf43cc077d0b7, versionCode 2, package com.alwansan.raft.lab.t1. Tests T1-01..04 are BUILT but no observed owner GPU results yet. No additional equivalent CI launched.
- Current HEAD 2361fb998c03d4d88910a308ed102f223db9ae3d contains latest T1 chat memory; do not modify shared TEST_CENTER or lab host without new device evidence. T4 owns physical mouse, T5 owns resolution/three UI controls.

## Evidence boundary and next decisive work
Generic GLES3.1 compute capability does not identify original Unity kernel index 6, imported GUID or water material pass. First obtain real phone results T1-01..04 and exported JSONL, then isolate authentic Unity ComputeShader GUID -> FindKernel name/index -> Dispatch groups -> SSBO/output readback, with first divergent FFT pass compared to pinned Vulkan reference. Preserve original resources and do not publish proprietary shaders. Until that evidence exists WATER-001 remains OPEN, NOT_READY 0/3. No new full-game Unity build, no phone claim, no resource modification in this cycle.
