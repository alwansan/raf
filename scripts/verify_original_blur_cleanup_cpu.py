"""Execute transformed authentic original Blur method using CPU Unity API stubs."""
import argparse,hashlib,subprocess,tempfile
from pathlib import Path
from scripts.blur_pixel_cleanup import protect
from scripts.verify_blur_pixel_cleanup_cpu import STUBS
PIN="67242ca043c8f659dba4ea833a8f5fe072b282f6ddc65ced16a2cf422e6f5b13"
def main(root):
 paths=list(root.rglob("Blur.cs"))
 if len(paths)!=1:raise ValueError("ambiguous original Blur")
 source=paths[0].read_text(encoding="utf-8-sig").replace("\r\n","\n")
 observed=hashlib.sha256(source.encode()).hexdigest()
 print("RAFT_ORIGINAL_BLUR_SOURCE sha256="+observed)
 if observed!=PIN:raise ValueError("original Blur source pin differs; refuse guessed transformation")
 try: changed=protect(source)
 except ValueError:
  import re,json
  print("RAFT_BLUR_CONTRACT_COUNTS "+json.dumps({k:source.count(k) for k in ["FilterMode filterMode = target.filterMode;","RenderTexture temporary = RenderTexture.GetTemporary(","target.filterMode = filterMode;","RenderTexture.ReleaseTemporary(temporary);"]},sort_keys=True))
  raise
 signature="protected void ApplyPixelShader(RenderTexture target)"
 at=changed.index(signature);opening=changed.index("{",at);end=opening+1;depth=1
 while depth:
  depth+=(changed[end]=="{")-(changed[end]=="}");end+=1
 method=changed[at:end]
 stubs=STUBS.replace('class RenderTexture {','class Texture { public virtual FilterMode filterMode {get;set;} public int width=16,height=16; public string name; }\nclass RenderTexture : Texture {').replace("public bool IsTarget;","public int width=16,height=16,format=0; public string name; public static int Draws; public bool IsTarget;")
 stubs=stubs.replace('public FilterMode filterMode {','public override FilterMode filterMode {')
 stubs=stubs.replace("RenderTexture.Fail=fail;RenderTexture.Releases=0;","RenderTexture.Fail=fail;RenderTexture.Releases=0;RenderTexture.Draws=0;")
 stubs=stubs.replace("class Subject {","class Material { public void SetVector(int key,Vector4 value){} }\nstruct Vector4 { public Vector4(float a,float b,float c,float d){} }\nstatic class ShaderVariables { public static int Offset=0; }\nstatic class Graphics { public static void Blit(Texture a,RenderTexture b,Material m,int pass) { RenderTexture.Draws++; if((RenderTexture.Fail==4&&RenderTexture.Draws==1)||(RenderTexture.Fail==5&&RenderTexture.Draws==2))throw new Exception(\"injected\"); } }\nclass Subject { Material BlurMaterial=new Material(); int _Iterations=2,_PassIndex=0;float _Size=0.005f;")
 stubs=stubs.replace("count++;","if(fail==0 && RenderTexture.Draws!=4)throw new Exception(\"original iteration order\");count++;")
 with tempfile.TemporaryDirectory() as d:
  p=Path(d);(p/"test.csproj").write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework></PropertyGroup></Project>')
  (p/"Program.cs").write_text(stubs.replace("METHOD_PLACEHOLDER",method))
  # Compiler output may include source context on failures: retain privately.
  result=subprocess.run(["dotnet","run","--project",str(p/"test.csproj"),"-c","Release"],capture_output=True,text=True)
  if result.returncode:
   import re,json
   output=result.stdout+result.stderr
   print("RAFT_BLUR_CPU_FAILURE "+json.dumps({"missing_stub_API_members":sorted(set(re.findall(r"\'(?:Texture|RenderTexture|Subject|Vector4|Material|ShaderVariables|FilterMode|int|float|object)\' does not contain a definition for \'([A-Za-z_]\w*)\'",output))),"compiler_codes":sorted(set(re.findall(r"CS[0-9]{4}",output))),"known_API_tokens":[x for x in ["Texture","RenderTexture","Graphics","Vector4","ShaderVariables","Material","FilterMode","Mathf","Color","RenderTextureFormat"] if x in output],"synthetic_assertions":[x for x in ["exception propagation","cleanup count","restore filter","original iteration order"] if x in output]}))
   raise ValueError("private original CSharp compile/execution failed")
  if "cases=14 passed" not in result.stdout:raise ValueError("missing actual execution evidence")
  print("RAFT_ORIGINAL_BLUR_CLEANUP source_verified=true original_method_executed=true cases=14 original_loop_draws=4 CPU_stubs_only=true")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--source-root",type=Path,required=True);main(p.parse_args().source_root)
