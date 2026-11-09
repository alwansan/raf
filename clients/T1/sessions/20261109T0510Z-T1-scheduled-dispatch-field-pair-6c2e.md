# T1 scheduled session
session_id: 20261109T0510Z-T1-scheduled-dispatch-field-pair-6c2e
origin: scheduled
baseline_sha: 50faa92289c6a0c05ec0a3ddfcb440d675b05950
scope_commit: 38647277fa9ab1138e3905e38970d335706686e3
code_commit: 0ed7c1c1838a42587153b15c4d03c47c224a2662
test_commit: fe5946aa3d0b1c4b0548b0c956873135915614db
issue: WATER-001 OPEN / NOT_READY

## Evidence and result
Owner device 42058825739: entered, saved and re-entered world from artifact, not a water fix. Owner Nov 8 CL session LogRaft-20261108-164850-270: 74359 invalid water passes and 11165 invalid FFT compute kernels; mouse pointer motion improved but three clicks/scroll failed (T4 scope). These are counts, not first-pass numeric divergence. Existing sequence-only audit could accept a returned event for another kernel/shader/resource/group if it reused sequence. Added bounded identity comparison for shared fields, and rejects empty key/value. Four regression cases added; tests NOT EXECUTED because local container cannot resolve raw.githubusercontent.com (curl DNS error 6). No Unity/Android/GPU claim.

## Next
Run: cd scripts && python -m unittest -v test_t1_fft_dispatch_pair_identity; verify actual AndroidRuntimeLog field names; gather same-build before/returned trace and Vulkan/Unity matching captures to locate first numerical divergence. Revisit whether identity fields need names matching real logger. No duplicate Unity CI requested; T4 mouse and T5 Resolution untouched.
