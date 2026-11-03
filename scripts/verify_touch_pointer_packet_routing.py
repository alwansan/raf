"""Execute the actual AndroidTouchPointer.OnEvent body with deterministic Unity event doubles.

Verifies second-finger raw TouchState routing while primary finger remains on UGUI.
The harness extracts production C# verbatim; it does not execute Unity or Android.
"""
from pathlib import Path
import argparse
import shutil


def extract_method(source, signature):
    if source.count(signature) != 1:
        raise ValueError("Ambiguous production OnEvent")
    start = source.index(signature)
    opening = source.index("{", start)
    depth = 0
    for end in range(opening, len(source)):
        if source[end] == "{":
            depth += 1
        elif source[end] == "}":
            depth -= 1
            if depth == 0:
                return source[start:end + 1]
    raise ValueError("Unclosed production OnEvent method")


HARNESS = r"""
using System;
using System.Collections.Generic;
using RaftAndroid.Platform;

struct Vector2 {
    public float x, y;
    public Vector2(float x, float y) { this.x=x; this.y=y; }
}
enum TouchPhase { None, Began, Moved, Stationary, Ended, Canceled }
struct TouchState {
    public int touchId;
    public Vector2 position;
    public TouchPhase phase;
}
class StateEvent {}
class Mouse { public bool added = true; }
static class Input { public static bool simulateMouseWithTouches; }
static class InputSystem {
    public static Action<InputEventPtr,InputDevice> onEvent;
    public static Action onBeforeUpdate;
    public static T AddDevice<T>(string name) where T:new() {return new T();}
    public static void RemoveDevice(Mouse m) { m.added = false; }
}
namespace RaftAndroid.Diagnostics {
    static class AndroidRuntimeLog {
        public static void Write(string category,string name,string detail) {}
    }
}
class InputEventPtr {
    public bool handled, isState=true, isTouchState=true, readable=true;
    public double time;
    public TouchState raw, primary;
    public bool IsA<T>() where T: class { return isState && typeof(T) == typeof(StateEvent); }
}
static class StateEventReader {
    public static T GetState<T>(InputEventPtr e) where T:struct {
        if (!e.isTouchState) throw new InvalidOperationException("not a raw TouchState");
        return (T)(object)e.raw;
    }
}
class ValueControl<T> {
    readonly Func<InputEventPtr,T> value;
    public ValueControl(Func<InputEventPtr,T> selector) { value=selector; }
    public bool ReadValueFromEvent(InputEventPtr e, out T result) {
        result=value(e); return e.readable;
    }
}
class TouchControl {
    public ValueControl<int> touchId = new ValueControl<int>(e=>e.primary.touchId);
    public ValueControl<Vector2> position = new ValueControl<Vector2>(e=>e.primary.position);
    public ValueControl<TouchPhase> phase = new ValueControl<TouchPhase>(e=>e.primary.phase);
}
class InputDevice {}
class Touchscreen:InputDevice { public TouchControl primaryTouch=new TouchControl(); }
class AndroidTouchPointer {
    public readonly List<TouchPointerCommand> commands=new List<TouchPointerCommand>();
    public readonly List<string> trace=new List<string>();
    private readonly HashSet<int> uiTouches=new HashSet<int>();
    private static AndroidTouchPointer instance;
    private Mouse mouse;
    private TouchPointerButtons buttons;
    private TouchPointerGesture gesture;
    private bool suspended;
    public AndroidTouchPointer() {
        gesture=new TouchPointerGesture((cmd,x,y)=>commands.Add(cmd));
    }
    public void Enable() {OnEnable();}
    public void Disable() {OnDisable();}
    private void SetButton(bool pressed) {}
    private void Command(TouchPointerCommand cmd,float x,float y) {commands.Add(cmd);}
    private void BeforeInput() {}
    public bool Active {get{return gesture.Active;}}
    public bool Held {get{return gesture.Held;}}
    public int UiTouchCount {get{return uiTouches.Count;}}
    public void SetSuspended(bool value) {suspended=value;}
    // Deterministic fake hit test: leftmost 100px is an interactive UI zone.
    // Production OwnedUi has separately covered GraphicRaycaster source contracts.
    private bool OwnedUi(Vector2 p) {return p.x<100f;}
    public void Route(InputEventPtr input, InputDevice device) {OnEvent(input,device);}
__ENABLE_METHOD__
__DISABLE_METHOD__
__SUSPEND_METHOD__
__METHOD__
}
static class Program {
    static int checks;
    static void Require(bool condition, string name) {
        checks++;
        if (!condition) throw new InvalidOperationException("MULTITOUCH_ROUTE: "+name);
    }
    static InputEventPtr Packet(int id, float x, TouchPhase phase,
         int primaryId=0, float primaryX=0f, TouchPhase primaryPhase=TouchPhase.Stationary,
         double time=0d) {
        var p=new InputEventPtr();
        p.raw=new TouchState{touchId=id,position=new Vector2(x,12f),phase=phase};
        p.primary=primaryId==0?p.raw:
            new TouchState{touchId=primaryId,position=new Vector2(primaryX,12f),phase=primaryPhase};
        p.time=time;
        return p;
    }
    static void Main() {
        var screen=new Touchscreen();
        // UI first: primaryTouch remains finger #1; raw #2 is gameplay.
        var a=new AndroidTouchPointer();
        var u=Packet(1,20,TouchPhase.Began,time:10d);
        a.Route(u,screen);
        Require(!u.handled && a.UiTouchCount==1 && !a.Active,"first-ui-touch-preserved");
        var g=Packet(2,250,TouchPhase.Began,1,20,TouchPhase.Stationary,10.1d);
        a.Route(g,screen);
        Require(g.handled && a.Active && a.commands.Count==1 &&
            a.commands[0]==TouchPointerCommand.Move,"second-gameplay-touch-recognized");
        var moved=Packet(2,290,TouchPhase.Moved,1,20,TouchPhase.Stationary,10.2d);
        a.Route(moved,screen);
        Require(moved.handled && a.commands.Count==2 &&
            a.commands[1]==TouchPointerCommand.Move,"second-gameplay-move");
        var end=Packet(2,290,TouchPhase.Ended,1,20,TouchPhase.Stationary,10.3d);
        a.Route(end,screen);
        Require(end.handled && !a.Active && a.commands.Count==3 &&
            a.commands[2]==TouchPointerCommand.Tap,"second-gameplay-short-tap");
        var ux=Packet(1,250,TouchPhase.Moved,time:10.4d);
        a.Route(ux,screen);
        Require(!ux.handled && a.UiTouchCount==1 &&
            a.commands.Count==3,"ui-sticky-on-drag-outside");
        var ue=Packet(1,250,TouchPhase.Ended,time:10.5d);
        a.Route(ue,screen);
        Require(!ue.handled && a.UiTouchCount==0 &&
            a.commands.Count==3,"ui-up-not-synthesized");

        // Gameplay first, then second finger over UGUI: UGUI input is left intact.
        var b=new AndroidTouchPointer();
        var first=Packet(3,350,TouchPhase.Began,time:20d);
        b.Route(first,screen);
        Require(first.handled && b.Active,"first-gameplay-owned");
        var secondUi=Packet(4,30,TouchPhase.Began,3,350,TouchPhase.Stationary,20.1d);
        b.Route(secondUi,screen);
        Require(!secondUi.handled && b.UiTouchCount==1 && b.Active,
            "secondary-ui-touch-preserved");
        var secondUiEnd=Packet(4,320,TouchPhase.Ended,3,350,TouchPhase.Stationary,20.2d);
        b.Route(secondUiEnd,screen);
        Require(!secondUiEnd.handled && b.UiTouchCount==0 && b.Active,
            "secondary-ui-sticky-up");
        var gameEnd=Packet(3,350,TouchPhase.Ended,time:20.3d);
        b.Route(gameEnd,screen);
        Require(gameEnd.handled && !b.Active, "primary-gameplay-can-end");

        // Non-touch full-state fallback keeps the former primaryTouch path.
        var c=new AndroidTouchPointer();
        var full=Packet(6,350,TouchPhase.Began,time:30d);
        full.isTouchState=false;
        c.Route(full,screen);
        Require(full.handled && c.Active,"non-touchstate-primary-fallback");
        var unrelated=Packet(7,370,TouchPhase.Began,time:30.1d);
        unrelated.isState=false;
        c.Route(unrelated,screen);
        Require(!unrelated.handled,"non-state-is-ignored");
        var already=Packet(8,380,TouchPhase.Began,time:30.2d);
        already.handled=true;
        c.Route(already,screen);
        Require(already.handled && c.commands.Count==1,"handled-event-not-replayed");

        // A suspended session consumes gamepad input without creating clicks.
        var d=new AndroidTouchPointer();
        d.SetSuspended(true);
        var paused=Packet(9,400,TouchPhase.Began,time:40d);
        d.Route(paused,screen);
        Require(paused.handled && !d.Active && d.commands.Count==0,
            "pause-keeps-gesture-released");
        // Exact production enable/disable/suspend lifecycle. Re-enabling the
        // same Unity component must not remain latched in suspended mode.
        var e=new AndroidTouchPointer();
        e.Enable();
        var firstLifecycle=Packet(10,420,TouchPhase.Began,time:50d);
        e.Route(firstLifecycle,screen);
        Require(firstLifecycle.handled && e.Active,"reenable-first-activation");
        e.Disable();
        Require(!e.Active,"reenable-disables-old-gesture");
        int oldCommands=e.commands.Count;
        e.Enable();
        var again=Packet(11,430,TouchPhase.Began,time:60d);
        e.Route(again,screen);
        Require(again.handled && e.Active && e.commands.Count==oldCommands+1 &&
            e.commands[e.commands.Count-1]==TouchPointerCommand.Move,
            "reenable-clears-stale-suspension");
        e.Disable();
        Console.WriteLine("RAFT_TOUCH_RAW_PACKET_ROUTING checks="+checks+
            " primaryUiSecondaryGameplay=true secondaryUiPreserved=true"+
            " authoredOnEventExtracted=true actualUnityDeviceExecution=false");
    }
}
""".replace("StateEvent.GetState<TouchState>(input)", "StateEventReader.GetState<TouchState>(input)")


def generate(output, root=Path(".")):
    source=(root/"android-port/Runtime/Platform/AndroidTouchPointer.cs").read_text(encoding="utf-8")
    authored=extract_method(source,"private void OnEvent(InputEventPtr input, InputDevice device)")
    enable=extract_method(source,"private void OnEnable()")
    disable=extract_method(source,"private void OnDisable()")
    suspend=extract_method(source,"private void Suspend(bool value)")
    # Extract actual authored callbacks; engine interfaces are strict CPU doubles.
    program=(HARNESS.replace("__METHOD__",authored)
             .replace("__ENABLE_METHOD__",enable)
             .replace("__DISABLE_METHOD__",disable)
             .replace("__SUSPEND_METHOD__",suspend))
    program=program.replace("StateEvent.GetState<TouchState>(input)",
                            "StateEventReader.GetState<TouchState>(input)")
    output.mkdir(parents=True, exist_ok=False)
    (output/"Program.cs").write_text(program,encoding="utf-8")
    shutil.copy2(root/"android-port/Runtime/Platform/TouchPointerGesture.cs",
                 output/"TouchPointerGesture.cs")
    shutil.copy2(root/"android-port/Runtime/Platform/TouchPointerButtons.cs",
                 output/"TouchPointerButtons.cs")
    (output/"Router.csproj").write_text(
        '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType>'
        '<TargetFramework>net8.0</TargetFramework><LangVersion>9.0</LangVersion>'
        '</PropertyGroup></Project>',encoding="utf-8")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    generate(args.output)
