"""Execute actual authored pointer methods with strict input/device doubles.

Tests left-button output and legacy key merging; not a Unity event-loop test.
"""
import argparse
from pathlib import Path
import shutil


def method(source, signature):
    if source.count(signature) != 1:
        raise ValueError('Ambiguous authored pointer method')
    start = source.index(signature)
    opening = source.index('{', start)
    depth = 0
    for end in range(opening, len(source)):
        if source[end] == '{': depth += 1
        elif source[end] == '}':
            depth -= 1
            if depth == 0: return source[start:end + 1]
    raise ValueError('Incomplete authored pointer method')


HARNESS = r'''
using System;
using System.Collections.Generic;
using RaftAndroid.Platform;
enum KeyCode { Mouse0, Mouse1, Mouse2, Space }
enum MouseButton { Left = 0, Right = 1 }
struct Vector2 { public float x, y; }
struct MouseState {
 public Vector2 position, delta; public int buttons;
 public MouseState WithButton(MouseButton button, bool pressed) {
  buttons = pressed ? buttons | (1 << (int)button) : buttons & ~(1 << (int)button); return this;
 }
}
class Mouse { public bool added = true; }
static class Input {
 public static bool physical;
 public static bool GetKey(KeyCode key) => physical;
 public static bool GetKeyDown(KeyCode key) => physical;
 public static bool GetKeyUp(KeyCode key) => physical;
}
static class Time { public static int frameCount = 10; }
static class InputSystem {
 public static List<MouseState> states = new List<MouseState>();
 public static void QueueStateEvent(Mouse mouse, MouseState state) { states.Add(state); }
}
class AndroidTouchPointer {
 static AndroidTouchPointer instance;
 Mouse mouse = new Mouse(); Vector2 position;
 TouchPointerButtons buttons = new TouchPointerButtons(_ => {});
 int pressedFrame = -1, releasedFrame = -1;
__METHODS__
 static int checks;
 static void Require(bool value) { checks++; if (!value) throw new Exception("Pointer mapping failed: " + checks); }
 static void Main() {
  instance = new AndroidTouchPointer();
  foreach (bool synthetic in new[] { false, true })
  foreach (bool physical in new[] { false, true })
  foreach (KeyCode key in Enum.GetValues(typeof(KeyCode))) {
   instance.buttons.Hold(synthetic); instance.pressedFrame = instance.releasedFrame = synthetic ? Time.frameCount : -1;
   Input.physical = physical;
   bool expected = physical || (key == KeyCode.Mouse0 && synthetic);
   Require(GetKey(key) == expected); Require(GetKeyDown(key) == expected); Require(GetKeyUp(key) == expected);
  }
  instance.buttons.Hold(true); instance.Send(new Vector2());
  Require(InputSystem.states.Count == 1 && InputSystem.states[0].buttons == 1);
  instance.buttons.Hold(false); instance.Send(new Vector2());
  Require(InputSystem.states[1].buttons == 0);
  instance.mouse.added = false; instance.Send(new Vector2()); Require(InputSystem.states.Count == 2);
  instance = null; Input.physical = false; Require(!GetKey(KeyCode.Mouse0));
  Input.physical = true; Require(GetKey(KeyCode.Mouse1) && GetKeyDown(KeyCode.Space) && GetKeyUp(KeyCode.Mouse2));
  Console.WriteLine("RAFT_TOUCH_POINTER_MOUSE_MAPPING checks=" + checks + " syntheticButton=left legacyKey=Mouse0 physicalDevicesPreserved=true actualUnityDeviceExecution=false");
 }
}
'''


def generate(output, root=Path('.')):
    runtime = root / 'android-port/Runtime/Platform'
    source = (runtime / 'AndroidTouchPointer.cs').read_text()
    signatures = ['private void Send(Vector2 delta)'] + [
        'public static bool ' + name + '(KeyCode key)' for name in ('GetKey', 'GetKeyDown', 'GetKeyUp')]
    actual = '\n'.join(method(source, signature) for signature in signatures)
    output.mkdir(parents=True, exist_ok=False)
    (output / 'Program.cs').write_text(HARNESS.replace('__METHODS__', actual))
    shutil.copy2(runtime / 'TouchPointerButtons.cs', output / 'TouchPointerButtons.cs')
    (output / 'Mapping.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><LangVersion>9.0</LangVersion></PropertyGroup></Project>')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    generate(a.output)
