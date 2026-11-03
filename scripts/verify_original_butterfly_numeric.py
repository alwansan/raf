"""Generate PRIVATE execution of original FFT tables/CPU body against direct DFT.

No Unity, shader execution, runtime kernel-index proof or proprietary code output.
The generated directory contains original code and must never be published.
"""
import argparse
import hashlib
from pathlib import Path
from scripts.instrument_android_runtime_operations import body_bounds

PINS={
 'ButterflyFFTUtility':'e1f7b56f6dca4a29d11b6db714809bdee4d9df2ca05fb6b9f27af47b66e459e1',
 'GpuFFT':'2f866cbe58836da8260461fe6406793f35d868eba94e816e593209544b4ba704',
 'CpuFFT':'31a455c417805bccc75c66874a070a6dd2cf72b67dfc95946c0eb2a076fb881f',
}

DOUBLES='''using System;
namespace UnityEngine {
 public struct Vector2 { public float x,y; }
 public struct Color { public float r,g,b,a; }
 public static class Mathf {
  public static float Cos(float x)=>MathF.Cos(x);
  public static float Sin(float x)=>MathF.Sin(x);
 }
 public class Texture2D {
  public readonly int width,height; public readonly Color[,] pixels; readonly bool half;
  public Texture2D(int w,int h,bool quantize) {width=w;height=h;half=quantize;pixels=new Color[w,h];}
  public void SetPixel(int x,int y,Color c) {
   if(half) {c.r=(float)(Half)c.r;c.g=(float)(Half)c.g;c.b=(float)(Half)c.b;c.a=(float)(Half)c.a;}
   pixels[x,y]=c;
  }
 }
}
'''
WRAPPERS='''using UnityEngine;
class ActualEncoder {
 int _Resolution,_NumButterflies;
 public ActualEncoder(int n,int stages) {_Resolution=n;_NumButterflies=stages;}
 public void Fill(Texture2D butterfly,int[][] indices,Vector2[][] weights) {__ENCODE__}
}
class ActualCpu {
 int _Resolution;
 public ActualCpu(int n) {_Resolution=n;}
 public void Run(int[][] indices,float[][] weights,ref float[] pingPongA,ref float[] pingPongB) {__CPU__}
}
'''
HARNESS='''using System;
using System.Numerics;
using UnityEngine;
using UltimateWater;
class Tests {
 static int checks,cases;
 static double maxFloat,maxHalf,maxCpu;
 static void Require(bool value,string reason) {checks++;if(!value)throw new Exception("Numeric check failed: "+reason);}
 static Complex[] Input(int n,int kind) {
  var a=new Complex[n];uint seed=12345;
  for(int i=0;i<n;i++) {
   float re,im;
   if(kind==0){re=i==3?1:0;im=i==3?0.5f:0;}
   else if(kind==1){re=0.3f;im=-0.2f;}
   else if(kind==2){re=(float)Math.Cos(6*Math.PI*i/n);im=(float)Math.Sin(6*Math.PI*i/n);}
   else {seed=1664525*seed+1013904223;re=(float)((seed>>8)/16777216.0-0.5);seed=1664525*seed+1013904223;im=(float)((seed>>8)/16777216.0-0.5);}
   a[i]=new Complex(re,im);
  }
  return a;
 }
 // O(N^2) independent double-precision reference; negative exponent, no normalization.
 static Complex[] Dft(Complex[] a) {
  int n=a.Length;var b=new Complex[n];
  for(int k=0;k<n;k++)for(int j=0;j<n;j++) {
   double angle=-2*Math.PI*j*k/n;
   b[k]+=a[j]*new Complex(Math.Cos(angle),Math.Sin(angle));
  }
  return b;
 }
 static double Error(Complex[] a,Complex[] b) {
  double diff=0,energy=0;
  for(int i=0;i<a.Length;i++){diff+=Complex.Abs(a[i]-b[i])*Complex.Abs(a[i]-b[i]);energy+=b[i].Magnitude*b[i].Magnitude;}
  return Math.Sqrt(diff/Math.Max(1e-30,energy));
 }
 static Complex[] Replay(Complex[] input,Texture2D texture,int stages,int bank,bool reverse=false,bool conjugate=false) {
  int n=input.Length;var a=(Complex[])input.Clone();
  for(int i=0;i<stages;i++) {
   var b=new Complex[n];int row=reverse?stages-i-1:i;
   for(int k=0;k<n;k++) {
    Color c=texture.pixels[bank*n+k,row];
    int x=(int)Math.Floor(c.r*2*n)-bank*n,y=(int)Math.Floor(c.g*2*n)-bank*n;
    Require(x>=0 && x<n && y>=0 && y<n,"address bounds");
    b[k]=a[x]+new Complex(c.b,conjugate?-c.a:c.a)*a[y];
   }
   a=b;
  }
  return a;
 }
 static Complex[] OriginalCpu(Complex[] input,int[][] indices,float[][] weights) {
  int n=input.Length;int[][] scaled=new int[indices.Length][];
  for(int i=0;i<indices.Length;i++){scaled[i]=(int[])indices[i].Clone();for(int j=0;j<scaled[i].Length;j++)scaled[i][j]*=12;}
  float[] a=new float[n*12],b=new float[n*12];
  // Original complex lane at offsets8/9 follows the conventional multiply.
  for(int i=0;i<n;i++){a[12*i+8]=(float)input[i].Real;a[12*i+9]=(float)input[i].Imaginary;}
  new ActualCpu(n).Run(scaled,weights,ref a,ref b);
  var output=new Complex[n];for(int i=0;i<n;i++)output[i]=new Complex(a[12*i+8],a[12*i+9]);
  return output;
 }
 static void Main() {
  foreach(int n in new[]{32,64,128,256,512}) {
   int stages=0;while((1<<stages)<n)stages++;
   ButterflyFFTUtility.ComputeButterfly(n,stages,out int[][] indices,out Vector2[][] vectors);
   ButterflyFFTUtility.ComputeButterfly(n,stages,out int[][] cpuIndices,out float[][] weights);
   var full=new Texture2D(2*n,stages,false);var half=new Texture2D(2*n,stages,true);
   new ActualEncoder(n,stages).Fill(full,indices,vectors);new ActualEncoder(n,stages).Fill(half,indices,vectors);
   for(int i=0;i<stages;i++)for(int k=0;k<n;k++) {
    Require(weights[i][2*k]==vectors[i][k].x && weights[i][2*k+1]==vectors[i][k].y,"weight overload identity");
    Require(indices[i][2*k]==cpuIndices[i][2*k] && indices[i][2*k+1]==cpuIndices[i][2*k+1],"index overload identity");
    for(int bank=0;bank<2;bank++) {
     Color c=full.pixels[bank*n+k,i],h=half.pixels[bank*n+k,i];
     Require(c.r==h.r && c.g==h.g,"binary16 address exactness");
     Require(c.r*2*n==indices[stages-i-1][2*k]+bank*n+0.5f,"first encoded index");
     Require(c.g*2*n==indices[stages-i-1][2*k+1]+bank*n+0.5f,"second encoded index");
    }
   }
   for(int kind=0;kind<4;kind++) {
    Complex[] input=Input(n,kind),reference=Dft(input);
    double cpuError=Error(OriginalCpu(input,cpuIndices,weights),reference);maxCpu=Math.Max(maxCpu,cpuError);
    Require(cpuError<1e-5,"actual CPU FFT vs DFT");
    for(int bank=0;bank<2;bank++) {
     double fullError=Error(Replay(input,full,stages,bank),reference),halfError=Error(Replay(input,half,stages,bank),reference);
     maxFloat=Math.Max(maxFloat,fullError);maxHalf=Math.Max(maxHalf,halfError);
     Require(fullError<1e-5,"float table vs DFT");Require(halfError<0.003,"binary16 table error budget");cases++;
    }
   }
   if(n==32) {
    Complex[] input=Input(n,3),reference=Dft(input);
    Require(Error(Replay(input,full,stages,0,true),reference)>0.1,"negative control reversed stages");
    Require(Error(Replay(input,full,stages,0,false,true),reference)>0.1,"negative control reversed sign");
    var normalized=Replay(input,full,stages,0);for(int k=0;k<n;k++)normalized[k]/=n;
    Require(Error(normalized,reference)>0.1,"negative control normalization");
   }
  }
  Console.WriteLine("RAFT_ORIGINAL_BUTTERFLY_NUMERIC cases="+cases+" checks="+checks+" maxFloatRelativeL2="+maxFloat.ToString("R",System.Globalization.CultureInfo.InvariantCulture)+" maxHalfRelativeL2="+maxHalf.ToString("R",System.Globalization.CultureInfo.InvariantCulture)+" maxOriginalCpuRelativeL2="+maxCpu.ToString("R",System.Globalization.CultureInfo.InvariantCulture)+" negativeControls=3 direction=negativeExponent normalization=none actualUnityOrGpuExecution=false");
 }
}
'''


def generate(source,output):
    if output.exists() or output.resolve().is_relative_to(source.resolve()):raise ValueError('Private harness output must be new and outside source')
    texts={}
    for name,expected in PINS.items():
        paths=list(source.rglob(name+'.cs'))
        if len(paths)!=1 or paths[0].is_symlink() or paths[0].stat().st_size>200000:raise ValueError('Original numeric source missing or ambiguous')
        text=paths[0].read_text(encoding='utf-8-sig').replace('\r\n','\n')
        if hashlib.sha256(text.encode()).hexdigest()!=expected:raise ValueError('Original numeric source fingerprint mismatch')
        texts[name]=text
    a,b=body_bounds(texts['GpuFFT'],'protected virtual void FillButterflyTexture(Texture2D butterfly, int[][] indices, Vector2[][] weights)')
    c,d=body_bounds(texts['CpuFFT'],'private void FFT(int[][] indices, float[][] weights, ref float[] pingPongA, ref float[] pingPongB)')
    output.mkdir(parents=True,exist_ok=False)
    (output/'OriginalUtilityPrivate.cs').write_text(texts['ButterflyFFTUtility'])
    (output/'ActualBodiesPrivate.cs').write_text(WRAPPERS.replace('__ENCODE__',texts['GpuFFT'][a:b]).replace('__CPU__',texts['CpuFFT'][c:d]))
    (output/'UnityDoubles.cs').write_text(DOUBLES)
    (output/'Program.cs').write_text(HARNESS)
    (output/'Numeric.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><LangVersion>9.0</LangVersion></PropertyGroup></Project>')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();generate(a.source,a.output)
