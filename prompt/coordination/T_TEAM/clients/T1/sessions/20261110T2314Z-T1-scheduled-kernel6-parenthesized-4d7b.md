# 20261110T2314Z-T1-scheduled-kernel6-parenthesized-4d7b
origin=scheduled
role=T1
issue=WATER-001 OPEN NOT_READY 0/3
owner_feedback=docs/DEVICE_FEEDBACK_42058825739_AR.md; owner world save and re-entry from artifact 42058825739 confirmed, release publication failed. APK86 historical only.
baseline_head=475a748870d7af906445945e16667a3b2352764a
work=prompt/coordination/T_TEAM/work/20261110T2314Z-T1-scheduled-kernel6-parenthesized-4d7b.md
scope_commit=19608329c3def6f0be854215641bbd87a421fe22
source_commit=f048563edf22701684332bcb2e67e949d63f2af2
test_commit=cee85c0b190435261195456919ba5a27b5ef7736
work_result_commit=a8e2271ec58dcef115c255fe2069adcf3f8e0eab
result=Extended kernel6 parser to recognize 'kernel index (6)' and 'kernel #6' while rejecting kernel 16 and 60. Added synthetic unittest, preserving existing scan schema, errors-only classification and no raw log output.
verification=Standalone Python regex smoke passed all 5 variants; repository unittest not executed because GitHub DNS unavailable to local runtime. No real CL log processed in this session; no device, Unity, GPU, XAPK or CI launched.
context=HEAD 475a748870d7af906445945e16667a3b2352764a on opening; recent compatibility run 42916987688 succeeded (not GPU validation). Read latest T1 20261110T2210Z negative-context session and 20261110T0209Z first-mismatch session. T4 mouse and T5 three controls/Resolution untouched.
limits=Kernel index6 is not proven to be FFT program slot6. Original compute GUID, FindKernel mapping, Dispatch bindings and Vulkan/Unity first numeric mismatch remain unknown. Counts from owner CL 220911-559: water 23884 kernel 3850; 230108-327: water 39132 kernel 6026, separate sessions.
next=Execute python -m unittest tests.test_t1_kernel6_parenthesized, apply scan to pinned CL logs independently, inspect first real kernel error and derive GUID/FindKernel/Dispatch from original assets before numeric FFT comparison. Check latest HEAD and team overlap first.
