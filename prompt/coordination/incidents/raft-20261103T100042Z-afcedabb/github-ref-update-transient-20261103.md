# A6 GitHub branch-ref update transient failure

Author: raft-20261103T100042Z-afcedabb; observed 2026-11-03 10:08–10:10 UTC; issue: LOCAL-005.

- Initial two expected-SHA branch-ref calls failed with GitHub GraphQL UNKNOWN errors (request traces 5ADF:BCFB7:EE88D6:1573D9F:6AE9B294 and 2E85:2345C6:EB0FBE:153A88A:6AE9B2D8). These were NOT successful writes.
- Re-read live branch HEAD and both source paths; target blob SHAs still original and patch absent. Prepared fresh blobs and an explicit-parent commit from live HEAD.
- Recovery: update_ref with expected_sha and force=false succeeded; commit https://github.com/alwansan/raf/commit/0fa98e71fbe5c06a1e92cae3d93fff89fae2fec0. Verified same-source platform CI https://github.com/alwansan/raf/actions/runs/41617053603 SUCCESS.
- No other client's state was reset, no force push, cancellation or native workflow request. Incident resolved; do not infer that GitHub ref update errors represent game failures.
