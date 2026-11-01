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
            Console.WriteLine("RAFT_PERSISTENT_LOG_TEST checks=" + checks + " passed=true actualAndroidStorageVerified=false");
        }
        finally { Directory.Delete(root, true); }
    }
    static void RequireFalse(bool value) { if (value) throw new Exception("Repeated error was not grouped"); }
}
