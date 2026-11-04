"""Compile/execute transformed synthetic C# with injected failures; no Unity."""
from pathlib import Path
import subprocess
import tempfile
from scripts.blur_pixel_cleanup import protect

METHOD="""protected void ApplyPixelShader(RenderTexture target)
{
 FilterMode filterMode = target.filterMode;
 target.filterMode = FilterMode.Bilinear;
 RenderTexture temporary = RenderTexture.GetTemporary(1, 1, 0, 0);
 temporary.filterMode = FilterMode.Bilinear;
 Work(4); Work(5);
 target.filterMode = filterMode;
 RenderTexture.ReleaseTemporary(temporary);
}
"""
STUBS="""
using System;
enum FilterMode { Point, Bilinear }
class RenderTexture {
 public static int Fail, Releases; public static RenderTexture Target;
 public bool IsTarget; public int Sets; FilterMode mode;
 public RenderTexture(bool target, FilterMode initial) { IsTarget=target;mode=initial; }
 public FilterMode filterMode {
  get { return mode; }
  set {
   Sets++;
   if ((IsTarget && Sets==1 && Fail==1) ||
       (!IsTarget && Fail==3) || (IsTarget && Sets==2 && Fail==6)) throw new Exception("injected");
   mode=value;
  }
 }
 public static RenderTexture GetTemporary(int a,int b,int c,int d) {
  if(Fail==2)throw new Exception("injected");
  return new RenderTexture(false,FilterMode.Point);
 }
 public static void ReleaseTemporary(RenderTexture t) { Releases++; }
}
class Subject {
 static void Work(int phase) { if(RenderTexture.Fail==phase)throw new Exception("injected"); }
 public void Run(RenderTexture t) { ApplyPixelShader(t); }
 METHOD_PLACEHOLDER
}
class Program {
 static void Main() {
  int count=0;
  foreach(FilterMode initial in new[]{FilterMode.Point,FilterMode.Bilinear})
  for(int fail=0;fail<=6;fail++) {
   RenderTexture.Fail=fail;RenderTexture.Releases=0;
   var t=new RenderTexture(true,initial);bool threw=false;
   try { new Subject().Run(t); } catch(Exception){threw=true;}
   if(threw!=(fail!=0))throw new Exception("exception propagation");
   if(RenderTexture.Releases!=((fail==1||fail==2)?0:1))throw new Exception("cleanup count");
   if(fail!=6 && t.filterMode!=initial)throw new Exception("restore filter");
   count++;
  }
  Console.WriteLine("RAFT_BLUR_CLEANUP cases="+count+" passed; CPU stubs only");
 }
}
"""
def main():
    transformed=protect(METHOD)
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)
        (p/'test.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework></PropertyGroup></Project>')
        (p/'Program.cs').write_text(STUBS.replace('METHOD_PLACEHOLDER',transformed))
        subprocess.run(['dotnet','run','--project',str(p/'test.csproj'),'-c','Release'],check=True)
if __name__=='__main__':main()
