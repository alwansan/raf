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
            Test("world directory symlink cannot redirect save outside sandbox", () =>
            {
                string sandbox = Path.Combine(root, "linked-world-sandbox");
                string profile = new LocalProfileStore(sandbox).GetOrCreateProfileId();
                var paths = new LocalSavePaths(sandbox, profile);
                string directory = paths.GetWorldDirectory("redirect");
                Directory.CreateDirectory(Path.GetDirectoryName(directory)!);
                string outside = Path.Combine(root, "world-outside");
                Directory.CreateDirectory(outside);
                Directory.CreateSymbolicLink(directory, outside);
                ExpectException<IOException>(() => paths.GetWorldSaveFile("redirect"));
                ExpectException<IOException>(() => paths.GetWorldSaveFileAndCreateDirectory("redirect"));
                Assert(!File.Exists(Path.Combine(outside, "world.sav")), "Outside world save created");
            });
            Test("linked profile ancestor cannot redirect world saves", () =>
            {
                string sandbox = Path.Combine(root, "linked-profile-sandbox");
                string profiles = Path.Combine(sandbox, "RaftAndroid", "profiles");
                Directory.CreateDirectory(profiles);
                string outside = Path.Combine(root, "profile-outside");
                Directory.CreateDirectory(outside);
                Directory.CreateSymbolicLink(Path.Combine(profiles, "safe_profile"), outside);
                var paths = new LocalSavePaths(sandbox, "safe_profile");
                ExpectException<IOException>(() => paths.GetWorldDirectory("legit_world"));
                Assert(!Directory.Exists(Path.Combine(outside, "worlds")), "Outside profile directories created");
            });
            Test("save file symlink cannot redirect writes outside sandbox", () =>
            {
                string sandbox = Path.Combine(root, "linked-file-sandbox");
                string profile = new LocalProfileStore(sandbox).GetOrCreateProfileId();
                var paths = new LocalSavePaths(sandbox, profile);
                string leaf = paths.GetWorldSaveFileAndCreateDirectory("valid_world");
                string outside = Path.Combine(root, "external-world-save.bin");
                File.WriteAllText(outside, "original-external");
                File.CreateSymbolicLink(leaf, outside);
                ExpectException<IOException>(() => paths.GetWorldSaveFile("valid_world"));
                ExpectException<IOException>(() => paths.GetWorldSaveFileAndCreateDirectory("valid_world"));
                Assert(File.ReadAllText(outside) == "original-external", "External file changed");
            });
            Test("dangling save file symlink is rejected before target creation", () =>
            {
                string sandbox = Path.Combine(root, "dangling-file-sandbox");
                string profile = new LocalProfileStore(sandbox).GetOrCreateProfileId();
                var paths = new LocalSavePaths(sandbox, profile);
                string leaf = paths.GetWorldSaveFileAndCreateDirectory("valid_world");
                string outside = Path.Combine(root, "missing-target.bin");
                Assert(!File.Exists(outside), "Negative control target already exists");
                File.CreateSymbolicLink(leaf, outside);
                // File.Exists can report the link entry as existing on some .NET runtimes
                // even when its target is missing. Assert the actual link metadata.
                Assert((File.GetAttributes(leaf) & FileAttributes.ReparsePoint) != 0,
                    "Dangling save entry is not a symbolic link");
                ExpectException<IOException>(() => paths.GetWorldSaveFile("valid_world"));
                ExpectException<IOException>(() => paths.GetWorldSaveFileAndCreateDirectory("valid_world"));
                Assert(!File.Exists(outside), "Broken link unexpectedly created target");
            });
            Test("existing ordinary world save file remains readable and writable", () =>
            {
                string sandbox = Path.Combine(root, "regular-file-sandbox");
                string profile = new LocalProfileStore(sandbox).GetOrCreateProfileId();
                var paths = new LocalSavePaths(sandbox, profile);
                string leaf = paths.GetWorldSaveFileAndCreateDirectory("valid_world");
                File.WriteAllText(leaf, "unchanged-format");
                Assert(paths.GetWorldSaveFile("valid_world") == leaf, "Ordinary save filename changed");
                Assert(paths.GetWorldSaveFileAndCreateDirectory("valid_world") == leaf, "Regular world path changed");
                Assert(File.ReadAllText(leaf) == "unchanged-format", "Regular save contents changed");
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
