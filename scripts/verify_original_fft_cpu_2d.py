"""Extend private original-body harness with independent direct2D DFT comparison."""
import argparse
from pathlib import Path
from scripts.verify_original_butterfly_numeric import generate
EXTRA=r'''
 static void TwoDimensional() {
  int n=32,stages=5;double max=0;
  ButterflyFFTUtility.ComputeButterfly(n,stages,out int[][] indices,out float[][] weights);
  for(int kind=0;kind<4;kind++) {
   var input=new Complex[n*n];uint seed=98765;
   for(int y=0;y<n;y++)for(int x=0;x<n;x++) {
    if(kind==0)input[y*n+x]=(x==3&&y==5)?new Complex(1,0.5):Complex.Zero;
    else if(kind==1)input[y*n+x]=new Complex(0.3f,-0.2f);
    else if(kind==2)input[y*n+x]=new Complex(Math.Cos(2*Math.PI*(3*x+5*y)/n),Math.Sin(2*Math.PI*(3*x+5*y)/n));
    else {seed=1664525*seed+1013904223;input[y*n+x]=new Complex((float)((seed>>8)/16777216.0-0.5),0);}
   }
   var middle=new Complex[n*n];var actual=new Complex[n*n];var expected=new Complex[n*n];
   for(int y=0;y<n;y++) {
    var row=new Complex[n];for(int x=0;x<n;x++)row[x]=input[y*n+x];
    var output=OriginalCpu(row,indices,weights);
    for(int x=0;x<n;x++)middle[y*n+x]=output[x];
   }
   for(int x=0;x<n;x++) {
    var col=new Complex[n];for(int y=0;y<n;y++)col[y]=middle[y*n+x];
    var output=OriginalCpu(col,indices,weights);
    for(int y=0;y<n;y++)actual[y*n+x]=output[y];
   }
   // Direct double2D sum, not row/column decomposition.
   for(int ky=0;ky<n;ky++)for(int kx=0;kx<n;kx++)
    for(int y=0;y<n;y++)for(int x=0;x<n;x++) {
     double angle=-2*Math.PI*(kx*x+ky*y)/n;
     expected[ky*n+kx]+=input[y*n+x]*new Complex(Math.Cos(angle),Math.Sin(angle));
    }
   double error=Error(actual,expected);max=Math.Max(max,error);
   Require(error<1e-5,"original CPU row-column vs direct2D DFT");
   if(kind==3) {
    var swapped=new Complex[n*n];for(int y=0;y<n;y++)for(int x=0;x<n;x++)swapped[y*n+x]=actual[x*n+y];
    Require(Error(swapped,expected)>0.1,"negative2D transposed output");
    var normalized=(Complex[])actual.Clone();for(int i=0;i<normalized.Length;i++)normalized[i]/=n*n;
    Require(Error(normalized,expected)>0.1,"negative2D normalization");
   }
  }
  Console.WriteLine("RAFT_ORIGINAL_CPU_2D cases=4 size=32 negativeControls=2 maxRelativeL2="+max.ToString("R",System.Globalization.CultureInfo.InvariantCulture)+" actualUnityOrGpuExecution=false");
 }
'''
def build(source,output):
    generate(source,output)
    p=output/"Program.cs"
    text=p.read_text()
    marker=" static void Main() {"
    if text.count(marker)!=1: raise ValueError("Harness entrypoint changed")
    p.write_text(text.replace(marker,EXTRA+marker+"\n  TwoDimensional();",1))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();build(a.source,a.output)
