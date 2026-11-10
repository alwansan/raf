# 20261110T0712Z-T1-scheduled-fft-terminal-contract-f2a9
origin=scheduled
role=T1
issue=WATER-001 OPEN NOT_READY
baseline=755da1cbf69f5c6b21d342e6ae49689b9571da3a
scope_commit=ae29d3bf583b2fff9e463ad10ae3bb0a91a336c1
implementation_commit=57a2d8850dc32e7e053246926ad4a71478598030
work=prompt/coordination/T_TEAM/work/20261110T0712Z-T1-scheduled-fft-terminal-contract-f2a9.md
experiment=T1-FFT-TERMINAL-CONTRACT-20261110
owner_device=42058825739; world/save/reentry from Artifact confirmed; release publication failed; water and kernel faults remain.
log_evidence=220911-559: 23884 water-pass and 3850 FFT-kernel errors; 230108-327: 39132 and 6026 respectively; separate sessions, no unique-failure inference.
result=Added three regression tests to tests/test_t1_fft_native_trace_contract.py for synchronous throw, return-then-throw, and throw-then-return. They assert paired_count=0 for terminal failures and contradictory events. These are source-level tests, not GPU proof.
ci=latest relevant T1 run 42747722414 succeeded on older 4c50a7b; does NOT include new tests. No equivalent CI re-run launched.
limitations=Tests newly committed but not executed in this session. No authentic resource GUID/FindKernel/Dispatch mapping, Vulkan/Unity same-pass numeric readbacks or device water fix proven. No shader or APK edits.
coordination=T4 physical mouse; T5 Resolution and three UI buttons, packaging; unchanged.
next=Execute python -m unittest tests.test_t1_fft_native_trace_contract on commit 57a2d885 or descendant; investigate failures. Then obtain authentic FFT asset GUID and original runtime kernel binding, compare first differing pass with same-build GPU traces. Keep WATER-001 OPEN.
