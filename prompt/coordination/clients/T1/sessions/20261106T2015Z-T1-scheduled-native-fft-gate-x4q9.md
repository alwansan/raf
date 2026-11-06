# T1 scheduled — native Unity import gate versus FFT evidence

- session_id: `20261106T2015Z-T1-scheduled-native-fft-gate-x4q9`
- origin: `scheduled`
- issue: WATER-001 OPEN; NOT_READY 0/3; T1 trial vote remains «لا يحتاج».
- baseline HEAD: `b89242e9d984eb1f43fd1eb7426a1c2ecb101040`
- work scope reserved: [independent work](../../../../work/WATER-001/20261106T2015Z-T1-scheduled-native-fft-gate-x4q9.json), commit `fb24b29e444c47b2795963c9e55bc2ea0e0e910e`.
- resumed: `20261106T195959Z-T1-chat-ci-log-pin-7b42` and `20261106T1907Z-T1-scheduled-report-shape-n8v2`.

## Owner device evidence first

[Owner 5 Nov phone report](../../../../../docs/DEVICE_FEEDBACK_42058825739_AR.md): run 42058825739 / immutable e9c358eda01785b65e4eb14f18723da426635628; world enter/save/reenter confirmed by owner, packaging publish failed. CL fixed 520c4cf: session 220911-559 water pass 23,884 / FFT kernel 3,850; session 230108-327 pass 39,132 / kernel 6,026. Device FPS/HUD not GPU-time proof. This supersedes APK86 historical local-world failure; no new device run here.

## Live evidence and decision

- [T1 paired-capture source controls 42285338050](https://github.com/alwansan/raf/actions/runs/42285338050): completed success at `ccb013e1b1e7dafbe6c4cd9a64b9576c373e01b2`, updated 2026-11-06T20:05:43Z. This is source-only, not original-vs-Unity real invocation capture.
- [T1 CI historical log provenance 42285401655](https://github.com/alwansan/raf/actions/runs/42285401655): completed success at `47df6c4b344a688928219596cae66ef865108050`, updated 20:06:10Z. Prior T1 chat established 12/12 verifier tests and authenticated three historical job markers, **not** runtime numerical parity.
- **New consequential live change:** [owner-direct native run 42281310905](https://github.com/alwansan/raf/actions/runs/42281310905) at immutable `d692400115c36c4839fa4f4954e5f6ed1c60d413` is now **completed failure** (20:09:08Z). Jobs `native-request-gate` and `unity-license-preflight` succeeded; `reconstruct` failed specifically in step **Unity Editor 2021.3.45f2 Android import and compile**; `delivery-result` failed downstream and `publish-early-test` skipped. This is not a new FFT runtime failure: the build never reached confirmed device FFT binding.
- T3 original Shader48 job 42286299737 was in_progress on initial branch read. Do not cancel or compete. T4 is actively tracking original Save and first native compile failure (HEAD `b89242e9`); do not edit their compile/runtime files. T5 owns delivery/packaging. No new native or duplicate source workflow launched.
- Current evidence **does not** prove authored FFT compute kernels, correct `FindKernel` names, resource IDs or `Dispatch` dimensions in the game; Vulkan numeric parity on one profile does not establish Unity/Adreno parity. No raw proprietary shaders/assets copied.

## Precise unblock

1. Recheck live head and T4/T5 native compile repair; read actual failing Unity Editor log rather than infer shader cause from generic job step. A compile failure is upstream of any meaningful FFT runtime comparison.
2. After compile is fixed and an isolated authorized Unity test is available, record actual imported ComputeShader GUID, kernel names/index returned by `FindKernel`, group sizes, source input texture bindings and variant, dispatch dimensions, and output SHA; require the same original ZIP2-pinned input/variant and keyed invocation records before applying ULP comparator.
3. If another T1 chat session owns same Unity binding files, take complementary evidence-only capture or independent input fingerprint, not a conflicting edit. Preserve Settings/audio/left touch and the current phone-proven world save behavior.

**Result:** confirmed a fresh, specific upstream blocker from live Actions, and preserved an independent nonoverlapping continuation. No source fix, new GPU test, or phone water repair is claimed. WATER-001 OPEN; NOT_READY 0/3; no trial vote change.
