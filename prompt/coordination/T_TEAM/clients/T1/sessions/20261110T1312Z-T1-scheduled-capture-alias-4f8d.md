# 20261110T1312Z-T1-scheduled-capture-alias-4f8d
origin=scheduled
role=T1
issue=WATER-001 OPEN NOT_READY
baseline=9dd04b325b32e84ba470ee0382099171c0a99307
current_head_at_closure=595a3639c6288a9684af78250a756f830a963bdb
work=prompt/coordination/T_TEAM/work/20261110T1312Z-T1-scheduled-capture-alias-4f8d.md
scope_commit=ad2296d512192b208d50f1a4edfd21dd3e29fd21
implementation_commit=33ab7444820f1a2a26331a986db3fed355ae8bd4
test_commits=a35d567fce78d0215b4d5cb61fe0698e56fc78d2,595a3639c6288a9684af78250a756f830a963bdb
experiment=T1-FFT-CAPTURE-ALIAS-20261110
result=Capture integrity verifier now rejects repeated (st_dev,st_ino) across Vulkan/Unity or passes, preventing same file or hardlink from impersonating independent readbacks. Added 3 synthetic regression cases: distinct file accepted without GPU proof, same path rejected, hardlink rejected (skipped if unsupported).
tests=NOT_RUN; environment cannot reach raw.githubusercontent.com to materialize repository files; do not claim CI pass.
owner_device=42058825739 world/save/reentry from Artifact confirmed; packaging publication failed. Log 220911-559 water-pass=23884 kernel=3850; 230108-327 water-pass=39132 kernel=6026; separate sessions.
limitations=Source-level metadata gate only. Identical pixel contents from independent files remain allowed; no GPU execution or original FindKernel/Dispatch proof. No original FFT GUID or same-build Vulkan/Unity numeric capture acquired. No mouse/Resolution changes (T4/T5 ownership).
next=Run python -m unittest tests.test_t1_fft_capture_alias on SHA >=595a3639; inspect for false positives; obtain original FFT GUID/kernel binding and paired private GPU readbacks from same build to locate first numeric divergence. Keep WATER-001 OPEN.
