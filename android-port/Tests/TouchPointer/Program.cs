using System;
using System.Collections.Generic;
using System.Linq;
using RaftAndroid.Platform;

class Program
{
    static int checks;
    static void Require(bool condition) { checks++; if (!condition) throw new Exception("Touch pointer contract failed: " + checks); }
    static void Main()
    {
        var output = new List<(TouchPointerCommand command, float x, float y)>();
        var gesture = new TouchPointerGesture((c, x, y) => output.Add((c, x, y)));
        gesture.Begin(1, 10, 20, 0); gesture.End(1, 10, 20, 0.1, false);
        Require(output.Count(v => v.command == TouchPointerCommand.Tap) == 1 && !gesture.Active);
        Require(!output.Any(v => v.command == TouchPointerCommand.Down || v.command == TouchPointerCommand.Up));
        output.Clear();
        gesture.Begin(1, 10, 20, 1); gesture.Tick(1.499);
        Require(!gesture.Held);
        gesture.Tick(1.5); gesture.Tick(2);
        Require(gesture.Held && output.Count(v => v.command == TouchPointerCommand.Down) == 1);
        gesture.Move(1, 50, 60, 2.1); gesture.End(1, 70, 80, 2.2, false);
        Require(output.Last().command == TouchPointerCommand.Up && output.Last().x == 70 && output.Last().y == 80);
        Require(!output.Any(v => v.command == TouchPointerCommand.Tap));
        output.Clear();
        gesture.Begin(1, 0, 0, 3); gesture.End(1, 0, 0, 3.1, true);
        Require(output.Count == 1 && !gesture.Active); // cancelled short press never clicks
        output.Clear();
        gesture.Begin(1, 0, 0, 4); gesture.Tick(4.5); gesture.Cancel(); gesture.Cancel();
        Require(output.Count(v => v.command == TouchPointerCommand.Up) == 1 && !gesture.Held);
        output.Clear();
        gesture.Begin(1, 1, 2, 5); gesture.Begin(2, 9, 9, 5.1);
        gesture.Move(2, 99, 99, 5.2); gesture.End(2, 99, 99, 5.3, false);
        Require(gesture.Active && output.Count == 1);
        gesture.End(1, 3, 4, 5.4, false);
        Require(output.Last().command == TouchPointerCommand.Tap && output.Last().x == 3);
        gesture.Move(2, 100, 100, 5.5); gesture.End(2, 100, 100, 5.6, false);
        Require(output.Count == 2); // no ownership handoff to a finger already down
        output.Clear();
        gesture.Begin(3, 1, 2, 6); gesture.End(3, 1, 2, 6.7, false);
        Require(output.Select(v => v.command).SequenceEqual(new[] { TouchPointerCommand.Move, TouchPointerCommand.Down, TouchPointerCommand.Up }));
        output.Clear();
        gesture.Begin(4, float.NaN, 0, 7); gesture.Begin(4, 0, 0, double.PositiveInfinity);
        Require(!gesture.Active && output.Count == 0);
        gesture.Begin(4, 0, 0, 7); gesture.Move(4, 5, 5, 6); gesture.End(4, 5, 5, 6, false);
        Require(!gesture.Active && output.Count == 1);
        gesture.Begin(4, 0, 0, 8); gesture.Tick(8.5); gesture.End(4, float.NaN, 0, 8.6, false);
        Require(!gesture.Held && output.Last().command == TouchPointerCommand.Up);
        var transitions = new List<bool>();
        var buttons = new TouchPointerButtons(transitions.Add);
        buttons.Tap(); Require(buttons.Pressed);
        buttons.Tap(); buttons.Tap();
        buttons.BeginUpdate(); Require(!buttons.Pressed);
        buttons.BeginUpdate(); Require(buttons.Pressed);
        buttons.BeginUpdate(); buttons.BeginUpdate(); buttons.BeginUpdate();
        Require(transitions.SequenceEqual(new[] { true, false, true, false, true, false }));
        buttons.Hold(true); buttons.BeginUpdate(); buttons.BeginUpdate(); Require(buttons.Pressed);
        buttons.Hold(false); Require(!buttons.Pressed);
        buttons.Tap(); buttons.Tap(); buttons.Cancel(); buttons.BeginUpdate(); buttons.BeginUpdate();
        Require(!buttons.Pressed && transitions.Last() == false);
        checks += BoundaryMatrix.Run();
        Console.WriteLine("RAFT_TOUCH_POINTER_GESTURE checks=" + checks + " holdMilliseconds=500 passed=true actualUnityDeviceExecution=false");
    }
}
