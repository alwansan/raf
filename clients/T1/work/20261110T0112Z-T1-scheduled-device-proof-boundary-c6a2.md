# T1 scoped audit 20261110T0112Z-T1-scheduled-device-proof-boundary-c6a2
origin: scheduled
baseline_sha: e6a3fbd8395f09aad0fefef88b783de052e0951d
issue: WATER-001 OPEN / NOT_READY 0/3
scope: evidence boundary between synthetic Android FFT and original Raft Unity FFT; no shared source modifications.
files: clients/T1/work/20261110T0112Z-T1-scheduled-device-proof-boundary-c6a2.md; clients/T1/sessions/20261110T0112Z-T1-scheduled-device-proof-boundary-c6a2.md
hypothesis: successful Android synthetic SSBO FFT readback does not imply original shader GUID / FindKernel / Dispatch binding.
experiment_key: T1-FFT-ORIGINAL-BINDING-GATE-20261110
shared_resource: none; no CI or build requested.
owner_baseline: 42058825739 source e9c358eda01785b65e4eb14f18723da426635628, phone world enter/save/reenter PASS, package publishing FAIL.
new evidence: shared mini T1-05 owner Android15 Adreno730 512-local synthetic SSBO 1024 floats maxabs 2.3841858E-7 <=3E-5, GL0, unmap true; pinned CL 1dc0bf53303c1486afdb5a812d8597d682292589/test/shared-20261109-225506-552476830; source CI 42690809051 success. This validates synthetic GPU probe ONLY.
source-only gates: 42723946943 and 42723947211 success at fb0bfea9; full native Unity and original GPU proof remain unverified.
next: original verified FFT shader asset GUID and original FindKernel callsite; kernel index, bindings and thread groups, same-session per-pass GPU readback; compare first divergent Vulkan vs Unity pass. Do not repeat Mini build.
