"""Run the actual authored path-restore body against a strict registration double.

Input System 1.7.0 OnScreenControl's active controlPath setter always calls
SetupInputControl. The double rejects duplicate registration and models enable
callbacks; this is not an actual Unity device/PlayerInput or pointer test.
"""
import argparse
from pathlib import Path


def extract_method(source):
    signature='private static void ApplyControlPath(OnScreenControl widget, string path)'
    if source.count(signature)!=1: raise ValueError('Expected one real runtime path guard')
    start=source.index(signature);opening=source.index('{',start);depth=0
    for end in range(opening,len(source)):
        if source[end]=='{':depth+=1
        elif source[end]=='}':
            depth-=1
            if depth==0:return source[start:end+1].replace('private static','public static',1)
    raise ValueError('Unterminated runtime method')


HARNESS=r'''
using System;

// State-contract double for the inspected 1.7.0 vendor setter + enable lifecycle.
// No Unity runtime or actual input actions are simulated as passing here.
class OnScreenControl
{
    string path;
    bool enabledValue=true, hierarchyActive;
    public int Registrations, Setups, Cleanups, Writes;
    public bool ThrowOnWrite;
    public bool enabled
    {
        get { return enabledValue; }
        set
        {
            bool before=isActiveAndEnabled;
            enabledValue=value;
            Transition(before);
        }
    }
    public bool isActiveAndEnabled { get { return enabledValue && hierarchyActive; } }
    public string controlPath
    {
        get { return path; }
        set
        {
            Writes++;
            if (ThrowOnWrite) throw new InvalidOperationException("Injected path-write failure");
            path=value;
            // Mirrors the inspected vendor setter's unconditional active setup.
            if (isActiveAndEnabled) SetupInputControl();
        }
    }
    public OnScreenControl(string initial, bool active=true, bool componentEnabled=true)
    {
        path=initial; hierarchyActive=active; enabledValue=componentEnabled;
        if (isActiveAndEnabled) SetupInputControl();
    }
    void SetupInputControl()
    {
        if (Registrations!=0) throw new InvalidOperationException("Duplicate registration");
        Registrations++;Setups++;
    }
    void Transition(bool before)
    {
        if (before && !isActiveAndEnabled) { Registrations--;Cleanups++; }
        else if (!before && isActiveAndEnabled) SetupInputControl();
    }
    public void SetActive(bool active)
    {
        bool before=isActiveAndEnabled;hierarchyActive=active;Transition(before);
    }
}
class RuntimeGuard
{
__ACTUAL_METHOD__
}
class Program
{
    static int checks;
    static void Check(bool condition, string message)
    {
        checks++; if (!condition) throw new Exception(message);
    }
    static void Main()
    {
        var vendor=new OnScreenControl("A");
        bool rejected=false;
        try { vendor.controlPath="A"; } catch(InvalidOperationException) { rejected=true; }
        Check(rejected,"Negative control must reproduce the active vendor-setter precondition");

        var same=new OnScreenControl("A");
        for(int i=0;i<1001;i++) RuntimeGuard.ApplyControlPath(same,"A");
        Check(same.Writes==0 && same.Setups==1 && same.Cleanups==0 && same.Registrations==1,"Repeated restore must be a no-op");

        var active=new OnScreenControl("A");
        for(int i=0;i<1001;i++)
        {
            string path=(i%2==0)?"B":"A";
            RuntimeGuard.ApplyControlPath(active,path);
            Check(active.Registrations==1 && active.enabled && active.controlPath==path,"Active path change must unregister/re-register exactly once");
        }
        Check(active.Setups==1002 && active.Cleanups==1001,"No registration leases may accumulate");

        var disabled=new OnScreenControl("A",true,false);
        RuntimeGuard.ApplyControlPath(disabled,"B");
        Check(!disabled.enabled && disabled.Registrations==0 && disabled.Setups==0 && disabled.controlPath=="B","Edit-mode control must remain disabled");
        RuntimeGuard.ApplyControlPath(disabled,"B");
        Check(disabled.Writes==1,"Disabled same-path restore must be a no-op too");

        var inactive=new OnScreenControl("A",false);
        RuntimeGuard.ApplyControlPath(inactive,"B");
        Check(inactive.enabled && inactive.Registrations==0 && inactive.Setups==0,"Inactive hierarchy must not create a device");
        inactive.SetActive(true);
        Check(inactive.Setups==1 && inactive.Registrations==1,"First visible activation must register once");

        var failing=new OnScreenControl("A");failing.ThrowOnWrite=true;
        rejected=false;
        try { RuntimeGuard.ApplyControlPath(failing,"B"); } catch(InvalidOperationException) { rejected=true; }
        Check(rejected && failing.enabled && failing.controlPath=="A" && failing.Registrations==1,"Exception must propagate and restore enabled state");

        var failingDisabled=new OnScreenControl("A",true,false);failingDisabled.ThrowOnWrite=true;
        rejected=false;
        try { RuntimeGuard.ApplyControlPath(failingDisabled,"B"); } catch(InvalidOperationException) { rejected=true; }
        Check(rejected && !failingDisabled.enabled && failingDisabled.Registrations==0,"Failure must not enable an editing control");
        Console.WriteLine("RAFT_TOUCH_BINDING_LIFECYCLE checks="+checks+" repeatedRestores=1001 activeRemaps=1001 duplicateRegistrations=0 actualUnityDeviceVerified=false");
    }
}
'''


def prepare(source, output):
    method=extract_method(source.read_text())
    output.mkdir(parents=True,exist_ok=False)
    (output/'Program.cs').write_text(HARNESS.replace('__ACTUAL_METHOD__',method))
    (output/'Lifecycle.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><LangVersion>9.0</LangVersion><ImplicitUsings>disable</ImplicitUsings><Nullable>disable</Nullable></PropertyGroup></Project>')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=Path('android-port/Runtime/Platform/AndroidTouchGamepadOverlay.cs'))
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();prepare(args.source,args.output)
