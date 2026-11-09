# T1 scheduled session 20261109T0718Z-T1-scheduled-pair-presence-b8e4
origin=scheduled
status=source_fixed_tests_pending
baseline_sha=5c644c14eaae1baeebe4020722b1d1d577fa2ff0
scope_file=clients/T1/work/20261109T0718Z-T1-scheduled-pair-presence-b8e4.md

## Evidence
Owner phone 42058825739: world entry/save/re-entry successful from artifact; packaging publish failed. Water/FFT errors remain. Prior pair audit compared only identity fields present on BOTH sides, so one-sided omitted fields could pair silently. This is a trace-integrity issue, not proof of FFT kernel correctness.

## Work completed
- Commit fea0071fd1ea7fab5915b500e0c1bef4549cd59b: separate scope.
- Commit 821ad7e36e72d12c4fa4425633819ce191a1ba61: detect identity key presence mismatch in scripts/t1_fft_dispatch_pair_audit.py.
- Commit 92c8e4fce837cee4a286a6370b11922fa947f38f: four isolated regressions in tests/test_t1_fft_pair_presence_b8e4.py.
- Last known runtime evidence workflow 42571153053 success for DIFFERENT source (ae3477e); does not test this change.

## Validation and limits
Local test execution blocked: curl DNS resolution of raw.githubusercontent.com failed. Tests authored but NOT executed. No CI or Unity build launched; no phone or Vulkan/Unity numeric comparison performed. Script still accepts sequence-only trace but correctly does not claim runtime identity or GPU proof. Next: run python3 -m unittest discover -s tests -p 'test_t1_fft_pair_presence_b8e4.py' -v on a working runner, verify actual Android JSONL keys, then correlate first divergent FFT pass with original shader GUID, FindKernel index and resource bindings. Coordinate with T4/T5 for physical mouse/Resolution; no edits in their files.

WATER-001=OPEN; NOT_READY 0/3.
