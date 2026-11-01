using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RaftAndroid.Platform;

internal static class Program
{
    private static int _passed;
    private static int _failed;

    private static void Assert(bool value, string explanation)
    {
        if (!value) throw new Exception(explanation);
    }

    private static void Test(string name, Action action)
    {
        try
        {
            action();
            _passed++;
            Console.WriteLine("PASS " + name);
        }
        catch (Exception exc)
        {
            _failed++;
            Console.WriteLine("FAIL " + name + ": " + exc.GetType().Name + " - " + exc.Message);
        }
    }

    private static void ExpectException<T>(Action action) where T : Exception
    {
        try { action(); }
        catch (T) { return; }
        throw new Exception("Expected " + typeof(T).Name);
    }

    private static int Main(string[] args)
    {
        if (args.Length == 2 && args[0] == "--profile-child")
        {
            Console.WriteLine(new LocalProfileStore(args[1]).GetOrCreateProfileId());
            return 0;
        }
        string root = Path.Combine(Path.GetTempPath(), "raft-platform-tests-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        try
        {
            Test("new profile ID is stable across restarts", () =>
            {
                var store = new LocalProfileStore(root);
                string first = store.GetOrCreateProfileId();
                Assert(first.Length == 32, "GUID-format ID required");
                Assert(first == new LocalProfileStore(root).GetOrCreateProfileId(), "Identity changed on reopen");
            });
            Test("concurrent first launches preserve one durable profile identity", () =>
            {
                // Exercise multiple fresh roots; the old File.Move race was intermittent.
                for (int round = 0; round < 8; round++)
                {
                string parallelRoot = Path.Combine(root, "parallel-first-launch-" + round);
                using var start = new ManualResetEventSlim(false);
                var tasks = Enumerable.Range(0, 24).Select(_ => Task.Run(() =>
                {
                    start.Wait();
                    return new LocalProfileStore(parallelRoot).GetOrCreateProfileId();
                })).ToArray();
                start.Set();
                Task.WaitAll(tasks);
                string first = tasks[0].Result;
                Assert(tasks.All(task => task.Result == first),
                    "Concurrent launch generated multiple profile identities");
                string profileDirectory = Path.Combine(parallelRoot, "RaftAndroid", "profiles", "local");
                Assert(Directory.GetFiles(profileDirectory, "*.tmp").Length == 0,
                    "Concurrent profile creation left temporary identity files");
                Assert(new LocalProfileStore(parallelRoot).GetOrCreateProfileId() == first,
                    "Concurrent identity did not persist after restart");
                }
            });
            Test("concurrent separate processes preserve one durable profile identity", () =>
            {
                // A process-level regression is needed in addition to the thread test:
                // the old check-then-Move bug could replace a profile on Unix.
                string processRoot = Path.Combine(root, "parallel-process-launch");
                var children = new List<Process>();
                try
                {
                    for (int i = 0; i < 12; i++)
                    {
                        var start = new ProcessStartInfo("dotnet")
                        {
                            UseShellExecute = false,
                            RedirectStandardOutput = true,
                            RedirectStandardError = true
                        };
                        start.ArgumentList.Add(typeof(Program).Assembly.Location);
                        start.ArgumentList.Add("--profile-child");
                        start.ArgumentList.Add(processRoot);
                        children.Add(Process.Start(start) ?? throw new Exception("Child process failed to start"));
                    }
                    var identities = new List<string>();
                    foreach (Process child in children)
                    {
                        Assert(child.WaitForExit(30000), "Concurrent profile child timed out");
                        string identity = child.StandardOutput.ReadToEnd().Trim();
                        string error = child.StandardError.ReadToEnd();
                        Assert(child.ExitCode == 0, "Concurrent profile child failed: " + error);
                        Assert(identity.Length == 32, "Concurrent profile child returned invalid identity");
                        identities.Add(identity);
                    }
                    Assert(identities.Distinct().Count() == 1, "Concurrent processes generated different identities");
                    Assert(new LocalProfileStore(processRoot).GetOrCreateProfileId() == identities[0],
                        "Concurrent process identity did not persist on reopen");
                }
                finally
                {
                    foreach (Process child in children)
                    {
                        if (!child.HasExited) child.Kill(entireProcessTree: true);
                        child.Dispose();
                    }
                }
            });
            Test("incomplete identity is retried without replacing its writer", () =>
            {
                // A separate process may see the final file before the first
                // process has finished writing its GUID. Never treat this
                // transient empty file as a permanently corrupt save.
                string pendingRoot = Path.Combine(root, "pending-profile-writer");
                string profileDirectory = Path.Combine(pendingRoot, "RaftAndroid", "profiles", "local");
                Directory.CreateDirectory(profileDirectory);
                string profileFile = Path.Combine(profileDirectory, "profile.id");
                File.WriteAllText(profileFile, "");
                string expected = Guid.NewGuid().ToString("N");
                Task writer = Task.Run(() =>
                {
                    Thread.Sleep(75);
                    File.WriteAllText(profileFile, expected + Environment.NewLine);
                });
                string observed = new LocalProfileStore(pendingRoot).GetOrCreateProfileId();
                Assert(writer.Wait(5000), "Simulated profile writer did not finish");
                Assert(observed == expected, "Incomplete identity was not retried");
                Assert(File.ReadAllText(profileFile).Trim() == expected,
                    "Concurrent reader overwrote the writer's identity");
            });
            Test("independent app sandboxes have separate identities", () =>
            {
                string first = new LocalProfileStore(root).GetOrCreateProfileId();
                string other = new LocalProfileStore(Path.Combine(root, "another-sandbox")).GetOrCreateProfileId();
                Assert(first != other, "Cross-app identity collision");
            });
            Test("offline session is local-only and acts as solo host", () =>
            {
                string id = new LocalProfileStore(root).GetOrCreateProfileId();
                var session = new OfflineSession(id);
                Assert(session.IsHost && session.IsSinglePlayer && session.IsConnected, "Incorrect solo flags");
                Assert(!session.UsesSteam && !session.UsesInternet && session.ConnectedPlayerCount == 1, "External network leak");
            });
            Test("separate worlds stay in isolated save directories", () =>
            {
                string id = new LocalProfileStore(root).GetOrCreateProfileId();
                var paths = new LocalSavePaths(root, id);
                var a = paths.GetWorldSaveFileAndCreateDirectory("world_one");
                var b = paths.GetWorldSaveFileAndCreateDirectory("world_two");
                Assert(a != b, "World save collision");
                Assert(File.Exists(a) == false && Directory.Exists(Path.GetDirectoryName(a)!), "Unexpected save contents");
                Assert(Path.GetFullPath(a).StartsWith(Path.GetFullPath(root), StringComparison.Ordinal), "Save escaped sandbox");
            });
            Test("world name path traversal and separators are rejected", () =>
            {
                string id = new LocalProfileStore(root).GetOrCreateProfileId();
                var paths = new LocalSavePaths(root, id);
                foreach (string input in new[] { "../other", "..", "x/y", "x\\y", "", "space here" })
                    ExpectException<ArgumentException>(() => paths.GetWorldDirectory(input));
            });
            Test("corrupt existing identity is not silently overwritten", () =>
            {
                string bad = Path.Combine(root, "corrupted-sandbox", "RaftAndroid", "profiles", "local");
                Directory.CreateDirectory(bad);
                File.WriteAllText(Path.Combine(bad, "profile.id"), "invalid-id!");
                var store = new LocalProfileStore(Path.Combine(root, "corrupted-sandbox"));
                ExpectException<InvalidDataException>(() => store.GetOrCreateProfileId());
                Assert(File.ReadAllText(Path.Combine(bad, "profile.id")) == "invalid-id!", "Corrupt identity overwritten");
            });
            Test("invalid local profile IDs and missing root are rejected", () =>
            {
                ExpectException<ArgumentException>(() => new LocalSavePaths(root, "../escape"));
                ExpectException<ArgumentException>(() => new LocalSavePaths("", "ok"));
                ExpectException<ArgumentException>(() => new LocalProfileStore(""));
            });
        }
        finally
        {
            try { Directory.Delete(root, recursive: true); } catch (IOException) { }
        }
        Console.WriteLine("TOTAL passed=" + _passed + " failed=" + _failed);
        return _failed == 0 ? 0 : 1;
    }
}
