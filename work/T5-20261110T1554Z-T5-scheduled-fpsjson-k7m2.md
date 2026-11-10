# T5 scope 20261110T1554Z-T5-scheduled-fpsjson-k7m2
origin=scheduled
baseline_sha=50b5424e44ba13cc79b6aa899f19d9e025d11cfb
experiment_key=T5-CL-FPS-JSON-DUPLICATE-KEY-GATE
scope=scripts/t5_cl_fps_cohort_gate.py JSONL ingestion only; new isolated tests; no T4 input/Unity/UI changes
hypothesis=Duplicate JSON keys can silently replace source/package/PID/fps metadata because json.loads accepts last duplicate. Reject duplicates before cohort classification.
shared_resource=none
owner_phone_baseline=42058825739 e9c358eda01785b65e4eb14f18723da426635628; world save/reload owner-confirmed; FPS 22.29 historical SurfaceFlinger estimate only.
plan=Add object_pairs_hook reject duplicate keys at any depth, regression test valid/duplicate; no Unity or full build.
status=IN_PROGRESS
