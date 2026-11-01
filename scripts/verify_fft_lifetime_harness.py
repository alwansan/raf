"""Exercise the actual original/adapted FFT body against bounded resource/API doubles."""
import argparse
from pathlib import Path
from scripts.adapt_android_render_lifetimes import adapt
from scripts.instrument_android_runtime_operations import body_bounds

STUBS='''using System;
class Texture { public int height=8; }
class RenderTexture:Texture { public bool enableRandomWrite; public bool IsCreated()=>false; public void Create(){} }
class TemporaryRenderTexture { public static int Live; public TemporaryRenderTexture(){Live++;} public void Dispose(){Live--;} public static implicit operator RenderTexture(TemporaryRenderTexture x)=>new RenderTexture(); }
class Cache { public TemporaryRenderTexture GetTemporary()=>new TemporaryRenderTexture(); }
class Shader { public static bool FailSet,FailDispatch; public void SetTexture(int i,string n,Texture t){if(FailSet)throw new InvalidOperationException();} public void Dispatch(int i,int x,int y,int z){if(FailDispatch)throw new InvalidOperationException();} }
class Candidate { Cache _RenderTexturesSet=new Cache(); Shader _Shader=new Shader(); int _KernelIndex=6; Texture Butterfly=new Texture(); public void ComputeFFT(Texture tex,RenderTexture target) { /*__RAFT_BODY__*/ } }
class Program { static void Main(){ var c=new Candidate(); Shader.FailSet=true; for(int i=0;i<10000;i++){try{c.ComputeFFT(new Texture(),new RenderTexture());throw new Exception("Expected kernel failure");}catch(InvalidOperationException){} if(TemporaryRenderTexture.Live!=0)throw new Exception("FFT temporary leaked after SetTexture failure");} Shader.FailSet=false;Shader.FailDispatch=true;try{c.ComputeFFT(new Texture(),new RenderTexture());}catch(InvalidOperationException){} if(TemporaryRenderTexture.Live!=0)throw new Exception("FFT temporary leaked after Dispatch failure"); Shader.FailDispatch=false;c.ComputeFFT(new Texture(),new RenderTexture());if(TemporaryRenderTexture.Live!=0)throw new Exception("Successful FFT leaked temporary");Console.WriteLine("RAFT_ACTUAL_FFT_BODY_LIFETIME failures=10001 success=1 leaked=0 GPUExecution=false");} }
'''

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    matches=list(a.source.rglob('Dx11FFT.cs'))
    if len(matches)!=1:raise ValueError('Original FFT source ambiguous')
    text=adapt('Dx11FFT',matches[0].read_text(encoding='utf-8-sig'))
    start,end=body_bounds(text,'public override void ComputeFFT(Texture tex, RenderTexture target)')
    a.output.mkdir(parents=True,exist_ok=False)
    (a.output/'Program.cs').write_text(STUBS.replace('/*__RAFT_BODY__*/',text[start:end]))
    (a.output/'Harness.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><LangVersion>9.0</LangVersion></PropertyGroup></Project>')

if __name__=='__main__':main()
