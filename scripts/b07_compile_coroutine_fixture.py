"""Build a synthetic compiled coroutine proof with the production B07 injector.

Never copies or prints original Raft managed source. Execute with dotnet run using
-p:DefineConstants=UNITY_ANDROID and -p:DefineConstants=NON_ANDROID separately.
"""
import argparse
from pathlib import Path

from scripts.b07_probe_original_world_callbacks import fingerprint, method_body
from scripts.b07_world_coroutine_trace import ENTRY, _instrument_pinned

SOURCE = '''using System;
using System.Collections;
public class Raft_Network {
    public IEnumerator WorldHasBeenLoaded() {
        yield return 3;
        yield return 5;
        throw new InvalidOperationException("synthetic-coroutine-failure");
    }
}
'''

SUPPORT = '''
namespace RaftAndroid.Diagnostics {
    public static class AndroidRuntimeLog {
        public static int Entries;
        public static void Write(string area, string operation, string detail, bool critical) {
            if (area != "world" || operation != "WorldHasBeenLoaded.firstMoveNext" ||
                detail != "iterator entry only" || critical)
                throw new Exception("Incorrect world coroutine probe");
            Entries++;
        }
    }
}
class Program {
    public static void Main() {
        var game = new Raft_Network();
        var iterator = game.WorldHasBeenLoaded();
        if (RaftAndroid.Diagnostics.AndroidRuntimeLog.Entries != 0)
            throw new Exception("Logged before first MoveNext");
        if (!iterator.MoveNext() || (int)iterator.Current != 3)
            throw new Exception("First yield changed");
        if (!iterator.MoveNext() || (int)iterator.Current != 5)
            throw new Exception("Second yield changed");
        bool caught = false;
        try { iterator.MoveNext(); }
        catch (InvalidOperationException ex) {
            if (ex.Message != "synthetic-coroutine-failure")
                throw new Exception("Changed iterator error");
            caught = true;
        }
        if (!caught) throw new Exception("Iterator error swallowed");
#if UNITY_ANDROID && !UNITY_EDITOR
        int expected = 1;
        string platform = "android";
#else
        int expected = 0;
        string platform = "nonandroid";
#endif
        if (RaftAndroid.Diagnostics.AndroidRuntimeLog.Entries != expected)
            throw new Exception("Wrong first MoveNext log count");
        Console.WriteLine("B07_COROUTINE_CLR_PROOF platform=" + platform +
            " yields=2 exceptionRethrown=true entries=" + expected +
            " originalGameSource=false unityOrDevice=false");
    }
}
'''

CSPROJ = '''<Project Sdk="Microsoft.NET.Sdk">
<PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework>
<LangVersion>9.0</LangVersion><EnableDefaultCompileItems>false</EnableDefaultCompileItems>
</PropertyGroup><ItemGroup><Compile Include="Fixture.cs"/></ItemGroup></Project>
'''


def build(output: Path):
    if output.is_symlink() or output.exists():
        raise ValueError("B07 synthetic output directory must not exist or be linked")
    output.mkdir(parents=True)
    body_sha = fingerprint(method_body(SOURCE, "WorldHasBeenLoaded")[1])
    adapted = _instrument_pinned(SOURCE, fingerprint(SOURCE), body_sha)
    if adapted.replace(adapted.split("#if UNITY_ANDROID")[1].split("#endif")[0], "", 1) == SOURCE:
        raise ValueError("Invalid bounded diagnostic fixture assertion")
    (output / "Fixture.cs").write_text(adapted + "\n" + SUPPORT, encoding="utf-8")
    (output / "B07Harness.csproj").write_text(CSPROJ, encoding="utf-8")
    return output / "B07Harness.csproj"


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    project = build(args.output)
    print("B07_SYNTHETIC_COROUTINE_PROJECT prepared=true originalGameSource=false project=" + project.name)
