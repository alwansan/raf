"""Compile the actual authored Android touch layout handle against pointer-event doubles.

This verifies per-control pointer capture, release ordering and interrupted
gestures. It does not execute Unity UI dispatch or prove device multitouch.
"""
import argparse
from pathlib import Path


def extract_handle(source):
    signature = 'public sealed class AndroidTouchLayoutHandle : MonoBehaviour,'
    if source.count(signature) != 1:
        raise ValueError('Expected exactly one authored touch layout handle')
    start = source.index(signature)
    opening = source.index('{', start)
    depth = 0
    for end in range(opening, len(source)):
        if source[end] == '{':
            depth += 1
        elif source[end] == '}':
            depth -= 1
            if depth == 0:
                return source[start:end + 1]
    raise ValueError('Unterminated authored touch layout handle')


HARNESS = r'''
using System;
using System.Reflection;

public class MonoBehaviour {}
public interface IPointerDownHandler { void OnPointerDown(PointerEventData pointer); }
public interface IDragHandler { void OnDrag(PointerEventData pointer); }
public interface IEndDragHandler { void OnEndDrag(PointerEventData pointer); }
public interface IPointerUpHandler { void OnPointerUp(PointerEventData pointer); }
public class PointerEventData
{
    public int pointerId;
    public PointerEventData(int id) { pointerId=id; }
}
public class AndroidTouchGamepadOverlay
{
    public bool Editing { get; set; }
    public int Selections, Drags, Saves;
    public void Select(string label) { Selections++; }
    public void Drag(string label, PointerEventData pointer) { Drags++; }
    public void SavePosition(string label) { Saves++; }
}
__ACTUAL_HANDLE__
class Program
{
    static int checks;
    static void Check(bool ok, string reason)
    {
        checks++; if (!ok) throw new Exception(reason);
    }
    static void Main()
    {
        var overlay = new AndroidTouchGamepadOverlay { Editing=true };
        var handle = new AndroidTouchLayoutHandle();
        handle.Bind(overlay,"Move");
        var first = new PointerEventData(101);
        var second = new PointerEventData(202);
        handle.OnDrag(first);
        Check(overlay.Drags==0,"Drag without pointer-down must be ignored");
        handle.OnPointerDown(first);
        handle.OnPointerDown(second);
        Check(overlay.Selections==1,"Second finger cannot steal captured handle");
        handle.OnDrag(second);
        Check(overlay.Drags==0,"Uncaptured finger cannot drag");
        handle.OnDrag(first);
        Check(overlay.Drags==1,"Captured finger can drag");
        handle.OnPointerUp(second);
        Check(overlay.Saves==0,"Wrong finger cannot commit");
        handle.OnPointerUp(first);
        handle.OnEndDrag(first);
        Check(overlay.Saves==1,"Pointer-up then end-drag commits exactly once");
        handle.OnPointerDown(second);
        handle.OnDrag(second);
        handle.OnEndDrag(second);
        handle.OnPointerUp(second);
        Check(overlay.Drags==2 && overlay.Saves==2,"End-drag then pointer-up commits exactly once");
        overlay.Editing=false;
        handle.OnPointerDown(first);
        handle.OnDrag(first);
        Check(overlay.Selections==2 && overlay.Drags==2,"Non-edit gameplay cannot capture or drag");
        overlay.Editing=true;
        handle.OnPointerDown(first);
        overlay.Editing=false;
        handle.OnPointerUp(first);
        Check(overlay.Saves==2,"Exiting edit mode must not save a stale gesture");
        overlay.Editing=true;
        handle.OnPointerDown(first);
        typeof(AndroidTouchLayoutHandle).GetMethod("OnDisable",
            BindingFlags.NonPublic|BindingFlags.Instance).Invoke(handle,null);
        handle.OnDrag(first);
        Check(overlay.Drags==2,"Disable must release the captured pointer");
        handle.OnPointerDown(second);
        handle.OnDrag(second);
        handle.OnPointerUp(second);
        Check(overlay.Drags==3 && overlay.Saves==3,"Handle must accept a new gesture after disable");
        Console.WriteLine("RAFT_TOUCH_DRAG_CAPTURE checks="+checks+
            " conflictingTouchesIgnored=true duplicateSaves=0 actualUnityDeviceVerified=false");
    }
}
'''


def prepare(source, output):
    handle = extract_handle(source.read_text(encoding='utf-8'))
    output.mkdir(parents=True, exist_ok=False)
    (output / 'Program.cs').write_text(HARNESS.replace('__ACTUAL_HANDLE__', handle))
    (output / 'DragCapture.csproj').write_text(
        '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType>'
        '<TargetFramework>net8.0</TargetFramework><LangVersion>9.0</LangVersion>'
        '<ImplicitUsings>disable</ImplicitUsings><Nullable>disable</Nullable>'
        '</PropertyGroup></Project>')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, default=Path(
        'android-port/Runtime/Platform/AndroidTouchGamepadOverlay.cs'))
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    prepare(args.source, args.output)
