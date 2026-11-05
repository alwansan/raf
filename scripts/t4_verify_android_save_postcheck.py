"""Generate a source-free C# UNITY_ANDROID compile/execution check for T4 Save IO telemetry.

This fixture does not contain original Raft source or serialized game bytes.
The real original source and adapted-SHA gates are exercised separately by the
existing offline managed pipeline.
"""
import argparse
from pathlib import Path

from scripts.instrument_android_runtime_operations import wrap

SAVE_SIGNATURE = "private void Save(string filename, RGD raftgamedata)"

SYNTHETIC_CLASS = """\
public sealed class RGD {}
public sealed class SaveAndLoad
{
    private void Save(string filename, RGD raftgamedata)
    {
        if (raftgamedata == null) return;
        if (filename == "!") throw new System.InvalidOperationException("synthetic exception");
        using (var f = System.IO.File.Create(filename))
        {
            f.WriteByte(42);
            f.Flush(true);
        }
    }
    public void Run(string filename, RGD data) { Save(filename, data); }
}
"""

STUBS_AND_EXECUTION = r"""
namespace RaftAndroid.Diagnostics
{
    public static class AndroidRuntimeLog
    {
        public static readonly System.Collections.Generic.List<string> Events =
            new System.Collections.Generic.List<string>();
        public static bool ThrowOnSnapshot;
        public static long BeginOperation(string area, string operation, string detail)
        {
            Events.Add(area + "." + operation + ".enter");
            return 1L;
        }
        public static void Write(string area, string operation, string detail,
                                 bool critical = false)
        {
            if (ThrowOnSnapshot && operation.StartsWith("Save.argumentFileSnapshot"))
                throw new System.InvalidOperationException("synthetic logger failure");
            Events.Add(area + "." + operation + "|" + detail);
        }
        public static void EndOperation(string area, string operation, long started, bool failed)
        {
            Events.Add(area + "." + operation + ".exit|failed=" + failed);
        }
        public static void Clear() { Events.Clear(); }
    }
}
internal static class Program
{
    private static void Require(bool condition)
    {
        if (!condition) throw new System.InvalidOperationException("synthetic assertion");
    }
    private static string First(string prefix)
    {
        foreach (string e in RaftAndroid.Diagnostics.AndroidRuntimeLog.Events)
            if (e.StartsWith(prefix)) return e;
        throw new System.InvalidOperationException("synthetic event missing");
    }

    private static void Main()
    {
        var root = System.IO.Path.Combine(System.IO.Path.GetTempPath(),
            "t4-post-save-" + System.Guid.NewGuid().ToString("N"));
        System.IO.Directory.CreateDirectory(root);
        var file = System.IO.Path.Combine(root, "synthetic-not-a-game-save.rgd");
        var game = new SaveAndLoad();
        try
        {
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Clear();
            game.Run(file, new RGD());
            Require(System.IO.File.Exists(file));
            Require(System.IO.File.ReadAllBytes(file).Length == 1);
            Require(First("save.Save.argumentFileSnapshot|").Contains(
                "exists_at_filename_argument=True; length_class=nonzero"));
            Require(First("save.Save.exit|").Contains("failed=False"));

            System.IO.File.Delete(file);
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Clear();
            game.Run(file, null);
            Require(!System.IO.File.Exists(file));
            Require(First("save.Save.argumentFileSnapshot|").Contains(
                "exists_at_filename_argument=False; length_class=not_checked"));
            Require(First("save.Save.exit|").Contains("failed=False"));

            RaftAndroid.Diagnostics.AndroidRuntimeLog.Clear();
            RaftAndroid.Diagnostics.AndroidRuntimeLog.ThrowOnSnapshot = true;
            game.Run(file, new RGD());
            RaftAndroid.Diagnostics.AndroidRuntimeLog.ThrowOnSnapshot = false;
            Require(System.IO.File.Exists(file));
            Require(First("save.Save.exit|").Contains("failed=False"));

            RaftAndroid.Diagnostics.AndroidRuntimeLog.Clear();
            bool originalExceptionPreserved = false;
            try { game.Run("!", new RGD()); }
            catch (System.InvalidOperationException e)
            {
                originalExceptionPreserved = e.Message == "synthetic exception";
            }
            Require(originalExceptionPreserved);
            Require(First("save.Save.exit|").Contains("failed=True"));
            Require(First("save.Save.argumentFileSnapshot|").Contains(
                "exists_at_filename_argument=False"));

            System.Console.WriteLine(
                "T4_ANDROID_POST_SAVE_CHECK synthetic_android_csharp_compiled=true" +
                " nonempty_file_observed=true empty_path_observed=true" +
                " logger_failure_nonfatal=true original_exception_preserved=true" +
                " original_game_serializer_executed=false real_RGD_roundtrip=false" +
                " unity_il2cpp_or_device_tested=false");
        }
        finally
        {
            RaftAndroid.Diagnostics.AndroidRuntimeLog.ThrowOnSnapshot = false;
            if (System.IO.Directory.Exists(root))
                System.IO.Directory.Delete(root, true);
        }
    }
}
"""

PROJECT = """\
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net9.0</TargetFramework>
    <DefineConstants>UNITY_ANDROID</DefineConstants>
    <Nullable>disable</Nullable>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
</Project>
"""


def build_source():
    wrapped = wrap(SYNTHETIC_CLASS, SAVE_SIGNATURE, "save", "filename")
    if wrapped.count("Save.argumentFileSnapshot") != 2:
        # A normal status and a separate unavailable status, never real success.
        raise ValueError("Unexpected generated Save post-snapshot markers")
    if "if (raftgamedata == null) return;" not in wrapped:
        raise ValueError("Original early-return fixture altered")
    if wrapped.count("System.IO.File.Exists(filename)") != 1:
        raise ValueError("Expected one read-only original argument path probe")
    if "new System.IO.FileInfo(filename).Length == 0L" not in wrapped:
        raise ValueError("Expected bounded file length class only")
    return wrapped + "\n" + STUBS_AND_EXECUTION


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output
    if output.exists() or output.is_symlink() or any(
            node.is_symlink() for node in output.parents):
        raise ValueError("Refuse an existing or linked fixture directory")
    output.mkdir(parents=True, exist_ok=False)
    (output / "Probe.csproj").write_text(PROJECT, encoding="utf8")
    (output / "Program.cs").write_text(build_source(), encoding="utf8")
    print("T4_ANDROID_POST_SAVE_FIXTURE synthetic_only=true original_game_code_written=false")


if __name__ == "__main__":
    main()
