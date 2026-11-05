# T4 → T5 — Android Load argument-path evidence gate

- author: T4; session_id: 20261105T1246Z-T4-chat-load-file-gate-m8q2; issue_id: LOCAL-005; origin: chat
- source commit: a88000086d973adfcb05a85a7ecd0b12133cbf81; fixture correction: e1ff457c8b4723bba5e53b944fe97cbbf898a3e4
- original 14-source managed integration SUCCESS [42030693004](https://github.com/alwansan/raf/actions/runs/42030693004), synthetic UNITY_ANDROID C# SUCCESS [42031436693](https://github.com/alwansan/raf/actions/runs/42031436693)

New `save/Load.argumentFileSnapshot` read-only marker classifies exists_at_filename_argument and length_class zero/nonzero/not_checked (or probe-unavailable) after original load. This does not mutate file, deserialize, guarantee valid `.rgd`, or prove runtime device. Existing `save/Load.caughtException` marks swallowed original error; the operation exit name is `Load<T>` (generic) while snapshot marker deliberately remains `Load.argumentFileSnapshot`.

On a single coordinated native candidate, correlate B07 `WorldHasBeenLoaded.firstMoveNext`, T4 `WorldHasBeenLoaded.originalCompletionAssigned`, `Save.argumentFileSnapshot`, `Load.caughtException`, `Load.argumentFileSnapshot` with create→play→genuine save→quit→relaunch→load. A caught exception plus absent file suggests missing input/path; caught exception with present nonzero file directs investigation to open/read/deserialize/assembly compatibility. Neither diagnoses itself without the original error/context. No native build or Release requested by this T4 session.

LOCAL-005 OPEN, NOT_READY 0/3; preserve sound, Settings and deferred touch; source pin and .meta unchanged. Work/session links in clients/T4/sessions/20261105T1246Z-T4-chat-load-file-gate-m8q2.md.
