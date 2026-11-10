# 20261110T2210Z-T1-scheduled-kernel6-negative-context-c3e8
origin=scheduled
role=T1
issue=WATER-001 OPEN NOT_READY 0/3
baseline=9ac20bf03b827f175f8d48b15097a0e371fc6b5f
latest_head_checked=df0d0d8bdc7dc71e7e8b4ff06563c92c387b3524
work=prompt/coordination/T_TEAM/work/20261110T2210Z-T1-scheduled-kernel6-negative-context-c3e8.md
scope_commit=6295d6f4996b4cd133f4c4eab764b48476c55c6c
source_commit=bbf67be8ff01a40977aee87e045f5196728239ca
test_commit=df0d0d8bdc7dc71e7e8b4ff06563c92c387b3524
owner_feedback=docs/DEVICE_FEEDBACK_42058825739_AR.md; 42058825739 Artifact world/save/reentry succeeded, release publishing failed; supersedes APK86.
result=Fixed same-line kernel6 error detection for 'not found', 'cannot find', 'could not find', and 'missing'. This prevents negative lookup events from being silently excluded by --errors-only. Added isolated synthetic regression asserting three negative and two benign lines.
verification=Regex smoke check executed locally for positive and negative strings; repository unittest newly committed but not run in this session. No device GPU/Unity test and no CI dispatched.
limits=No evidence that runtime kernel index6 maps to original FFT slot6, original GUID, FindKernel or Dispatch; no original shader recovery, no numeric Vulkan/Unity comparison. No edits to T4 physical mouse or T5 Resolution/three buttons.
next=Run python -m unittest tests.test_t1_kernel6_negative_context at commit df0d0d8bdc7dc71e7e8b4ff06563c92c387b3524 or descendant, then process pinned CL log per epoch and correlate original compute GUID/FindKernel/Dispatch before first-pass numeric comparison. Recheck HEAD and ongoing CI first.
