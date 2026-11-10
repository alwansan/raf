# T1 independent scope — 20261110T1710Z-T1-scheduled-kernel6-context-5d8a
origin=scheduled
baseline_sha=fd8a4ef2f79bf04e083da6163bdfaebff2869306
issue=WATER-001
experiment_key=T1-KERNEL6-RAW-CONTEXT-20261110
files=scripts/t1_kernel6_log_context.py; clients/T1/work/20261110T1710Z-T1-scheduled-kernel6-context-5d8a.md; clients/T1/sessions/20261110T1710Z-T1-scheduled-kernel6-context-5d8a.md
hypothesis=Kernel index 6 flood is not proof of original FFT kernel identity. A bounded raw-log context extractor can preserve original adjacent FindKernel/Dispatch lines and avoid conflating separate sessions.
shared_resources=none; CPU-only; no CI/Unity.
owner_evidence=42058825739 phone world save/reentry; CL 220911-559 23884 pass/3850 kernel, 230108-327 39132 pass/6026 kernel; 8-Nov session 74359 pass/11165 kernel; do not sum across sessions.
scope=read-only raw text log extraction with bounded output and explicit source/session identifiers; no T4/T5 edits; no raw game assets published.
