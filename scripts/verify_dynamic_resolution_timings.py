"""Execute the privately adapted original resolution algorithm with timing doubles."""
import argparse
from pathlib import Path
from scripts.adapt_android_render_lifetimes import adapt

STUBS = '''namespace UnityEngine {
public class MonoBehaviour {}
public struct FrameTiming {
public double gpuFrameTime;
public ulong cpuTimeFrameComplete, cpuTimePresentCalled;
}
public static class FrameTimingManager {
public static uint returned = 1;
public static int reads,captures;
public static FrameTiming sample;
public static void CaptureFrameTimings() {captures++;}
public static uint GetLatestTimings(uint count, FrameTiming[] frames) {
reads++;
// Retain a stale value when Unity returns no sample, as a persistent array can.
if (returned != 0) frames[0] = sample;
return returned;
}
}
public static class ScalableBufferManager {
public static int calls;
public static void ResizeBuffers(float x,float y) {calls++;}
}
public static class Mathf {
public static float Max(float a,float b) => System.Math.Max(a,b);
public static float Min(float a,float b) => System.Math.Min(a,b);
public static float Clamp(float v,float min,float max) => Min(max,Max(min,v));
public static float Lerp(float a,float b,float t) => a+(b-a)*Clamp(t,0,1);
}
}
'''
HARNESS = '''using System;
using System.Reflection;
using UnityEngine;
class Tests {
static int checks;
static readonly BindingFlags Flags = BindingFlags.Instance|BindingFlags.NonPublic;
static void Require(bool v) {checks++; if (!v) throw new Exception("Timing guard failure "+checks);}
static void Set(DynamicResolution p,string n,object v) {typeof(DynamicResolution).GetField(n,Flags).SetValue(p,v);}
static void Run(DynamicResolution p) {typeof(DynamicResolution).GetMethod("DetermineResolution",Flags).Invoke(p,null);}
static DynamicResolution Setup(double gpu,uint returned) {
var p = new DynamicResolution();
Set(p,"m_frameCount",1u);
Set(p,"frameTimings",new[]{new FrameTiming {gpuFrameTime=40,cpuTimeFrameComplete=2,cpuTimePresentCalled=1}});
DynamicResolution.m_widthScale = DynamicResolution.m_heightScale = 0.7f;
DynamicResolution.m_scaleRaiseCounter = 359;
FrameTimingManager.returned = returned;
FrameTimingManager.reads = FrameTimingManager.captures = 0;
FrameTimingManager.sample = new FrameTiming {gpuFrameTime=gpu,cpuTimeFrameComplete=2,cpuTimePresentCalled=1};
return p;
}
static void Main() {
foreach (double gpu in new[]{0.0,-1.0,double.NaN,double.PositiveInfinity,double.NegativeInfinity}) {
var p=Setup(gpu,1); Run(p);
Require(DynamicResolution.m_widthScale==0.7f && DynamicResolution.m_heightScale==0.7f);
Require(DynamicResolution.m_scaleRaiseCounter==359);
Require(FrameTimingManager.reads==1 && FrameTimingManager.captures==1);
}
var stale=Setup(40,0);Run(stale);
Require(DynamicResolution.m_widthScale==0.7f && DynamicResolution.m_scaleRaiseCounter==359);
var slow=Setup(40,1);Run(slow);
Require(DynamicResolution.m_widthScale==0.5f && DynamicResolution.m_heightScale==0.5f);
Require(DynamicResolution.m_scaleRaiseCounter==0);
var fast=Setup(10,1);Run(fast);
Require(DynamicResolution.m_widthScale>0.7f && DynamicResolution.m_widthScale==DynamicResolution.m_heightScale);
Require(DynamicResolution.m_scaleRaiseCounter==0);
var early=Setup(40,1);Set(early,"m_frameCount",0u);Run(early);
Require(FrameTimingManager.reads==0 && FrameTimingManager.captures==0);
var unfinished=Setup(40,1);FrameTimingManager.sample.cpuTimeFrameComplete=0;Run(unfinished);
Require(DynamicResolution.m_widthScale==0.7f);
Require(ScalableBufferManager.calls==0);
Console.WriteLine("RAFT_ORIGINAL_DYNAMIC_TIMING checks="+checks+" cases=10 validScaleAlgorithmPreserved=true UnityGpuExecuted=false");
}
}
'''

def generate(root,output):
    matches=list(root.rglob('DynamicResolution.cs'))
    if len(matches)!=1:raise ValueError('Original DynamicResolution source identity unavailable/ambiguous')
    source=adapt('DynamicResolution',matches[0].read_text(encoding='utf-8-sig'))
    output.mkdir(parents=True,exist_ok=False)
    (output/'OriginalPrivate.cs').write_text(source)
    (output/'UnityDoubles.cs').write_text(STUBS)
    (output/'Program.cs').write_text(HARNESS)
    (output/'DynamicTiming.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><DefineConstants>UNITY_ANDROID</DefineConstants></PropertyGroup></Project>')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();generate(a.source,a.output)
