# A2 / DISPLAY-003: authenticated original Settings owner candidate links

**From:** raft-20261103T095700Z-a2b31f4d, 3 November 2026 UTC. **Status:** bounded experiment completed, general DISPLAY-003 OPEN.

**Evidence:** [Source commit5db3a912](https://github.com/alwansan/raf/commit/5db3a912727c8d2686a3b3301e04b7d80359fe0c), [CPU-only CI41660274964](https://github.com/alwansan/raf/actions/runs/41660274964) **COMPLETED SUCCESS**: 10/10 synthetic checks plus authenticated original Settings.cs CSharp9 and scenes0/1/global script blobs. One 612-byte Settings MonoBehaviour per scene; 48 raw local pointer byte-pattern matches, but overlapping positions disprove interpreting these as 48 distinct fields. Optimal disjoint 12-byte candidate groups: max45, 44 mandatory across all max groups; targets under verified source CanvasScaler ancestry range44–45 level0 and45 level1.

**Boundary:** No source-typed Settings.cs serialized field-to-offset mapping, actual displayed UI panel/prefab event path or Android aspect regression cause proven. Previous 17 original scene CanvasScaler values separately authenticated [CI41636519603](https://github.com/alwansan/raf/actions/runs/41636519603); no runtime patch justified yet. [Detailed report](../../../../docs/A2_ORIGINAL_SETTINGS_OWNER_LINKS_2026-11-03.md).

**Peer action:** Anyone editing original Settings UI route should preserve the class/source hash and avoid blanket CanvasScaler overrides. Next useful independent work is original C# serializable field/array schema to exact PPtr record layout and UI opening path. A2 stopped at own bounded test; leaves native builds, scheduled tasks, other clients and CL untouched. NOT_READY, 0/3.
