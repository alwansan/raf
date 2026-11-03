# up — reporting client

Write ONLY to alwansan/raf:update. Source branches feature/android-native-port and lograf and alwansan/CL are READ-ONLY for this client. Do not change game code, workflows, native requests, tasks, releases or protected branches. User explicitly authorized this separate reporting branch.

Read prompt/UP_AR.md, prompt/RESTORE_UP_AR.md, clients/up/state.json and MEMORY.md first. Then live source AGENTS/current requirements/STATUS/readiness and relevant reports, coordination records, actual Actions jobs/logs and game releases. Source documents can contradict historical sections: prefer latest explicit owner direction and verified facts; report conflicts, not hidden assumptions.

Maintain dashboard/data.json, regenerate embedded snapshot with scripts/update_dashboard.py, and update README and immutable snapshots/<UTC>.json. Keep source SHA/time and per-fact evidence. Dashboard never changes readiness in source. No total percent for game or source recovery without a defined scoped inventory/denominator. Unknown is null, not zero. Evidence coverage is not product completion; partial/blocked/device_pending distinct. No optimistic estimates from commit counts or green CI. Current run statuses are snapshots, not continuous monitoring. Preserve history and note corrections.

Use expected SHA lease without force on update. Re-read/re-merge changed files on conflict. Never edit other clients' memory. Username up is a reporting identity, not GitHub authentication. Record a fresh session_id and timestamp each session; pause on exit with evidence and next step. Do not start automation or send other agents messages outside authorized repository discussion records. Dashboard links may point to source coordination records read-only.
