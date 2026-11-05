# T2 independent work — 20261105T2017Z-T2-scheduled-retfix-7c3a
origin: scheduled
baseline_sha: 413b9dc06c1e6f304f276d2976dd9d666b272566
resumed_from_session: 20261105T1916Z-T2-scheduled-localbound-c61f.md
scope: scripts/t2_rt_return_cfg.py; tests/test_t2_rt_return_cfg.py; independent session/work records
hypothesis: a CFG return-site visited before a predecessor join can retain stale return classifications in the append-only returns list, so results are order-dependent; branch operands of bool are incorrectly accepted as int.
test: synthetic branch convergence with a return reprocessed after an incoming-state change; bool branch target rejected. No private game input.
shared_resource: none; no Unity or CI requested.
status: registered before source changes; lease: reread file blob SHA before update, no force.
