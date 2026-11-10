using System;
using System.IO;
using System.Collections.Generic;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.Rendering;
using UnityEngine;
using UnityEngine.Rendering;

namespace RaftGraphicsLabEditor
{
    /// <summary>Independent exact-version PC compile witness; no source code exported.</summary>
    public static class GfxOriginalStandardPcWitness098
    {
        [Serializable] public class Request
        { public int subshader,tier;public string passName,stage;public string[] keywords;public string originalSHDR,originalISGN,originalOSGN; }
        [Serializable] public class Requests{public string sourceSHA;public Request[] requests;}
        [Serializable] public class SafeReport
        {
            public string experiment="GFX-MULTI-098-PC-COMPILE";
            public string UnityVersion;
            public int requestedStages,compileSuccess,compiledDXBCFound,SHDRByteExact,ISGNByteExact,OSGNByteExact;
            public int compileRejected,exceptionCount,candidateCompilesAttempted;
            public int sourceTierKnownRequests,sourceTierUnknownRequests,requestsWithSHDRByteExact,requestsWithAllChunksByteExact;
            public bool allRequestedOriginalSHDRByteExact;
            public bool originalShaderRestored=false,phase_closed=false,PC_Adreno_pixels_proven=false;
        }
        private static uint U32(byte[] data,int offset){return BitConverter.ToUInt32(data,offset);}
        private static string Hash(byte[] data,int offset,int count)
        {using(var sha=SHA256.Create())return BitConverter.ToString(sha.ComputeHash(data,offset,count)).Replace("-","").ToLowerInvariant();}
        private static Dictionary<string,string> Chunks(byte[] data)
        {
            if(data==null||data.Length>16*1024*1024)return null;
            for(int off=0;off+36<=data.Length;off++)
            {
                if(data[off]!=68||data[off+1]!=88||data[off+2]!=66||data[off+3]!=67)continue;
                uint size=U32(data,off+24),n=U32(data,off+28);
                if(size<36||size>data.Length-off||n<1||n>64||32+4*n>size)continue;
                var hashes=new Dictionary<string,string>();bool valid=true;
                for(int i=0;i<n;i++)
                {
                    uint rel=U32(data,off+32+4*i);if(rel>size-8){valid=false;break;}
                    int pos=off+(int)rel;uint bytes=U32(data,pos+4);
                    if(bytes>size-rel-8){valid=false;break;}
                    string name=System.Text.Encoding.ASCII.GetString(data,pos,4);
                    if(name=="SHDR"||name=="SHEX")hashes["SHDR"]=Hash(data,pos+8,(int)bytes);
                    else if(name=="ISGN"||name=="ISG1")hashes["ISGN"]=Hash(data,pos+8,(int)bytes);
                    else if(name=="OSGN"||name=="OSG1"||name=="OSG5")hashes["OSGN"]=Hash(data,pos+8,(int)bytes);
                }
                if(valid&&hashes.ContainsKey("SHDR"))return hashes;
            }
            return null;
        }
        public static SafeReport Run()
        {
            var report=new SafeReport{UnityVersion=Application.unityVersion};
            var input=JsonUtility.FromJson<Requests>(File.ReadAllText("Assets/Gfx098Private/pc-compile-requests.json"));
            if(input.sourceSHA!="15964ea8f246b6e076ce26b60931ee2e1a9a2385"||input.requests.Length!=14)
                throw new InvalidOperationException("GFX098_PC_REQUESTS_IDENTITY");
            report.requestedStages=input.requests.Length;
            Shader shader=Shader.Find("Standard");var data=ShaderUtil.GetShaderData(shader);
            foreach(var request in input.requests)
            {
                try
                {
                    if(request.tier < -1||request.tier>2)throw new InvalidOperationException("GFX098_ORIGINAL_TIER");
                    if(request.tier==-1)report.sourceTierUnknownRequests++;else report.sourceTierKnownRequests++;
                    var sub=data.GetSubshader(request.subshader);ShaderData.Pass pass=null;
                    if(sub!=null)for(int p=0;p<sub.PassCount;p++)if(sub.GetPass(p).Name==request.passName){if(pass!=null)throw new InvalidOperationException("GFX098_DUPLICATE_PASS");pass=sub.GetPass(p);}
                    if(pass==null)throw new InvalidOperationException("GFX098_SOURCE_PASS_NOT_FOUND");
                    ShaderType type=request.stage=="Vertex"?ShaderType.Vertex:ShaderType.Fragment;
                    bool anySHDR=false,anyAll=false;
                    int begin=request.tier==-1?0:request.tier,end=request.tier==-1?2:request.tier;
                    for(int tier=begin;tier<=end;tier++)
                    {
                        report.candidateCompilesAttempted++;
                        var compiled=pass.CompileVariant(type,request.keywords,ShaderCompilerPlatform.D3D,
                            BuildTarget.StandaloneWindows64,(GraphicsTier)tier,true);
                        if(!compiled.Success){report.compileRejected++;continue;}
                        report.compileSuccess++;var hashes=Chunks(compiled.ShaderData);
                        if(hashes==null)continue;report.compiledDXBCFound++;
                        bool shdr=hashes.ContainsKey("SHDR")&&hashes["SHDR"]==request.originalSHDR;
                        bool inputMatch=hashes.ContainsKey("ISGN")&&hashes["ISGN"]==request.originalISGN;
                        bool outputMatch=hashes.ContainsKey("OSGN")&&hashes["OSGN"]==request.originalOSGN;
                        if(shdr)report.SHDRByteExact++;if(inputMatch)report.ISGNByteExact++;if(outputMatch)report.OSGNByteExact++;
                        anySHDR|=shdr;anyAll|=shdr&&inputMatch&&outputMatch;
                    }
                    if(anySHDR)report.requestsWithSHDRByteExact++;
                    if(anyAll)report.requestsWithAllChunksByteExact++;

                }
                catch(Exception){report.exceptionCount++;}
            }
            report.allRequestedOriginalSHDRByteExact=report.requestsWithSHDRByteExact==report.requestedStages;
            Directory.CreateDirectory("Assets/Resources");
            File.WriteAllText("Assets/Resources/Gfx098PcCompileSafe.json",JsonUtility.ToJson(report,true));
            File.WriteAllText("gfx098-PC-compile-safe.json",JsonUtility.ToJson(report,true));
            // The original variant keywords, chunk hashes and any compiled bytes
            // stay private; delete requests before building the Android APK.
            File.Delete("Assets/Gfx098Private/pc-compile-requests.json");
            Debug.Log("GFX098_PC_COMPILE_SAFE "+JsonUtility.ToJson(report,false));
            return report;
        }
    }
}
