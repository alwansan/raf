"""Execute transformed authentic original Blur method using CPU Unity API stubs."""
import argparse,hashlib,subprocess,tempfile
from pathlib import Path
from scripts.blur_pixel_cleanup import protect
from scripts.verify_blur_pixel_cleanup_cpu import STUBS
PIN="f03ff7a771e866a84591daf030c2648029efb15851bd63b3df0bc7a67dd8c08f"
def main(root):
 paths=list(root.rglob("Blur.cs"))
 if len(paths)!=1:raise ValueError("ambiguous original Blur")
 source=paths[0].read_text(encoding="utf-8-sig").replace("\r\n","\n")
 observed=hashlib.sha256(source.encode()).hexdigest()
 print("RAFT_ORIGINAL_BLUR_SOURCE sha256="+observed)
 if observed!=PIN:raise ValueError("original Blur source pin differs; refuse guessed transformation")
 changed=protect(source)
 signature="protected void ApplyPixelShader(RenderTexture target)"
 at=changed.index(signature);opening=changed.index("{",at);end=opening+1;depth=1
 while depth:
  depth+=(changed[end]=="{")-(changed[end]=="}");end+=1
 method=changed[at:end]
 stubs=STUBS.replace("public bool IsTarget;","public int width=16,height=16,format=0; public string name; public static int Draws; public bool IsTarget;")
 stubs=stubs.replace("RenderTexture.Fail=fail;RenderTexture.Releases=0;","RenderTexture.Fail=fail;RenderTexture.Releases=0;RenderTexture.Draws=0;")
 stubs=stubs.replace("class Subject {","class Material { public void SetVector(int key,Vector4 value){} }\nstruct Vector4 { public Vector4(float a,float b,float c,float d){} }\nstatic class ShaderVariables { public static int Offset=0; }\nstatic class Graphics { public static void Blit(RenderTexture a,RenderTexture b,Material m,int pass) { RenderTexture.Draws++; if((RenderTexture.Fail==4&&RenderTexture.Draws==1)||(RenderTexture.Fail==5&&RenderTexture.Draws==2))throw new Exception(\"injected\"); } }\nclass Subject { Material BlurMaterial=new Material(); int _Iterations=2,_PassIndex=0;float _Size=0.005f;")
 stubs=stubs.replace("count++;","if(fail==0 && RenderTexture.Draws!=4)throw new Exception(\"original iteration order\");count++;")
 with tempfile.TemporaryDirectory() as d:
  p=Path(d);(p/"test.csproj").write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework></PropertyGroup></Project>')
  (p/"Program.cs").write_text(stubs.replace("METHOD_PLACEHOLDER",method))
  # Compiler output may include source context on failures: retain privately.
  result=subprocess.run(["dotnet","run","--project",str(p/"test.csproj"),"-c","Release"],capture_output=True,text=True)
  if result.returncode:raise ValueError("private original CSharp compile/execution failed")
  if "cases=14 passed" not in result.stdout:raise ValueError("missing actual execution evidence")
  print("RAFT_ORIGINAL_BLUR_CLEANUP source_verified=true original_method_executed=true cases=14 original_loop_draws=4 CPU_stubs_only=true")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--source-root",type=Path,required=True);main(p.parse_args().source_root)
