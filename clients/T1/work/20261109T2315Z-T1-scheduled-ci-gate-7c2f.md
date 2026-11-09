# T1 independent scope — 20261109T2315Z-T1-scheduled-ci-gate-7c2f
session_id: 20261109T2315Z-T1-scheduled-ci-gate-7c2f
origin: scheduled
baseline_sha: 668a19e82658bdb4676c3f9cc2bc177c513544d8
issue: WATER-001 / original FFT verification unblock
files: clients/T1/work/20261109T2315Z-T1-scheduled-ci-gate-7c2f.md; clients/T1/sessions/20261109T2315Z-T1-scheduled-ci-gate-7c2f.md
experiment_key: t1-fft-native-gate-42715257589-42715257606
shared_resource: none; no Unity build, no APK, no competing CI.
hypothesis: The new T5 source parity failure and offline integration failure are separate failed gates, so neither supplies original FFT GPU execution evidence.
evidence: 42715257589 failed at "Verify exact source-to-final-candidate byte parity and tamper negatives"; 42715257606 failed at "Validate adapters and privately recover original source". Earlier 42696228231 failed before Unity during reconstruct/staging. These are stage names, not verified root causes.
owner_baseline: device run 42058825739 entered/saved/reentered world from Artifact; 220911-559 water passes 23884 / FFT kernel 3850, 230108-327 water passes 39132 / FFT kernel 6026, from 5 Nov CL snapshot. Do not combine epochs. Physical mouse/click and Resolution owned by T4/T5.
source_provenance: original FindKernel-to-resource mapping unverified; Vulkan-vs-Unity numeric first divergent pass unverified; original GPU readback unverified.
decision: do not launch redundant CI, do not modify T5 staging or T4 mouse. Await exact T5 parity diff and source recovery; use a single immutable candidate SHA and per-session trace before interpreting any FFT pair audit as runtime proof.
next: obtain verified original compute shader asset GUID/kernel name and runtime FindKernel/Dispatch binding from reconstructed source; record buffer dimensions, thread-group sizes, stage inputs and GPU readback. Then compare first-pass outputs against pinned Vulkan reference with tolerance and provenance.
status: blocked_on_native_candidate; WATER-001 OPEN NOT_READY 0/3.
