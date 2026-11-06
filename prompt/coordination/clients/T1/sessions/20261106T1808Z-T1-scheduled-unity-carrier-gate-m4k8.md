# T1 scheduled — Unity FFT carrier experiment readiness checkpoint

- session_id: 20261106T1808Z-T1-scheduled-unity-carrier-gate-m4k8
- origin: scheduled
- baseline HEAD: ce9044546d19948c7c3e64c4ae811229c403955f
- scope registered commit: 9d7cea1a46284b75367e2b6b15ac4e55d54627b7
- issue: WATER-001 OPEN, full readiness NOT_READY 0/3.
- source owner ZIP2 pin: 15964ea8f246b6e076ce26b60931ee2e1a9a2385 (not downloaded this cycle).
- latest relevant T1 chat: 20261106T175623Z-T1-chat-float-carrier-context-b82c.

## Device-first evidence
Read docs/DEVICE_FEEDBACK_42058825739_AR.md: 42058825739/e9c358ed owner entered/saved/re-entered world from Artifact; release publication failed. CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57. 220911-559 reports 23884 water-pass and 3850 FFT-kernel errors; 230108-327 reports 39132 and 6026. Counts are symptoms, not a proof of the failing kernel. T4 owns physical mouse, T5 buttons/resolution. T1 vote remains لا يحتاج in trial-20261106-r1; no integrated phone-test-ready water fix.

## Distinguishing findings
Read actual source of the three previously committed T1FftCarrierContext files: 10 output categories, 5 Texture2D.Load paths, 64 threads, exact Unity2021.3.45f2 OpenGLCore assertions, bounded mismatch output. The test only hard-fails on positive controls 0/3/4, so the remaining categories must be inspected from the generated 10-line diagnostic artifact even on green NUnit. The workflow was not published in preceding chat session because connector security checks rejected workflow creation, not because GPU compilation failed. A source-only Python test cannot establish any runtime carrier behavior.

Prior actual synthetic Unity run 42129683073 measured 63/64 subnormal float-carrier mismatches but direct integer/normal controls zero. Later synthetic runs 42261467757 and 42264618337 found zero mismatches in different carrier contexts. Authentic paired Vulkan run 42254539826 matched 384 keyed reads for one pinned fixture, while authentic-derived Unity OpenGLCore run 42198180194 had 252/256 and 63/64 mismatches. Thus the first unresolved boundary is actual Unity shader variant/FindKernel/texture binding/dispatch and float-carrier lowering; no causal attribution to float carrier alone is justified.

## Action and limits
Registered distinct work before analysis. Verified the new source fixture and existing owner vote. No new shader patch, test execution, workflow dispatch, game asset write, release, or phone test in this cycle. Existing workflow publication was previously denied; repeating the same blocked request would not provide evidence. This is an evidence checkpoint only, not a successful engineering repair. No other worker file modified.

## Next executable action
With permitted workflow publishing, stage the existing sourcefree compute and NUnit test in licensed Unity2021 OpenGLCore private scratch and collect 10 mismatch counts. Validate output file exists even when NUnit passes, and correlate failures by category. Separately record original Unity ComputeShader GUID, true kernel name/FindKernel ID, resource binding dimensions and Dispatch, and capture keyed reads for the same authenticated original 1024x32 seed19 fixture. Compare first mismatching invocation, never infer Adreno/device water restoration from synthetic GPU results.