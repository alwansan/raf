"""Create a tiny synthetic CLR coroutine harness using production T4 injection.

No original game source/binaries, source pin override, or Unity runtime involved.
"""
import argparse
from pathlib import Path
import runpy

from scripts.instrument_android_runtime_operations import trace_original_world_completion

PROJECT = """<Project Sdk="Microsoft.NET.Sdk">
<PropertyGroup>
<OutputType>Exe</OutputType>
<TargetFramework>net10.0</TargetFramework>
<DefineConstants>UNITY_ANDROID</DefineConstants>
<ImplicitUsings>enable</ImplicitUsings>
<Nullable>disable</Nullable>
</PropertyGroup>
</Project>
"""

SHIMS = r"""
public static class Helper {
    public static void BroadCastToScene(int id) {}
}
namespace RaftAndroid.Diagnostics {
    public static class AndroidRuntimeLog {
        public static System.Collections.Generic.List<string> Events = new();
        public static void Write(string area, string eventName, string detail, bool important) {
            Events.Add(eventName);
        }
    }
}
public class Program {
    static void Require(bool value, string what) {
        if (!value) throw new System.Exception(what);
    }
    public static void Main() {
        int verified = 0;
        foreach (bool ready in new bool[] { false, true }) {
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Events.Clear();
            var game = new Raft_Network() { ready = ready };
            var coro = game.WorldHasBeenLoaded();
            Require(!game.WorldHasBeenRecieved, "Iterator constructed a ready world");
            Require(RaftAndroid.Diagnostics.AndroidRuntimeLog.Events.Count == 0, "Eager tracing");
            Require(coro.MoveNext(), "Iterator first move lost");
            var logs = RaftAndroid.Diagnostics.AndroidRuntimeLog.Events;
            int actual = logs.FindAll(x => x == "WorldHasBeenLoaded.originalCompletionAssigned").Count;
            int entry = logs.FindAll(x => x == "WorldHasBeenLoaded.firstMoveNext").Count;
            Require(actual == (ready ? 1 : 0), "Completion trace fired on wrong branch");
            Require(entry == 1, "First-MoveNext trace changed");
            Require(game.WorldHasBeenRecieved == ready, "Original ready flag semantics changed");
            Require(!coro.MoveNext(), "Original iterator was not exhausted");
            Require(logs.FindAll(x => x == "WorldHasBeenLoaded.originalCompletionAssigned").Count == actual,
                    "Completion trace repeated");
            verified++;
        }
        System.Console.WriteLine("T4_CLR_COROUTINE_SEMANTICS branches=" + verified +
            " falseCompletion=0 trueCompletion=1 yieldsPreserved=true device=false");
    }
}
"""


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", type=Path, required=True)
    args = cli.parse_args()
    # Source-free fixture is already bounded by T4's adversarial tests.
    fixture = runpy.run_path("tests/test_t4_world_completion_trace.py")["ORIGINAL"]
    traced = trace_original_world_completion(fixture)
    target = "class Raft_Network {\n"
    if traced.count(target) != 1:
        raise ValueError("Synthetic network class structure changed")
    traced = traced.replace(target,
        "class Raft_Network {\n"
        " public bool ready;\n"
        " public bool WorldHasBeenRecieved;\n"
        " public void RecoverWithoutChangingWorldFlag() { }\n", 1)
    if traced.count("WorldHasBeenLoaded.originalCompletionAssigned") != 1:
        raise ValueError("Completion trace not exactly once")
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "T4WorldCompletion.csproj").write_text(PROJECT, encoding="utf-8")
    (args.output / "Program.cs").write_text(traced + "\n" + SHIMS, encoding="utf-8")
    print("T4_CLR_FIXTURE_GENERATED source_free=true original_data=false")


if __name__ == "__main__":
    main()
