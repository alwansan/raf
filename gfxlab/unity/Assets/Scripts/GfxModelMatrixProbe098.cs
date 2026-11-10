using System;
using System.IO;
using System.Collections;
using System.Security.Cryptography;
using UnityEngine;

namespace RaftGraphicsLab
{
    /// <summary>Deterministic studio camera readbacks, not PC/Raft pixel parity.</summary>
    public sealed class GfxModelMatrixProbe098 : MonoBehaviour
    {
        [Serializable] private sealed class Capture
        {
            public string experiment="GFX-MULTI-098";
            public string model;
            public int materialMode;
            public string captureKind="STUDIO_CAMERA_RENDER_READBACK";
            public string pngFile;
            public string pngSha256;
            public string stateJson;
            public int width,height;
            public int actualRendererMaterialSlots;
            public string[] actualShaderNames;
            public bool[] actualShaderSupported;
            public bool sourceSavedValuesCandidate;
            public bool originalShaderRestored=false;
            public bool originalRigRestored=false;
            public bool originalPCPixelParity=false;
        }
        public bool Running {get;private set;}
        private GfxMultiViewer viewer;
        private GfxSessionRecorder recorder;
        private string status="Waiting for model capture";
        private IEnumerator Start()
        {
            viewer=GetComponent<GfxMultiViewer>();recorder=GetComponent<GfxSessionRecorder>();
            yield return null;yield return null;
            if(viewer==null||recorder==null)throw new InvalidOperationException("GFX098_REQUIRED_VIEWER_RECORDER_MISSING");
            var proof=Resources.Load<TextAsset>("Gfx098PcCompileSafe");
            if(proof!=null)recorder.RecordState("PC_compile_source_witness",proof.text);
            RunMatrix();
        }
        public void RunMatrix(){if(!Running&&viewer!=null)StartCoroutine(Run());}
        private IEnumerator Run()
        {
            Running=true;viewer.automatedTestRunning=true;
            string directory=Path.Combine(recorder.RootDirectory,"sessions",recorder.SessionId,"model-matrix098");
            Directory.CreateDirectory(directory);int completed=0;string failure="";
            for(int model=0;model<6;model++)
            {
                for(int mode=3;mode<=4;mode++)
                {
                    viewer.SelectAutomatedCase(model,mode);
                    yield return new WaitForEndOfFrame();yield return new WaitForEndOfFrame();
                    try
                    {
                        CaptureCase(directory,model,mode);completed++;status="Captured "+completed+"/12 model cases";
                    }
                    catch(Exception ex)
                    {
                        failure=ex.GetType().Name+": "+ex.Message;
                        recorder.RecordAction("MODEL_MATRIX_CAPTURE_FAILED "+failure);
                    }
                    yield return null;
                }
            }
            viewer.automatedTestRunning=false;Running=false;
            recorder.RecordAction("MODEL_MATRIX098_COMPLETED captures="+completed+" expected=12 failure="+failure);
            yield return null;
            string path,error;bool ok=recorder.ExportAll(out path,out error);
            status=ok?"12-case matrix ZIP saved: "+path:"EXPORT FAILED: "+error;
            recorder.RecordExportResult(ok,status);
        }
        private void CaptureCase(string directory,int index,int mode)
        {
            Camera camera=viewer.viewingCamera;if(camera==null)throw new InvalidOperationException("GFX098_CAMERA_MISSING");
            var oldTarget=camera.targetTexture;var oldActive=RenderTexture.active;
            RenderTexture target=null;Texture2D pixels=null;
            try
            {
                target=new RenderTexture(960,540,24,RenderTextureFormat.ARGB32,RenderTextureReadWrite.Default);
                target.Create();camera.targetTexture=target;camera.Render();RenderTexture.active=target;
                pixels=new Texture2D(960,540,TextureFormat.RGBA32,false);
                pixels.ReadPixels(new Rect(0,0,960,540),0,0,false);pixels.Apply(false,false);
                byte[] png=pixels.EncodeToPNG();if(png==null||png.Length<100)throw new InvalidOperationException("GFX098_PNG_EMPTY");
                string id=viewer.models[index].id;string name=id+"_mode"+mode+"_"+DateTime.UtcNow.ToString("yyyyMMddTHHmmssfff")+".png";
                File.WriteAllBytes(Path.Combine(directory,name),png);
                var names=new System.Collections.Generic.List<string>();var supported=new System.Collections.Generic.List<bool>();
                foreach(var slot in viewer.models[index].slots)
                    foreach(var material in slot.renderer.sharedMaterials)
                    {names.Add(material==null||material.shader==null?"MISSING":material.shader.name);supported.Add(material!=null&&material.shader!=null&&material.shader.isSupported);}
                string hash;using(var sha=SHA256.Create())hash=BitConverter.ToString(sha.ComputeHash(png)).Replace("-","").ToLowerInvariant();
                var report=new Capture{model=id,materialMode=mode,pngFile=name,pngSha256=hash,
                    stateJson=viewer.SnapshotJson,width=960,height=540,actualRendererMaterialSlots=names.Count,
                    actualShaderNames=names.ToArray(),actualShaderSupported=supported.ToArray(),sourceSavedValuesCandidate=mode==4};
                string json=JsonUtility.ToJson(report,true);File.WriteAllText(Path.Combine(directory,Path.GetFileNameWithoutExtension(name)+".json"),json);
                recorder.RecordState("model_matrix_capture_"+id+"_mode"+mode,json);
            }
            finally
            {
                camera.targetTexture=oldTarget;RenderTexture.active=oldActive;
                if(target!=null){target.Release();Destroy(target);}if(pixels!=null)Destroy(pixels);
            }
        }
        private void OnGUI()
        {
            if(!Running)return;var safe=GfxLabViewport.SafeGuiRect();
            var style=new GUIStyle(GUI.skin.box);style.fontSize=22;
            GUI.Box(new Rect(safe.x+safe.width*.3f,safe.y+safe.height-50,safe.width*.4f,40),status,style);
        }
    }
}
