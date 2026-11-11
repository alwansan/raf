# T1 scheduled session 20261111T2205Z-T1-scheduled-fft-ci-triage-4d8c

origin: scheduled
issue: WATER-001 / NOT_READY 0/3
baseline_sha: 9f8e1e01f5b7e73fed172541a6dbe371ee91a82f
scope: work/T1-20261111T2205Z-T1-scheduled-fft-ci-failure-4d8c.md

## Owner baseline
Read docs/DEVICE_FEEDBACK_42058825739_AR.md. Run 42058825739 artifact enters/saves/reopens world; package publication failed. CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57: water pass and FFT kernelIndex 6 errors persist. Do not regress to APK86 diagnosis. Newer owner 8 November unified mini-lab and physical mouse observations are also documented in AGENTS/CURRENT_OWNER_REQUIREMENTS; T4/T5 own those non-FFT files.

## Work completed
Read live instructions, owner report, FFT comparator, tests, diagnostic workflow, branch HEAD, and Actions. Detected latest paired FFT workflow run 43101033840 at source fcb0c5c: FAILURE in verify step; checkout PASS, no artifacts. Recorded independently scoped investigation rather than launching duplicate workflow. The exact failed assertion is unknown because step metadata is not stdout. No source fix or numeric Vulkan-vs-Unity proof claimed.

## Evidence and next
https://github.com/alwansan/raf/actions/runs/43101033840/job/130792235243
https://github.com/alwansan/raf/blob/feature/android-native-port/work/T1-20261111T2205Z-T1-scheduled-fft-ci-failure-4d8c.md
Next: retrieve actual job log, isolate failing command, reproduce at fcb0c5c, repair source/tests, validate. Then establish authentic `.compute`/`.meta`/GUID and Unity `FindKernel`/`Dispatch` identity; no fabricated GPU/device parity. No Unity or APK build triggered, no other clients' scopes edited.
