using System;
using System.Collections;
using System.IO;
using UnityEngine;
using UnityEngine.Rendering;

namespace RaftGraphicsLab
{
    /// <summary>
    /// GFX-MULTI-041. New synthetic shaders only: perspective, flat and
    /// noperspective. No original Shader48, game textures, or PC parity claim.
    /// Records GPU readback samples + diagnostic PNGs and exports existing
    /// GfxSessionRecorder sessions through Android MediaStore scoped ZIP.
    /// </summary>
    public sealed class GfxAffineReferenceProbe : MonoBehaviour
    {
        [Serializable] public sealed class CaseResult
        {
            public string name;
            public bool shaderFound;
            public bool shaderSupportedOnDevice;
            public bool gpuReadbackCompleted;
            public bool allSamplePositionsHaveColor;
            public string failure;
            public Color[] sampledColors;
            public float largestBetweenSamplesColorDifference;
            public string screenshotFile;
        }
        [Serializable] private sealed class Report
        {
            public string experiment="GFX-MULTI-041";
            public string diagnosticType="SYNTHETIC_ONLY_GLES_INTERPOLATION";
            public bool originalShaderRestored=false;
            public bool originalRaftShaderBytecodeUsed=false;
            public bool originalPcPixelParityVerified=false;
            public bool sourceMaterialCbBindingsVerified=false;
            public string utc;
            public string sessionId;
            public string deviceModel;
            public string graphicsDevice;
            public string graphicsApi;
            public string graphicsVersion;
            public string unityVersion;
            public string colorSpace;
            public bool isGles3;
            public bool autoLogEnabled;
            public bool allFourGpuReadbacksComplete;
            public bool affineEmulatedMatchesCpu;
            public bool linearPerspectiveMatchesCpu;
            public bool nativeNoPerspectiveMatchesAffine;
            public bool nativeNoPerspectiveMatchesSmooth;
            public float cpuExpectedPerspectiveAffineDifference;
            public float gpuLinearVsCpuPerspectiveError;
            public float gpuAffineEmulatedVsCpuAffineError;
            public float gpuNativeVsCpuAffineError;
            public float gpuNativeVsLinearError;
            public string diagnosticStatus;
            public float smoothVsNoPerspectiveColorDifference;
            public bool flatConstantAcrossInteriorSamples;
            public bool perspectiveVsNoPerspectiveDistinguishable;
            public CaseResult[] results;
            public string exportedLogsPath;
            public string exportStatus;
        }

        private const int W=256;
        private const int H=256;
        private const string ShaderPrefix="Hidden/GfxLab/Interpolation";
        private static readonly string[] Modes={"Linear","Flat","NoPerspective","AffineEmulated"};
        private static readonly Vector2Int[] SamplePoints={
            new Vector2Int(128,98),new Vector2Int(104,108),new Vector2Int(152,108)
        };
        private GfxSessionRecorder recorder;
        private Mesh triangle;
        private readonly Texture2D[] previews=new Texture2D[4];
        private readonly CaseResult[] results=new CaseResult[4];
        private bool running;
        private bool exporting;
        private bool gpuComplete;
        private bool flatConsistent;
        private bool perspectiveDifferent;
        private bool linearPerspectiveCorrect;
        private bool affineEmulationCorrect;
        private bool nativeMatchesAffine;
        private bool nativeMatchesLinear;
        private float interpolationDifference;
        private float cpuPerspectiveVsAffineDifference;
        private float linearCpuError;
        private float affineCpuError;
        private float nativeAffineError;
        private float nativeLinearError;
        private string status="NOT_RUN";
        private string exportStatus="EXPORT ZIP saves ALL sessions + four GPU screenshots";
        private string lastPublicPath="";
                private GUIStyle headline;
        private GUIStyle caption;
        private GUIStyle action;

        private static string UtcNow(){return DateTime.UtcNow.ToString("o");}

        private void Start()
        {
            recorder=GetComponent<GfxSessionRecorder>();
            if(recorder==null)
                Debug.LogError("GFX041_MISSING_AUTOMATIC_SESSION_RECORDER");
            Screen.orientation=ScreenOrientation.LandscapeLeft;
            BuildSyntheticTriangle();
            for(int i=0;i<Modes.Length;i++)
                results[i]=new CaseResult { name=Modes[i],failure="NOT_RUN",sampledColors=new Color[3] };
            WriteReport("session_started");
            StartCoroutine(RunAllCases());
        }

        private void BuildSyntheticTriangle()
        {
            // Exact same projected XY for all three shaders; intentionally
            // unequal clip W guarantees a measurable nonperspective delta.
            triangle=new Mesh();
            triangle.name="SYNTHETIC_INTERPOLATION_TRIANGLE_NOT_RAFT";
            triangle.vertices=new[]{
                new Vector3(-.86f,-.77f,0),
                new Vector3( .86f,-.77f,0),
                new Vector3( 0f, .86f,0)
            };
            triangle.colors=new[]{Color.red,Color.green,Color.blue};
            triangle.uv=new[]{
                new Vector2(.55f,0),new Vector2(1.0f,0),new Vector2(2.7f,0)
            };
            triangle.triangles=new[]{0,1,2};
            triangle.RecalculateBounds();
        }

        private static float Difference(Color a,Color b)
        {
            return (Mathf.Abs(a.r-b.r)+Mathf.Abs(a.g-b.g)+Mathf.Abs(a.b-b.b))/3f;
        }
        private static float Brightness(Color c){return c.r+c.g+c.b;}
        private static float Spread(Color[] p)
        {
            if(p==null||p.Length!=3)return float.PositiveInfinity;
            return Mathf.Max(Difference(p[0],p[1]),
                Mathf.Max(Difference(p[1],p[2]),Difference(p[0],p[2])));
        }

        
        // Independent CPU reference from the exact synthetic vertex NDC
        // positions, measured pixel centers and clip W = 0.55, 1.0, 2.7.
        // Original Shader48 not involved.
        private static Color CpuExpected(Vector2Int pixel,bool perspective)
        {
            float x=2f*(pixel.x+.5f)/W-1f;
            float y=2f*(pixel.y+.5f)/H-1f;
            float ax=-.86f,ay=-.77f,bx=.86f,by=-.77f,cx=0f,cy=.86f;
            float den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy);
            float r=((by-cy)*(x-cx)+(cx-bx)*(y-cy))/den;
            float g=((cy-ay)*(x-cx)+(ax-cx)*(y-cy))/den;
            float b=1f-r-g;
            if(perspective)
            {
                float rr=r/.55f,gg=g/1.0f,bb=b/2.7f;
                float sum=rr+gg+bb;
                return new Color(rr/sum,gg/sum,bb/sum,1f);
            }
            return new Color(r,g,b,1f);
        }

        private float MeanCpuError(int mode,bool perspective)
        {
            float sum=0f;
            for(int i=0;i<SamplePoints.Length;i++)
                sum+=Difference(results[mode].sampledColors[i],
                    CpuExpected(SamplePoints[i],perspective));
            return sum/SamplePoints.Length;
        }

        private float MeanPairError(int first,int second)
        {
            float sum=0f;
            for(int i=0;i<SamplePoints.Length;i++)
                sum+=Difference(results[first].sampledColors[i],
                    results[second].sampledColors[i]);
            return sum/SamplePoints.Length;
        }

        private IEnumerator RunAllCases()
        {
            if(running)yield break;
            running=true;
            status="GPU_READBACK_IN_PROGRESS";
            if(recorder!=null)recorder.RecordAction("RUN_INTERPOLATION_PROBES_REQUESTED");
            WriteReport("begin_gpu_readback");
            // Execute in render frame; ReadPixels will synchronize the GPU.
            yield return new WaitForEndOfFrame();
            for(int i=0;i<Modes.Length;i++)
            {
                CaptureCase(i);
                WriteReport("gpu_case_"+Modes[i]+"_completed");
                yield return new WaitForEndOfFrame();
            }
            gpuComplete=true;
            for(int i=0;i<Modes.Length;i++)
                gpuComplete &= results[i]!=null &&
                    results[i].gpuReadbackCompleted && results[i].allSamplePositionsHaveColor;
            flatConsistent=gpuComplete &&
                results[1].largestBetweenSamplesColorDifference<=.06f;
            interpolationDifference=0f;
            cpuPerspectiveVsAffineDifference=0f;
            linearCpuError=affineCpuError=nativeAffineError=nativeLinearError=0f;
            perspectiveDifferent=linearPerspectiveCorrect=affineEmulationCorrect=false;
            nativeMatchesAffine=nativeMatchesLinear=false;
            if(gpuComplete)
            {
                linearCpuError=MeanCpuError(0,true);
                affineCpuError=MeanCpuError(3,false);
                nativeAffineError=MeanCpuError(2,false);
                nativeLinearError=MeanPairError(2,0);
                interpolationDifference=MeanPairError(0,3);
                for(int i=0;i<SamplePoints.Length;i++)
                    cpuPerspectiveVsAffineDifference+=Difference(
                        CpuExpected(SamplePoints[i],true),
                        CpuExpected(SamplePoints[i],false));
                cpuPerspectiveVsAffineDifference/=SamplePoints.Length;
                perspectiveDifferent=interpolationDifference>=.08f;
                linearPerspectiveCorrect=linearCpuError<=.02f;
                affineEmulationCorrect=affineCpuError<=.02f;
                nativeMatchesAffine=nativeAffineError<=.02f;
                nativeMatchesLinear=nativeLinearError<=.005f;
            }
            bool gles3=SystemInfo.graphicsDeviceType==GraphicsDeviceType.OpenGLES3;
            status= !gles3?"INCONCLUSIVE_NOT_GLES3":
                    !gpuComplete?"INCONCLUSIVE_SHADER_OR_READBACK":
                    !flatConsistent?"DIAGNOSTIC_FLAT_MISMATCH":
                    !linearPerspectiveCorrect?"DIAGNOSTIC_LINEAR_CPU_MISMATCH":
                    !affineEmulationCorrect?"DIAGNOSTIC_EMULATED_AFFINE_CPU_MISMATCH":
                    !perspectiveDifferent?"DIAGNOSTIC_REFERENCE_GEOMETRY_UNDISTINGUISHABLE":
                    nativeMatchesAffine?"DIAGNOSTIC_NATIVE_NOPERSPECTIVE_MATCHES_AFFINE":
                    nativeMatchesLinear?"DIAGNOSTIC_NATIVE_QUALIFIER_COLLAPSED_TO_SMOOTH":
                    "DIAGNOSTIC_NATIVE_NOPERSPECTIVE_OTHER_RESULT";
            running=false;
            WriteReport("automatic_gpu_diagnostic_completed");
            Debug.Log("GFX041_SYNTHETIC_GPU_DIAGNOSTIC status="+status+
                " original_shader_restored=false shader_material_binding_verified=false");
        }

        private void CaptureCase(int i)
        {
            var row=new CaseResult {
                name=Modes[i],sampledColors=new Color[3],failure=""
            };
            results[i]=row;
            RenderTexture rt=null;
            CommandBuffer cmd=null;
            Material mat=null;
            var previous=RenderTexture.active;
            try
            {
                Shader shader=Shader.Find(ShaderPrefix+Modes[i]);
                row.shaderFound=shader!=null;
                row.shaderSupportedOnDevice=shader!=null && shader.isSupported;
                if(!row.shaderSupportedOnDevice)
                    throw new InvalidOperationException("GFX041_SHADER_MISSING_OR_NOT_SUPPORTED_"+Modes[i]);
                mat=new Material(shader);
                rt=new RenderTexture(W,H,0,RenderTextureFormat.ARGB32,RenderTextureReadWrite.Linear);
                rt.name="GFX041_DIAGNOSTIC_RT_"+Modes[i];
                rt.filterMode=FilterMode.Point;
                if(!rt.Create())
                    throw new InvalidOperationException("GFX041_RENDER_TEXTURE_CREATE_FAILED");
                cmd=new CommandBuffer {name="GFX041_SYNTHETIC_TRIANGLE_GPU_DRAW"};
                cmd.SetRenderTarget(rt);
                cmd.ClearRenderTarget(true,true,Color.black);
                cmd.DrawMesh(triangle,Matrix4x4.identity,mat,0,0);
                Graphics.ExecuteCommandBuffer(cmd);
                RenderTexture.active=rt;
                var pixels=new Texture2D(W,H,TextureFormat.RGBA32,false,true);
                pixels.name="GFX041_DIAGNOSTIC_GPU_READBACK_"+Modes[i];
                pixels.ReadPixels(new Rect(0,0,W,H),0,0,false);
                pixels.Apply(false,false);
                for(int j=0;j<SamplePoints.Length;j++)
                {
                    var pt=SamplePoints[j];
                    row.sampledColors[j]=pixels.GetPixel(pt.x,pt.y);
                }
                row.largestBetweenSamplesColorDifference=Spread(row.sampledColors);
                row.allSamplePositionsHaveColor=true;
                for(int j=0;j<SamplePoints.Length;j++)
                    row.allSamplePositionsHaveColor &= Brightness(row.sampledColors[j])>=.15f;
                byte[] image=pixels.EncodeToPNG();
                if(image==null||image.Length<100)
                    throw new IOException("GFX041_GPU_SCREENSHOT_PNG_ENCODING_FAILED");
                if(recorder==null||string.IsNullOrEmpty(recorder.RootDirectory)||
                   string.IsNullOrEmpty(recorder.SessionId))
                    throw new IOException("GFX041_RECORDER_DIRECTORY_UNAVAILABLE");
                string folder=Path.Combine(recorder.RootDirectory,"sessions",recorder.SessionId);
                Directory.CreateDirectory(folder);
                string name="gpu-interpolation-"+Modes[i].ToLowerInvariant()+".png";
                File.WriteAllBytes(Path.Combine(folder,name),image);
                row.screenshotFile=name;
                row.gpuReadbackCompleted=true;
                if(previews[i]!=null)Destroy(previews[i]);
                previews[i]=pixels;
                Debug.Log("GFX041_DIAGNOSTIC_READBACK mode="+Modes[i]+
                    " all_samples_foreground="+row.allSamplePositionsHaveColor+
                    " spread="+row.largestBetweenSamplesColorDifference.ToString("F5"));
            }
            catch(Exception ex)
            {
                row.failure=ex.GetType().Name+": "+ex.Message;
                Debug.LogError("GFX041_DIAGNOSTIC_CASE_FAILED mode="+Modes[i]+" "+ex);
            }
            finally
            {
                RenderTexture.active=previous;
                if(cmd!=null)cmd.Release();
                if(rt!=null){rt.Release();Destroy(rt);}
                if(mat!=null)Destroy(mat);
            }
        }

        private string ReportJson()
        {
            var r=new Report {
                utc=UtcNow(),sessionId=recorder!=null?recorder.SessionId:"",
                deviceModel=SystemInfo.deviceModel,graphicsDevice=SystemInfo.graphicsDeviceName,
                graphicsApi=SystemInfo.graphicsDeviceType.ToString(),
                graphicsVersion=SystemInfo.graphicsDeviceVersion,
                unityVersion=Application.unityVersion,
                colorSpace=QualitySettings.activeColorSpace.ToString(),
                isGles3=SystemInfo.graphicsDeviceType==GraphicsDeviceType.OpenGLES3,
                autoLogEnabled=recorder!=null && string.IsNullOrEmpty(recorder.Failure),
                allFourGpuReadbacksComplete=gpuComplete,diagnosticStatus=status,
                affineEmulatedMatchesCpu=affineEmulationCorrect,
                linearPerspectiveMatchesCpu=linearPerspectiveCorrect,
                nativeNoPerspectiveMatchesAffine=nativeMatchesAffine,
                nativeNoPerspectiveMatchesSmooth=nativeMatchesLinear,
                cpuExpectedPerspectiveAffineDifference=cpuPerspectiveVsAffineDifference,
                gpuLinearVsCpuPerspectiveError=linearCpuError,
                gpuAffineEmulatedVsCpuAffineError=affineCpuError,
                gpuNativeVsCpuAffineError=nativeAffineError,
                gpuNativeVsLinearError=nativeLinearError,
                smoothVsNoPerspectiveColorDifference=interpolationDifference,
                flatConstantAcrossInteriorSamples=flatConsistent,
                perspectiveVsNoPerspectiveDistinguishable=perspectiveDifferent,
                results=results,exportedLogsPath=lastPublicPath,
                exportStatus=exportStatus
            };
            return JsonUtility.ToJson(r,true);
        }

        private void WriteReport(string reason)
        {
            var json=ReportJson();
            try
            {
                if(recorder!=null && !string.IsNullOrEmpty(recorder.RootDirectory))
                {
                    string path=Path.Combine(recorder.RootDirectory,"multi-report.json");
                    File.WriteAllText(path,json);
                    recorder.RecordState(reason,json);
                    recorder.Flush();
                }
            }
            catch(Exception ex)
            {
                Debug.LogError("GFX041_DIAGNOSTIC_REPORT_SAVE_FAILED "+ex);
            }
        }

        private IEnumerator ExportZip()
        {
            if(exporting)yield break;
            exporting=true;
            exportStatus="Exporting all session logs and four GPU PNGs...";
            WriteReport("export_zip_requested");
            yield return null;
            string publicPath="";
            string error="";
            bool ok=recorder!=null && recorder.ExportAll(out publicPath,out error);
            if(recorder==null)
            {
                publicPath="";error="GFX041_RECORDER_MISSING";
            }
            lastPublicPath=ok?publicPath:"";
            exportStatus=ok?"ZIP exported: "+publicPath:"ZIP export failed: "+error;
            if(recorder!=null)recorder.RecordExportResult(ok,exportStatus);
            exporting=false;
            WriteReport("export_zip_"+(ok?"success":"failure"));
        }

        private void OnGUI()
        {
            float scale=Mathf.Clamp(Screen.width/1400f,.7f,1.5f);
            if(headline==null)
            {
                headline=new GUIStyle(GUI.skin.label);
                headline.fontSize=Mathf.RoundToInt(24*scale);
                headline.normal.textColor=Color.white;
                headline.wordWrap=true;
                caption=new GUIStyle(headline);
                caption.fontSize=Mathf.RoundToInt(17*scale);
                action=new GUIStyle(GUI.skin.button);
                action.fontSize=Mathf.RoundToInt(19*scale);
            }
            var pad=16f*scale;
            GUI.Box(new Rect(6,5,Screen.width-12,Screen.height-10),"");
            GUI.Label(new Rect(pad,pad,Screen.width-2*pad,44*scale),
                "GFX-MULTI-041  |  GLES affine reference — SYNTHETIC ONLY",headline);
            GUI.Label(new Rect(pad,58*scale,Screen.width-2*pad,26*scale),
                "Device: "+SystemInfo.graphicsDeviceName+" / "+SystemInfo.graphicsDeviceType+
                "   |  Original Raft Shader48: NOT RESTORED",caption);
            GUI.Label(new Rect(pad,92*scale,Screen.width-2*pad,28*scale),
                "Status: "+status+"  |  Smooth CPU error="+linearCpuError.ToString("F4")+
                "  |  Affine CPU error="+affineCpuError.ToString("F4"),caption);
            float y=139*scale;
            float col=(Screen.width-5*pad)/4f;
            for(int i=0;i<Modes.Length;i++)
            {
                float left=pad+i*(col+pad);
                GUI.Label(new Rect(left,y,col,28*scale),Modes[i],headline);
                float side=Mathf.Min(col,Mathf.Max(95f*scale,Screen.height-y-160*scale));
                if(previews[i]!=null)
                    GUI.DrawTexture(new Rect(left,y+30*scale,side,side),previews[i],ScaleMode.ScaleToFit,false);
                else GUI.Box(new Rect(left,y+30*scale,side,side),"No GPU sample yet");
                var row=results[i];
                if(row!=null)
                {
                    GUI.Label(new Rect(left,y+35*scale+side,col,60*scale),
                        "GPU: "+(row.gpuReadbackCompleted?"READBACK":"PENDING/FAILED")+
                        " / "+(row.shaderSupportedOnDevice?"Supported":"No shader support")+
                        " / Spread "+row.largestBetweenSamplesColorDifference.ToString("F4"),caption);
                }
            }
            float buttonY=Screen.height-95*scale;
            if(GUI.Button(new Rect(pad,buttonY,260*scale,46*scale),
                running?"RUNNING...":"RERUN GPU TEST",action) && !running)
                StartCoroutine(RunAllCases());
            if(GUI.Button(new Rect(pad+278*scale,buttonY,290*scale,46*scale),
                exporting?"EXPORTING...":"EXPORT ALL LOGS ZIP",action) && !exporting)
                StartCoroutine(ExportZip());
            GUI.Label(new Rect(pad,Screen.height-39*scale,Screen.width-2*pad,28*scale),
                "Logs + full stacks + four PNGs: "+GfxDownloadsZipExporter.ExpectedPublicDirectory,caption);
        }

        private void OnApplicationPause(bool paused)
        {
            if(paused)WriteReport("application_paused");
        }
        private void OnApplicationQuit(){WriteReport("application_quit");}
        private void OnDestroy()
        {
            if(triangle!=null)Destroy(triangle);
            for(int i=0;i<previews.Length;i++)
                if(previews[i]!=null)Destroy(previews[i]);
        }
    }
}
