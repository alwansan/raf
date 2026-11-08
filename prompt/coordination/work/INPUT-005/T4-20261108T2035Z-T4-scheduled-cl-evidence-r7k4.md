# INPUT-005 T4 scope 20261108T2035Z-T4-scheduled-cl-evidence-r7k4
baseline_sha: 28024e36a57c053a79699c90c34c871ce373a40f
hypothesis: shared pack T4 NEEDS_INPUT indicates missing physical interaction evidence, not nine failures.
input: CL main/test/shared-20261108-230157-466487336/summary-20261108-230157-466487336.json and CL main/test/t4-builtin-mouse-20261108-191456-452866288/events-20261108-191456-452866288.jsonl
files: unique T4 session + this note; no shared code; resource none
experiment_key: T4-CL-SHARED-20261108-230157
result: 9/9 T4 statuses NEEDS_INPUT; no observed mouse route evidence in earlier T4 JSONL.
next: acquire actual mouse button/scroll/capture events from unified mini lab, then test Unity bridge; do not duplicate CI.
