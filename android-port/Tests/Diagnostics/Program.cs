using System;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using RaftAndroid.Diagnostics;

class Program
{
    static int checks;
    static void Require(bool ok) { if (!ok) throw new Exception("Persistent logging check failed: " + checks); checks++; }
    static string[] Lines(string root) => Directory.GetFiles(root, "raft-*.jsonl").SelectMany(File.ReadAllLines).ToArray();
    static void Main()
    {
        string root = Path.Combine(Path.GetTempPath(), "raft-log-test-" + Guid.NewGuid().ToString("N"));
        try
        {
            using (var log = new PersistentDiagnosticLog(root))
            {
                string detail = "Arabic العربية / quote \" slash \\ newline\ncontrol\u0001";
                log.Write("save", "begin", detail, true);
                var first = JsonDocument.Parse(Lines(root).Single()).RootElement;
                Require(first.GetProperty("detail").GetString() == detail);
                Require(first.GetProperty("operation").GetString() == "begin");
                Require(first.GetProperty("sequence").GetInt64() > 0);
                Require(first.GetProperty("thread").GetInt32() > 0);
                Parallel.For(0, 300, i => log.Write("parallel", "entry", i.ToString()));
                log.Write("audio", "native_call_barrier", "", true);
                Require(Lines(root).Any(l => l.Contains("native_call_barrier")));
                Require(log.LastError == null);
            }
            Require(Lines(root).Length == 302);
            using (var log = new PersistentDiagnosticLog(root, 4096, 12, 1))
            {
                Parallel.For(0, 5000, i => log.Write("pressure", "entry", i.ToString()));
                log.Write("audio", "critical_after_pressure", "", true);
                Require(Lines(root).Any(l => l.Contains("critical_after_pressure")));
                foreach (string line in Lines(root)) using (JsonDocument.Parse(line)) { }
                Require(log.LastError == null);
            }
            string rotating = Path.Combine(root, "rotation");
            Directory.CreateDirectory(rotating);
            File.WriteAllText(Path.Combine(rotating, "user-note.txt"), "keep");
            using (var log = new PersistentDiagnosticLog(rotating, 1024, 3))
            {
                log.Write("startup", "must_survive_rotation", "first failure stack", true);
                for (int i = 0; i < 30; i++) log.Write("rotation", "event", new string('x', 100), true);
                Require(Directory.GetFiles(rotating, "raft-*.jsonl").Length <= 3);
                Require(Directory.GetFiles(rotating, "raft-*.jsonl").All(p => new FileInfo(p).Length <= 1024));
                Require(File.ReadAllText(Path.Combine(rotating, "user-note.txt")) == "keep");
                Require(!Lines(rotating).Any(l => l.Contains("must_survive_rotation")));
                Require(Directory.GetFiles(Path.Combine(rotating, "startup")).SelectMany(File.ReadAllLines)
                    .Any(l => l.Contains("must_survive_rotation")));
            }
            using (var log = new PersistentDiagnosticLog(rotating, 1024, 3)) log.Write("startup", "new_session", "", true);
            Require(Lines(rotating).Any(l => l.Contains("new_session")));
            Require(Directory.GetFiles(rotating, "raft-*.jsonl").Length <= 3);
            for (int i = 0; i < 6; i++)
                using (var log = new PersistentDiagnosticLog(rotating)) log.Write("startup", "bounded_launch", "", true);
            Require(Directory.GetFiles(Path.Combine(rotating, "startup")).Length == 4);
            Require(Directory.GetFiles(Path.Combine(rotating, "startup")).All(p => new FileInfo(p).Length <= 256 * 1024));
            // Regression: Unity's threaded log callbacks can still be entering
            // Write while the scene/activity shuts down this sink. None may
            // signal an already-disposed AutoResetEvent or corrupt JSONL.
            string shutdownRoot = Path.Combine(root, "shutdown-race");
            Directory.CreateDirectory(shutdownRoot);
            for (int round = 0; round < 8; round++)
            {
                var concurrentLog = new PersistentDiagnosticLog(shutdownRoot, 4096, 4, 32);
                var go = new System.Threading.ManualResetEventSlim(false);
                var ready = new System.Threading.CountdownEvent(8);
                var unexpected = new System.Collections.Concurrent.ConcurrentQueue<Exception>();
                var writers = Enumerable.Range(0, 8).Select(workerId => Task.Run(() =>
                {
                    ready.Signal();
                    go.Wait();
                    for (int k = 0; k < 150; k++)
                    {
                        try { concurrentLog.Write("shutdown", "threaded", workerId + ":" + k, k % 50 == 0); }
                        catch (Exception error) { unexpected.Enqueue(error); }
                    }
                })).ToArray();
                Require(ready.Wait(5000));
                go.Set();
                concurrentLog.Dispose();
                Require(Task.WaitAll(writers, 10000));
                concurrentLog.Write("shutdown", "after_dispose", "", true);
                Require(unexpected.IsEmpty);
                Require(concurrentLog.LastError == null);
                foreach (string line in Lines(shutdownRoot))
                    using (JsonDocument.Parse(line)) { }
                ready.Dispose();
                go.Dispose();
            }
            // Storage-fault regression: a full queue plus dropped ordinary
            // diagnostics MUST NOT permit critical reports to grow the queue
            // without bound when Flush() fails before dequeuing anything.
            // This fault is confined to a private synthetic sink, no app data.
            string failedRoot = Path.Combine(root, "fault-bounded-queue");
            var broken = new PersistentDiagnosticLog(failedRoot, 1024, 3, 1);
            int queueCountUnderFault = -1, pendingUnderFault = -1;
            bool originalSeedSurvivedFault = false;
            bool originalSeedRecoverable = false;
            bool overflowMarkerRecoverable = false;
            long overflowRetained = -1;
            try
            {
                var reflection = System.Reflection.BindingFlags.Instance |
                    System.Reflection.BindingFlags.NonPublic;
                var type = typeof(PersistentDiagnosticLog);
                object faultIoGate = type.GetField("ioGate", reflection).GetValue(broken);
                var startupFault = (FileStream)type.GetField("startup", reflection).GetValue(broken);
                var pendingFault = (System.Collections.Concurrent.ConcurrentQueue<string>)
                    type.GetField("pending", reflection).GetValue(broken);
                var countField = type.GetField("count", reflection);
                var droppedField = type.GetField("dropped", reflection);
                lock (faultIoGate)
                {
                    // The background worker must not drain the queue until the
                    // deterministic error/overflow sequence has completed.
                    startupFault.Dispose(); // simulate persistent startup I/O fault
                    broken.Write("synthetic", "seed", "", false);
                    for (int i = 0; i < 24; i++)
                    {
                        broken.Write("synthetic", "ordinary_dropped", "", false);
                        broken.Write("synthetic", "critical_during_io_fault", "", true);
                    }
                    queueCountUnderFault = (int)countField.GetValue(broken);
                    pendingUnderFault = pendingFault.Count;
                    overflowRetained = (long)droppedField.GetValue(broken);
                    originalSeedSurvivedFault = pendingFault.Any(
                        line => line.Contains("\"operation\":\"seed\""));
                    Require(broken.LastError != null);
                    // Restore test-only I/O. A durable queue must preserve the
                    // first diagnostic and record the lost flood on recovery.
                    string originalStartupPath = Directory.GetFiles(
                        Path.Combine(failedRoot, "startup"), "startup-*.jsonl").Single();
                    type.GetField("startup", reflection).SetValue(broken,
                        new FileStream(originalStartupPath, FileMode.Append,
                            FileAccess.Write, FileShare.Read));
                    broken.Flush();
                    // A successful recovery must clear the stale storage-fault
                    // status, not keep AndroidRuntimeLog.Status permanently red.
                    // The earlier LastError != null assertion proves the fault.
                    Require(broken.LastError == null);
                    originalSeedRecoverable = Lines(failedRoot).Any(
                        line => line.Contains("\"operation\":\"seed\""));
                    overflowMarkerRecoverable = Lines(failedRoot).Any(
                        line => line.Contains("\"operation\":\"queue_overflow\""));
                }
            }
            finally { broken.Dispose(); }
            Require(queueCountUnderFault <= 1);
            Require(pendingUnderFault <= 1);
            Require(overflowRetained > 0);
            Require(originalSeedSurvivedFault);
            Require(originalSeedRecoverable);
            Require(overflowMarkerRecoverable);
            var repeated = new RepeatedDiagnosticMessages();
            DateTime now = DateTime.UtcNow;
            Require(repeated.First("Error", "same message\nfull stack", now));
            Parallel.For(0, 10000, i => RequireFalse(repeated.First("Error", "same message\nfull stack", now.AddSeconds(1))));
            string summary = null;
            repeated.Summarize((area, operation, detail) => summary = detail);
            Require(summary != null && summary.Contains("repeated=10000;") && summary.Contains("full stack"));
            repeated.Summarize((area, operation, detail) => throw new Exception("Duplicate summary"));
            Require(repeated.First("Exception", "same message\nfull stack", now));
            Require(repeated.First("Error", "same message\ndifferent stack", now));
            for (int i = 0; i < 200; i++) Require(repeated.First("Error", "unique " + i, now));
            Require(repeated.First("Error", "capacity overflow", now));
            Require(repeated.First("Error", "capacity overflow", now));
            // The previous implementation cleared every group's count before
            // delivering the first summary; an injected callback failure erased
            // both the failed group and groups never attempted.
            var faulted = new RepeatedDiagnosticMessages();
            Require(faulted.First("Exception", "alpha full stack", now));
            Require(!faulted.First("Exception", "alpha full stack", now));
            Require(!faulted.First("Exception", "alpha full stack", now));
            Require(faulted.First("Exception", "beta full stack", now));
            Require(!faulted.First("Exception", "beta full stack", now));
            bool callbackFailed = false;
            int attempted = 0;
            try
            {
                faulted.Summarize((area, operation, detail) =>
                {
                    attempted++;
                    throw new IOException("Injected persistent sink failure");
                });
            }
            catch (IOException) { callbackFailed = true; }
            Require(callbackFailed && attempted == 1);
            var recovered = new System.Collections.Generic.List<string>();
            faulted.Summarize((area, operation, detail) => recovered.Add(detail));
            Require(recovered.Count == 2);
            Require(recovered.Any(s => s.Contains("repeated=2;") && s.Contains("alpha full stack")));
            Require(recovered.Any(s => s.Contains("repeated=1;") && s.Contains("beta full stack")));
            faulted.Summarize((area, operation, detail) => throw new Exception("Duplicate recovery summary"));

            // Repeats received concurrently during a failing callback must
            // survive alongside the original failed batch, without re-logging
            // the first full exception stack.
            var overlapping = new RepeatedDiagnosticMessages();
            Require(overlapping.First("Error", "overlap stack", now));
            Require(!overlapping.First("Error", "overlap stack", now));
            callbackFailed = false;
            try
            {
                overlapping.Summarize((area, operation, detail) =>
                {
                    Require(!overlapping.First("Error", "overlap stack", now.AddSeconds(1)));
                    throw new IOException("Injected overlapping sink failure");
                });
            }
            catch (IOException) { callbackFailed = true; }
            Require(callbackFailed);
            string combined = null;
            overlapping.Summarize((area, operation, detail) => combined = detail);
            Require(combined != null && combined.Contains("repeated=2;"));
            overlapping.Summarize((area, operation, detail) => throw new Exception("Duplicate overlap summary"));
            // DIAG-010: the two pairs below serialize to the same old key,
            // but their first full error stacks must remain independent.
            var collision = new RepeatedDiagnosticMessages();
            Require(collision.First("scene\nload", "stack", now));
            Require(collision.First("scene", "load\nstack", now));
            Require(!collision.First("scene\nload", "stack", now));
            Require(!collision.First("scene", "load\nstack", now));
            var collisionSummaries = new System.Collections.Generic.List<string>();
            collision.Summarize((area, operation, detail) => collisionSummaries.Add(detail));
            Require(collisionSummaries.Count == 2);
            Require(collisionSummaries.All(s => s.Contains("repeated=1;")));
            Require(collisionSummaries.Any(s => s.Contains("operation_length=10;")));
            Require(collisionSummaries.Any(s => s.Contains("operation_length=5;")));
            collision.Summarize((area, operation, detail) => throw new Exception("Duplicate colliding summary"));
            // Compile and execute the *real* Android-only Unity logger source
            // against test-only UnityEngine stubs. A temporary path that is an
            // ordinary file simulates an unavailable app sandbox at startup.
            // After fixing the sandbox path, explicit Initialize must recover.
            string androidRetry = Path.Combine(root, "android-init-retry");
            Directory.CreateDirectory(androidRetry);
            string blockedAppRoot = Path.Combine(androidRetry, "blocked-as-file");
            File.WriteAllText(blockedAppRoot, "synthetic storage fault");
            UnityEngine.Application.persistentDataPath = blockedAppRoot;
            AndroidRuntimeLog.Initialize();
            Require(AndroidRuntimeLog.StorageError != null);
            Require(AndroidRuntimeLog.Status == AndroidRuntimeLog.StorageError);
            // The log callback must still permit the HUD to show an early
            // original error, but never consume dedup state without a sink.
            string initialError = "synthetic first exception\nSyntheticStackTrace_T4";
            Require(AndroidRuntimeLog.UnityMessage("Error", initialError, true));
            File.Delete(blockedAppRoot);
            Directory.CreateDirectory(blockedAppRoot);
            AndroidRuntimeLog.Initialize();
            Require(AndroidRuntimeLog.StorageError == null);
            Require(AndroidRuntimeLog.Status == "ready");
            // Same actual error after storage recovery is the FIRST durable
            // occurrence and must include its full original stack.
            Require(AndroidRuntimeLog.UnityMessage("Error", initialError, true));
            Require(!AndroidRuntimeLog.UnityMessage("Error", initialError, true));
            // A third Initialize must leave the same working sink in place.
            AndroidRuntimeLog.Initialize();
            AndroidRuntimeLog.Flush();
            AndroidRuntimeLog.Shutdown();
            string recoveredLogs = Path.Combine(blockedAppRoot, "raft-logs");
            Require(Directory.GetFiles(recoveredLogs, "raft-*.jsonl").Length == 1);
            Require(Lines(recoveredLogs).Any(l => l.Contains("\"operation\":\"logger.ready\"")));
            // A single full original Error record is expected. Shutdown
            // correctly emits a separate repeat_summary containing that
            // operation's original text; don't miscount it as a second crash.
            Require(Lines(recoveredLogs).Count(l =>
                l.Contains("\"operation\":\"Error\"") &&
                l.Contains("SyntheticStackTrace_T4")) == 1);
            Require(Lines(recoveredLogs).Any(l =>
                l.Contains("\"operation\":\"repeat_summary\"") &&
                l.Contains("SyntheticStackTrace_T4")));
            foreach (string line in Lines(recoveredLogs))
                using (JsonDocument.Parse(line)) { }

            // A new native logger start in the same managed process is a new
            // evidence session. The old error's repeat-group dictionary must
            // not suppress the first full stack of this new session.
            AndroidRuntimeLog.Initialize();
            Require(AndroidRuntimeLog.Status == "ready");
            Require(AndroidRuntimeLog.UnityMessage("Error", initialError, true));
            Require(!AndroidRuntimeLog.UnityMessage("Error", initialError, true));
            AndroidRuntimeLog.Shutdown();
            Require(Directory.GetFiles(recoveredLogs, "raft-*.jsonl").Length == 2);
            Require(Lines(recoveredLogs).Count(l =>
                l.Contains("\"operation\":\"Error\"") &&
                l.Contains("SyntheticStackTrace_T4")) == 2);
            foreach (string line in Lines(recoveredLogs))
                using (JsonDocument.Parse(line)) { }
            // The real Android operation tracer calls Begin/EndOperation
            // around original SaveGame/Load. A diagnostic transport exception
            // must not escape back into those original game operations.
            // Synthetic reflection fault never touches real game files.
            string logFailureRoot = Path.Combine(root, "operation-logger-fault");
            UnityEngine.Application.persistentDataPath = logFailureRoot;
            AndroidRuntimeLog.Initialize();
            Require(AndroidRuntimeLog.Status == "ready");
            var binding = System.Reflection.BindingFlags.Static |
                          System.Reflection.BindingFlags.Instance |
                          System.Reflection.BindingFlags.NonPublic;
            var sinkField = typeof(AndroidRuntimeLog).GetField("sink", binding);
            var actualSink = (PersistentDiagnosticLog)sinkField.GetValue(null);
            var lifecycleField = typeof(PersistentDiagnosticLog).GetField(
                "lifecycleGate", binding);
            object savedLifecycleGate = lifecycleField.GetValue(actualSink);
            string firstRecoveredStack = "Original synthetic SaveGame error\nT4 save stack";
            try
            {
                // Null out only the sink's lifecycle monitor via reflection:
                // PersistentDiagnosticLog.Write then throws before enqueue,
                // simulating an unexpected transport failure. The background
                // writer uses a different ioGate and is not disrupted.
                lifecycleField.SetValue(actualSink, null);
                AndroidRuntimeLog.Write("save", "SaveGame.enter", "", true);
                long started = AndroidRuntimeLog.BeginOperation("save", "SaveGame", "");
                AndroidRuntimeLog.EndOperation("save", "SaveGame", started, false);
                Require(AndroidRuntimeLog.UnityMessage("Error", firstRecoveredStack, true));
                Require(AndroidRuntimeLog.Status == "diagnostic_write_ArgumentNullException");
                Require(!AndroidRuntimeLog.Status.Contains("SaveGame"));
            }
            finally
            {
                lifecycleField.SetValue(actualSink, savedLifecycleGate);
            }
            // The failed first Unity stack was never enqueued, so the next
            // occurrence on recovered storage must not be deduplicated away.
            Require(AndroidRuntimeLog.UnityMessage("Error", firstRecoveredStack, true));
            Require(!AndroidRuntimeLog.UnityMessage("Error", firstRecoveredStack, true));
            Require(AndroidRuntimeLog.Status == "ready");
            AndroidRuntimeLog.Shutdown();
            string faultRecoveredLogs = Path.Combine(logFailureRoot, "raft-logs");
            Require(Lines(faultRecoveredLogs).Count(l =>
                l.Contains("\"operation\":\"Error\"") &&
                l.Contains("T4 save stack")) == 1);
            Console.WriteLine("RAFT_PERSISTENT_LOG_TEST checks=" + checks + " passed=true actualAndroidStorageVerified=false");
        }
        finally { Directory.Delete(root, true); }
    }
    static void RequireFalse(bool value) { if (value) throw new Exception("Repeated error was not grouped"); }
}
