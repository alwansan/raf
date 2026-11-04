"""B07: build a *synthetic* managed C# harness from the production callback adapter.

This runs real CLR try/rethrow/finally semantics without including any original
Raft source, decompiled C# or device state. It is NOT Unity/IL2CPP evidence.
"""
import argparse
from pathlib import Path
from scripts.b07_probe_original_world_callbacks import fingerprint, method_body
from scripts.instrument_android_runtime_operations import instrument


SOURCE = '''using System;
public class GameManager {
    public int Branch;
    public int Calls;
    public bool Fail;
    private void SaveGame(bool sendRemoteMessage) {
        Calls++;
        if (Fail) throw new InvalidOperationException("synthetic-world-save-failure");
    }
    public void OnWorldRecieved() {
        if (Branch == 0) SaveGame(true);
        else if (Branch == 1) SaveGame(false);
        else SaveGame(true);
    }
}
'''

SUPPORT = '''
namespace RaftAndroid.Diagnostics {
    public static class AndroidRuntimeLog {
        public static int BeginCount;
        public static int EndCount;
        public static int ExceptionCount;
        public static int FailureCount;
        public static long BeginOperation(string area, string method, string detail) {
            if (area != "world" || method != "OnWorldRecieved") throw new Exception("Wrong area");
            BeginCount++;
            return 7;
        }
        public static void EndOperation(string area, string method, long start, bool failed) {
            if (area != "world" || method != "OnWorldRecieved" || start != 7)
                throw new Exception("Wrong end context");
            EndCount++;
            if (failed) FailureCount++;
        }
        public static void Write(string area, string operation, string details, bool critical) {
            if (area != "world" || operation != "OnWorldRecieved.exception" || !critical)
                throw new Exception("Wrong error context");
            ExceptionCount++;
        }
    }
}
class Program {
    public static void Main() {
        for (int branch = 0; branch < 3; branch++) {
            var g = new GameManager { Branch = branch, Fail = (branch == 2) };
            bool failed = false;
            try { g.OnWorldRecieved(); }
            catch (InvalidOperationException ex) {
                if (ex.Message != "synthetic-world-save-failure")
                    throw new Exception("Changed original failure");
                failed = true;
            }
            if (failed != (branch == 2) || g.Calls != 1)
                throw new Exception("Lost SaveGame branch or exception");
        }
        if (RaftAndroid.Diagnostics.AndroidRuntimeLog.BeginCount != 3 ||
            RaftAndroid.Diagnostics.AndroidRuntimeLog.EndCount != 3 ||
            RaftAndroid.Diagnostics.AndroidRuntimeLog.ExceptionCount != 1 ||
            RaftAndroid.Diagnostics.AndroidRuntimeLog.FailureCount != 1)
            throw new Exception("Operation logging lost or exception swallowed");
        Console.WriteLine("B07_WORLD_CALLBACK_MANAGED_EXECUTED branches=3 saved=3 begin=3 end=3 caught=1 finally_failed=1 originalSourceUsed=false unityOrDevice=false");
    }
}
'''

CSPROJ = '''<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>
<OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework>
<LangVersion>9.0</LangVersion><DefineConstants>UNITY_ANDROID</DefineConstants>
<EnableDefaultCompileItems>false</EnableDefaultCompileItems>
</PropertyGroup><ItemGroup><Compile Include="Callback.cs"/></ItemGroup></Project>
'''


def build(output: Path):
    if output.is_symlink() or output.exists():
        raise ValueError("B07 synthetic output must be absent and not linked")
    output.mkdir(parents=True)
    body_sha = fingerprint(method_body(SOURCE, "OnWorldRecieved")[1])
    manifest = {
        "sources": {"GameManager": {
            "sha256": fingerprint(SOURCE),
            "area": "world",
            "methods": [{"name": "OnWorldRecieved", "body_sha256": body_sha}],
        }}
    }
    adapted = instrument("GameManager", SOURCE, manifest)
    if adapted.count("SaveGame(") != SOURCE.count("SaveGame("):
        raise ValueError("Synthetic branch callsite mutated")
    (output / "Callback.cs").write_text(adapted + "\n" + SUPPORT, encoding="utf-8")
    (output / "B07Harness.csproj").write_text(CSPROJ, encoding="utf-8")
    return output / "B07Harness.csproj"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    p = build(args.output)
    print("B07_SYNTHETIC_CALLBACK_PROJECT generated=true originalSourceUsed=false project=" + p.name)
