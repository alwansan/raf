"""Execute emitted Android guards with test-owned FMOD doubles, without Unity."""
import argparse
from pathlib import Path
from scripts.adapt_android_render_lifetimes import isolate_player_start_emitters,isolate_player_start_fmod

SOURCE = '''class Player {
StudioEventEmitter a;
StudioEventEmitter b;
bool local; int soundA, soundB, settings, actionMove;
private void Start() {
if (local) {
a.Play();
} else {
b.Play();
}
soundA = RuntimeManager.CreateInstance(1);
soundB = RuntimeManager.CreateInstance(2);
settings = 1;
actionMove = 1;
}
public static void Main() {
int checks = 0;
foreach (bool local in new[] {false,true})
foreach (int failure in new[] {0,1,2,3,4}) {
var p = new Player(); p.local = local; p.a = new StudioEventEmitter(); p.b = new StudioEventEmitter();
p.a.failure = p.b.failure = failure == 1 ? 1 : failure == 4 ? 2 : 0;
RuntimeManager.failure = failure;
RaftAndroid.Diagnostics.AndroidRuntimeLog.count = 0;
try {
p.Start();
if (failure == 4 || p.settings != 1 || p.actionMove != 1) throw new Exception("Setup failed");
if (RaftAndroid.Diagnostics.AndroidRuntimeLog.count != (failure == 0 ? 0 : 1)) throw new Exception("Diagnostic failed");
} catch (InvalidOperationException) {
if (failure != 4 || p.settings != 0 || p.actionMove != 0) throw;
}
checks++;
}
Console.WriteLine("RAFT_PLAYER_AUDIO_GUARDS cases="+checks+" actualUnityOrFmodExecution=false");
}
}
'''
STUBS = '''using System;
namespace FMODUnity { class EventNotFoundException : Exception {} }
class StudioEventEmitter {
public int failure;
public void Play() {
if (failure == 1) throw new FMODUnity.EventNotFoundException();
if (failure == 2) throw new InvalidOperationException();
}
}
static class RuntimeManager {
public static int failure;
public static int CreateInstance(int id) {
if (failure == id + 1) throw new FMODUnity.EventNotFoundException();
return id;
}
}
namespace RaftAndroid.Diagnostics {
static class AndroidRuntimeLog {
public static int count;
public static void Write(string area,string name,string detail,bool critical) {count++;}
}
}
'''
def generate(output):
    transformed = isolate_player_start_emitters(isolate_player_start_fmod(SOURCE))
    output.mkdir(parents=True,exist_ok=False)
    (output/'Program.cs').write_text(STUBS+transformed)
    (output/'PlayerAudio.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><DefineConstants>UNITY_ANDROID</DefineConstants></PropertyGroup></Project>')
if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    generate(p.parse_args().output)
