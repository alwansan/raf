using System;
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

    private static int Main()
    {
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
                string parallelRoot = Path.Combine(root, "parallel-first-launch");
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
