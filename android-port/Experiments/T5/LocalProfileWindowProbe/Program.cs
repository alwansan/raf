// T5: execute the REAL LocalProfileStore with a separate process holding an
// exclusive, visible-but-empty profile.id. All files and IDs are disposable;
// never emit an identity or sandbox path to CI logs.
using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using RaftAndroid.Platform;

internal static class Program
{
    private readonly record struct ReadResult(string Kind, string? Id);

    private static void Require(bool condition, string reason)
    {
        if (!condition) throw new InvalidOperationException(reason);
    }

    private static string ProfileFile(string root) =>
        Path.Combine(root, "RaftAndroid", "profiles", "local", "profile.id");

    private static int Writer(string root)
    {
        string pathname = ProfileFile(root);
        Directory.CreateDirectory(Path.GetDirectoryName(pathname)!);
        using var file = new FileStream(
            pathname, FileMode.CreateNew, FileAccess.Write, FileShare.None);

        // The final filename now exists, but its contents remain empty until
        // parent process signals the release. No race with timer startup.
        Console.WriteLine("READY");
        Console.Out.Flush();
        string release = Path.Combine(root, "release.writer");
        var timer = Stopwatch.StartNew();
        while (!File.Exists(release))
        {
            if (timer.Elapsed > TimeSpan.FromSeconds(12))
                throw new TimeoutException("Writer release signal missing");
            Thread.Sleep(5);
        }

        byte[] identity = Encoding.ASCII.GetBytes(
            Guid.NewGuid().ToString("N") + Environment.NewLine);
        file.Write(identity, 0, identity.Length);
        file.Flush(flushToDisk: true);
        return 0;
    }

    private static ReadResult ReadOriginal(string root)
    {
        try
        {
            return new ReadResult(
                "success", new LocalProfileStore(root).GetOrCreateProfileId());
        }
        catch (InvalidDataException)
        {
            return new ReadResult("invalid_data", null);
        }
        catch (IOException)
        {
            return new ReadResult("io_failure", null);
        }
    }

    private static void TestWindow(string parentRoot, string label,
                                   int writerHeldMilliseconds,
                                   bool expectSuccessBeforeRelease)
    {
        string root = Path.Combine(parentRoot, label);
        Directory.CreateDirectory(root);
        var start = new ProcessStartInfo("dotnet")
        {
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true
        };
        start.ArgumentList.Add(typeof(Program).Assembly.Location);
        start.ArgumentList.Add("--writer");
        start.ArgumentList.Add(root);
        using var writer = new Process { StartInfo = start };
        Require(writer.Start(), "Unable to launch exclusive original-profile writer");
        try
        {
            Task<string?> ready = writer.StandardOutput.ReadLineAsync();
            Require(ready.Wait(TimeSpan.FromSeconds(10)) &&
                    ready.Result == "READY",
                    "Exclusive writer did not announce real file creation");

            using var readerEntered = new ManualResetEventSlim(false);
            Task<ReadResult> reader = Task.Run(() =>
            {
                readerEntered.Set();
                return ReadOriginal(root);
            });
            Require(readerEntered.Wait(TimeSpan.FromSeconds(5)),
                    "Reader task did not start");

            Thread.Sleep(writerHeldMilliseconds);
            bool readerFinishedBeforeRelease = reader.IsCompleted;

            // Release the writer AFTER measuring the active retry boundary.
            // This also ensures its eventual original file is valid.
            File.WriteAllText(Path.Combine(root, "release.writer"), "release");
            Require(writer.WaitForExit(10000), "Writer failed to finish after release");
            Require(writer.ExitCode == 0, "Writer ended with an error");
            Require(reader.Wait(TimeSpan.FromSeconds(5)), "Reader did not finish");

            string persisted = File.ReadAllText(ProfileFile(root)).Trim();
            Require(persisted.Length == 32, "Writer did not persist full identity");
            string reopened = new LocalProfileStore(root).GetOrCreateProfileId();
            Require(persisted == reopened,
                    "Original persisted profile changed on reopening");

            ReadResult observed = reader.Result;
            if (expectSuccessBeforeRelease)
            {
                Require(!readerFinishedBeforeRelease,
                        "Short reader completed while exclusive profile writer still empty");
                Require(observed.Kind == "success" && observed.Id == persisted,
                        "Short exclusive writer yielded invalid/replaced identity");
            }
            else
            {
                Require(readerFinishedBeforeRelease,
                        "Original retry window outlasted long exclusive writer unexpectedly");
                Require(observed.Kind == "invalid_data" || observed.Kind == "io_failure",
                        "Long exclusive writer failed to expose bounded retry exception");
                Require(observed.Id == null,
                        "Long retry failure leaked an unverified profile identity");
            }

            Console.WriteLine("T5_PROFILE_PROCESS_WINDOW " +
                              "case=" + label +
                              " writer_held_ms=" + writerHeldMilliseconds +
                              " finished_before_release=" +
                              readerFinishedBeforeRelease.ToString().ToLowerInvariant() +
                              " outcome=" + observed.Kind +
                              " persisted_stable=true");
        }
        finally
        {
            if (!writer.HasExited)
            {
                writer.Kill(entireProcessTree: true);
                writer.WaitForExit(5000);
            }
        }
    }

    private static void TestPersistentCorruption(string parentRoot)
    {
        string root = Path.Combine(parentRoot, "persistent-corrupt");
        string pathname = ProfileFile(root);
        Directory.CreateDirectory(Path.GetDirectoryName(pathname)!);
        const string broken = "invalid-id!";
        File.WriteAllText(pathname, broken);
        ReadResult result = ReadOriginal(root);
        Require(result.Kind == "invalid_data" && result.Id == null,
                "Persistently invalid profile was not rejected");
        Require(File.ReadAllText(pathname) == broken,
                "Persistently corrupt identity was overwritten");
        Console.WriteLine(
            "T5_PROFILE_PERMANENT_CORRUPTION outcome=invalid_data original_unchanged=true");
    }

    private static int Run()
    {
        string root = Path.Combine(Path.GetTempPath(), "t5-profile-probe-" +
                                   Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        try
        {
            // One genuine separate process holds an empty final profile file
            // long enough for the original reader to see it, then publishes
            // valid bytes. This is NOT a fake profile-store implementation.
            TestWindow(root, "short", 300, expectSuccessBeforeRelease: true);
            TestWindow(root, "long", 3500, expectSuccessBeforeRelease: false);
            TestPersistentCorruption(root);
            Console.WriteLine(
                "T5_PROFILE_SOURCE_PROBE_PASSED actual_platform_library=true " +
                "cross_process=true synthetic_data_only=true android_device=false");
            return 0;
        }
        finally
        {
            try { Directory.Delete(root, recursive: true); }
            catch (IOException) { }
            catch (UnauthorizedAccessException) { }
        }
    }

    private static int Main(string[] args)
    {
        try
        {
            if (args.Length == 2 && args[0] == "--writer")
                return Writer(args[1]);
            if (args.Length != 0)
                throw new ArgumentException("Unknown source-probe mode");
            return Run();
        }
        catch (Exception error)
        {
            // Exact exception *category* only, never original ID or root path.
            Console.Error.WriteLine("T5_PROFILE_SOURCE_PROBE_FAILED type=" +
                                    error.GetType().Name);
            return 1;
        }
    }
}
