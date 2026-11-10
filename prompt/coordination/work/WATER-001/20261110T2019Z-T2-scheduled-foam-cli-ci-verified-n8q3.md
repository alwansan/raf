# 20261110T2019Z-T2-scheduled-foam-cli-ci-verified-n8q3 scope
owner: T2
origin: scheduled
base_sha: 16b3097b17800679e28540f696949a89b6fc1375
experiment_key: T2-FOAM-CLI-CI-PRODUCER-BOUNDARY-20261110
files: only this work file and matching T2 session; no game shaders or team-shared files
hypothesis: the new CLI gate has executed successfully but the production report publisher may bypass sanitizer
shared_resource: none; no CI dispatched
observed: Actions 42884997890 SUCCESS at SHA 849ee582; workflow explicitly says publisher_integration=UNKNOWN
next: locate report producer/upload boundary and introduce pre-upload fail-closed gate after confirming non-overlap
