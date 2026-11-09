# T1 FFT dispatch trace identity
session_id: 20261109T1110Z-T1-scheduled-sequence-canonical-7e2c
origin: scheduled
baseline_sha: c1ba237d3977fcc9086a48c46b473b14bdc52f88
scope: scripts/t1_fft_dispatch_pair_audit.py; scripts/tests/test_t1_fft_dispatch_sequence_canonical.py
hypothesis: JSONL sequence spellings 01 and 1 alias to the same int; non-ASCII decimal digits can alias or throw. This invalidates exact trace provenance for paired BeforeDispatch/AfterDispatch.
experiment_key: T1-FFT-SEQUENCE-CANONICAL-20261109
shared_resource: none; no Unity/CI/CL mutation
result: reject noncanonical ASCII decimal sequence; add 4 regression cases. Source commit 23fdbb24ae960f003ba61d6e72e430b86071886e; tests commit 6fba71b4e3a2b1da73cec3408f28c406a30fd1a2.
verification: code and tests committed; tests not executed in this environment because raw GitHub network DNS fails; not a GPU/Unity/device validation.
next: run python -m unittest discover -s scripts/tests -p test_t1_fft_dispatch_sequence_canonical.py; verify trace JSONL field spelling on actual device and obtain FindKernel/Dispatch bindings, compare Vulkan vs Unity first divergent pass.
