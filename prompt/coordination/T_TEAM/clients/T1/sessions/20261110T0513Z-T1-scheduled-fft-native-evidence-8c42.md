# 20261110T0513Z-T1-scheduled-fft-native-evidence-8c42
origin=scheduled
role=T1
issue=WATER-001
owner_priority=2026-11-05 device run 42058825739 (artifact world entry/save/re-entry succeeded; release packaging failed); historical APK86 is superseded.
owner_log_counters=220911-559: 23884 water pass, 3850 FFT kernel; 230108-327: 39132 water pass, 6026 FFT kernel; separate sessions, not unique fault counts.
work=prompt/coordination/T_TEAM/work/20261110T0513Z-T1-scheduled-fft-native-evidence-8c42.md
implementation=tests/test_t1_fft_native_trace_contract.py
commits=scope d37156c19388a102013e9695ab5bc88e8091352c; test 71241dd35229305440ad0f7a5876b67b35de0cd2
experiment=T1-FFT-NATIVE-TRACE-CONTRACT-20261110
result=Added 4 unittest cases (valid native return remains non-GPU proof; six invalid group vectors; cross-session provenance; forged GPU success). Source-level regression only; CI execution not yet confirmed. No original shader bytes or private assets published.
limitations=No authentic FindKernel mapping, resource GUID, GPU readback, or first mismatched Vulkan/Unity FFT pass proven. No Unity/Android build requested. T4 owns physical mouse and T5 owns Resolution and UI buttons; no overlapping edits.
next=Run python -m unittest tests.test_t1_fft_native_trace_contract on SHA 71241dd3 or newer; inspect failure if any. Then acquire authentic FFT kernel binding and per-pass GPU readbacks. Keep WATER-001 OPEN/NOT_READY.
