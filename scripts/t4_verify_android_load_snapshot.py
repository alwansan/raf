"""Generate and run a source-free compiled UNITY_ANDROID Load<T> snapshot fixture.

The real original SHA-adapted Unity source and private game RGD are not shipped
in this synthetic check; the genuine original managed compile is separate.
"""
import argparse
from pathlib import Path
from scripts.instrument_android_runtime_operations import (
    trace_caught_original_load_error, wrap,
)

SIGNATURE = "public static T Load<T>(string filename)"

SYNTHETIC = """\
public sealed class SaveAndLoad
{
    public static T Load<T>(string filename)
    {
        try { return (T)Deserialize(filename); }
        catch (System.Exception) { return default(T); }
    }
    private static object Deserialize(string filename)
    {
        string content = System.IO.File.ReadAllText(filename);
        if (!content.StartsWith("ok:"))
            throw new System.IO.InvalidDataException("synthetic invalid content");
        return content.Substring(3);
    }
}
"""

HARNESS = r"""
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
            if (ThrowOnSnapshot && operation.StartsWith("Load.argumentFileSnapshot"))
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
    static void Require(bool ok)
    {
        if (!ok) throw new System.InvalidOperationException("synthetic assertion");
    }
    static string First(string prefix)
    {
        foreach (string e in RaftAndroid.Diagnostics.AndroidRuntimeLog.Events)
            if (e.StartsWith(prefix)) return e;
        throw new System.InvalidOperationException("synthetic event absent: " + prefix);
    }
    static bool Has(string marker)
    {
        foreach (string e in RaftAndroid.Diagnostics.AndroidRuntimeLog.Events)
            if (e.Contains(marker)) return true;
        return false;
    }
    static void Main()
    {
        var dir = System.IO.Path.Combine(System.IO.Path.GetTempPath(),
            "t4-load-synthetic-" + System.Guid.NewGuid().ToString("N"));
        System.IO.Directory.CreateDirectory(dir);
        string file = System.IO.Path.Combine(dir, "synthetic-not-original.rgd");
        try
        {
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Clear();
            Require(SaveAndLoad.Load<string>(file) == null);
            Require(Has("Load.caughtException"));
            Require(First("save.Load.argumentFileSnapshot|").Contains(
                "exists_at_filename_argument=False; length_class=not_checked"));

            System.IO.File.WriteAllBytes(file, new byte[0]);
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Clear();
            Require(SaveAndLoad.Load<string>(file) == null);
            Require(Has("Load.caughtException"));
            Require(First("save.Load.argumentFileSnapshot|").Contains(
                "exists_at_filename_argument=True; length_class=zero"));

            System.IO.File.WriteAllText(file, "invalid synthetic content");
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Clear();
            Require(SaveAndLoad.Load<string>(file) == null);
            Require(Has("Load.caughtException"));
            Require(First("save.Load.argumentFileSnapshot|").Contains(
                "exists_at_filename_argument=True; length_class=nonzero"));

            System.IO.File.WriteAllText(file, "ok:synthetic-value");
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Clear();
            Require(SaveAndLoad.Load<string>(file) == "synthetic-value");
            Require(!Has("Load.caughtException"));
            Require(First("save.Load.argumentFileSnapshot|").Contains(
                "exists_at_filename_argument=True; length_class=nonzero"));
            Require(First("save.Load<T>.exit|").Contains("failed=False"));

            RaftAndroid.Diagnostics.AndroidRuntimeLog.Clear();
            RaftAndroid.Diagnostics.AndroidRuntimeLog.ThrowOnSnapshot = true;
            Require(SaveAndLoad.Load<string>(file) == "synthetic-value");
            RaftAndroid.Diagnostics.AndroidRuntimeLog.ThrowOnSnapshot = false;
            Require(First("save.Load<T>.exit|").Contains("failed=False"));
            Require(!Has("Load.caughtException"));
            foreach (string item in RaftAndroid.Diagnostics.AndroidRuntimeLog.Events)
                Require(!item.Contains(file));
            System.Console.WriteLine(
                "T4_ANDROID_LOAD_SNAPSHOT synthetic_android_csharp_compiled=true" +
                " missing_file_classified=true zero_file_classified=true" +
                " corrupt_nonzero_file_classified=true successful_load_retained=true" +
                " logger_failure_nonfatal=true original_load_exception_caught=true" +
                " game_rgd_unread=true unity_il2cpp_device_unverified=true");
        }
        finally
        {
            RaftAndroid.Diagnostics.AndroidRuntimeLog.ThrowOnSnapshot = false;
            if (System.IO.Directory.Exists(dir))
                System.IO.Directory.Delete(dir, true);
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
    # Generic source operation name is Load<T>, not Load; the event marker
    # Load.argumentFileSnapshot intentionally remains non-generic.
    original_with_caught = trace_caught_original_load_error(SYNTHETIC)
    result = wrap(original_with_caught, SIGNATURE, "save", "filename")
    if result.count('"Load.argumentFileSnapshot"') != 1:
        raise ValueError("Load marker missing or duplicated")
    if result.count("System.IO.File.Exists(filename)") != 1:
        raise ValueError("Must observe only original path argument")
    if result.count('return (T)Deserialize(filename);') != 1:
        raise ValueError("Original synthetic load body changed")
    return result + "\n" + HARNESS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    output = parser.parse_args().output
    if output.exists() or output.is_symlink() or any(p.is_symlink() for p in output.parents):
        raise ValueError("Refuse existing or linked fixture output")
    output.mkdir(parents=True, exist_ok=False)
    (output / "Probe.csproj").write_text(PROJECT, encoding="utf8")
    (output / "Program.cs").write_text(build_source(), encoding="utf8")
    print("T4_ANDROID_LOAD_FIXTURE synthetic_only=true original_game_code_written=false")


if __name__ == "__main__":
    main()
