using System;
using System.Collections;
using System.IO;
using UnityEngine;

namespace RaftGraphicsLab
{
    /// <summary>Six authenticated original geometry cases with explicit diagnostic shader fallbacks.</summary>
    public sealed class GfxMultiViewer : MonoBehaviour
    {
        [Serializable] public sealed class MaterialSlot
        {
            public Renderer renderer;
            public Material[] whiteLit;
            public Material[] whiteUnlit;
            public Material[] sourceAlbedo;
            public Material[] sourcePbr;
            public Material[] sourceSavedStandard;
        }

        [Serializable] public sealed class DiagnosticSlot
        {
            public Texture2D basecolorSource;
            public Texture2D basecolorLinear;
            public Texture2D normalSource;
            public Texture2D normalLinear;
            public Texture2D metallicSource;
            public Texture2D metallicLinear;
        }

        [Serializable] public sealed class Model
        {
            public string id;
            public string category;
            public string geometryKind;
            public int sourceBones;
            public int vertices;
            public int triangles;
            public int sourceMaterials;
            public int sourceTextures;
            public bool sourceVerified;
            public bool exactShaderRestored;
            public bool originalAnimationRestored;
            public GameObject root;
            public MaterialSlot[] slots;
            public DiagnosticSlot[] diagnosticSlots;
        }

        public Camera viewingCamera;
        public Model[] models;
        public GameObject studioFloor;
        public bool defaultHideHelpers = true;
        // Authored diagnostic-only material, never the original Shader48.
        public Material diagnosticChannelMaterial;
        public GfxSessionRecorder sessionRecorder;
        public bool sourceSavedCandidateAvailable;
        public bool automatedTestRunning;
        public string experimentOverride="";
        public string SnapshotJson { get { return Report(); } }
        public void SelectAutomatedCase(int model,int mode)
        {
            materialMode=mode;spin=false;helpersVisible=false;
            if(studioFloor!=null)studioFloor.SetActive(false);
            ChangeModel(model);
        }

        private int modelIndex;
        private int materialMode = 3;
        private float yaw=-30f;
        private float pitch=15f;
        private float distance=3.5f;
        private float pinchPrevious;
        private bool spin;
        private bool helpersVisible;
        private int loggedErrors;
        private string firstError="";
        private const string Experiment="GFX-MULTI-031";
        private bool exporting;
        private string exportStatus="AUTO LOGS ON | Press EXPORT ZIP to save all sessions";
        private float nextPeriodicSnapshot;

        private int diagnosticRole;   // BaseColor / Normal / Metallic
        private int diagnosticChannel; // RGB / R / G / B / A
        private int diagnosticSurface;
        private bool diagnosticForceLinear;
        private const string ProbeStatus="DIAGNOSTIC_SHADER_NOT_SOURCE_SHADER48";
        private static readonly string[] DiagnosticRoleNames={"BASECOLOR","NORMAL","METALLIC"};
        private static readonly string[] DiagnosticChannelNames={"RGB","R","G","B","A"};
        private Texture2D ActiveDiagnosticTexture()
        {
            if(models==null || modelIndex<0 || modelIndex>=models.Length)return null;
            var m=models[modelIndex];
            if(m==null||m.diagnosticSlots==null||m.diagnosticSlots.Length==0)return null;
            diagnosticSurface=Mathf.Clamp(diagnosticSurface,0,m.diagnosticSlots.Length-1);
            var s=m.diagnosticSlots[diagnosticSurface];
            if(s==null)return null;
            if(diagnosticRole==0)return diagnosticForceLinear?s.basecolorLinear:s.basecolorSource;
            if(diagnosticRole==1)return diagnosticForceLinear?s.normalLinear:s.normalSource;
            return diagnosticForceLinear?s.metallicLinear:s.metallicSource;
        }
        private void StepDiagnosticRole()
        {
            diagnosticRole=(diagnosticRole+1)%3;
            WriteReport("role_changed");
        }
        private void StepDiagnosticChannel()
        {
            diagnosticChannel=(diagnosticChannel+1)%5;
            WriteReport("channel_changed");
        }

        [Serializable] private struct DeviceLog
        {
            public string experiment;
            public string modelId;
            public string category;
            public string originalGeometryKind;
            public string materialMode;
            public string deviceModel;
            public string gfxDevice;
            public string gfxApi;
            public string gfxVersion;
            public string unityVersion;
            public string colorSpace;
            public bool sourceGeometryVerified;
            public bool sourceTextureChainVerified;
            public bool originalShaderRestored;
            public bool originalAnimationRestored;
            public bool coloredPixelsAutomaticallyVerified;
            public float cameraYaw;
            public float cameraPitch;
            public float cameraDistance;
            public float frameTimeMs;
            public float approximateFps;
            public bool autoSpin;
            public bool studioHelpersVisible;
            public string autoLogSession;
            public bool autoLogEnabled;
            public string diagnosticProbeStatus;
            public string diagnosticRole;
            public string diagnosticChannel;
            public string diagnosticSampling;
            public bool diagnosticTextureAssigned;
            public bool diagnosticShaderSupported;
            public int diagnosticMaterialSurface;
            public int diagnosticSurfaces;
            public int availableModels;
            public int sourceBones;
            public int vertices;
            public int triangles;
            public int sourceMaterials;
            public int sourceTextures;
            public int errors;
            public string firstError;
            public string utc;
        }

        private void Start()
        {
            Application.logMessageReceived+=CaptureError;
            if(sessionRecorder==null)sessionRecorder=GetComponent<GfxSessionRecorder>();
            helpersVisible=!defaultHideHelpers;
            nextPeriodicSnapshot=Time.unscaledTime+15f;
            if(models==null || models.Length!=6)
            {
                Debug.LogError("GFX_MULTI_STOP original_count_not_six");
                return;
            }
            for(int i=0;i<models.Length;i++)
            {
                if(models[i]==null || models[i].root==null || !models[i].sourceVerified)
                {
                    Debug.LogError("GFX_MULTI_STOP missing_original_verified_model_slot");
                    return;
                }
                models[i].root.SetActive(i==modelIndex);
            }
            UpdateMaterials("session_started");
            if(studioFloor!=null)studioFloor.SetActive(helpersVisible);
            WriteReport();
            Debug.Log("GFX_MULTI_STARTED source_model_count=6 original_shaders_not_claimed=true");
        }
        private void OnDestroy(){Application.logMessageReceived-=CaptureError;}
        private void CaptureError(string log,string stack,LogType type)
        {
            if(type!=LogType.Error && type!=LogType.Exception && type!=LogType.Assert)return;
            loggedErrors++;
            if(firstError.Length==0)firstError=log.Length>160?log.Substring(0,160):log;
        }
        private string ModeName()
        {
            switch(materialMode)
            {
                case 0:return "WHITE_LIT";
                case 1:return "WHITE_UNLIT";
                case 2:return "SOURCE_ALBEDO_STANDARD";
                case 4:return "SOURCE_SAVED_STANDARD_CANDIDATE";
                default:return "SOURCE_PBR_STANDARD_APPROX";
            }
        }
        private void UpdateMaterials(string reason="material_mode_changed")
        {
            var model=models[modelIndex];
            foreach(var slot in model.slots)
            {
                if(slot==null || slot.renderer==null)continue;
                Material[] materials = materialMode==0 ? slot.whiteLit :
                    materialMode==1 ? slot.whiteUnlit :
                    materialMode==2 ? slot.sourceAlbedo :
                    materialMode==4 ? slot.sourceSavedStandard : slot.sourcePbr;
                if(materials==null || materials.Length==0)
                    throw new InvalidOperationException("GFX_MULTI_MATERIAL_MODE_EMPTY");
                slot.renderer.sharedMaterials=materials;
            }
            WriteReport(reason);
        }
        private void ChangeModel(int index)
        {
            if(models==null||models.Length==0)return;
            modelIndex=(index+models.Length)%models.Length;
            for(int i=0;i<models.Length;i++)models[i].root.SetActive(i==modelIndex);
            yaw=-30f;pitch=15f;distance=3.5f;pinchPrevious=0;
            diagnosticSurface=0;
            UpdateMaterials("model_selected");
            Debug.Log("GFX_MULTI_SELECTED model="+models[modelIndex].id+" shader_exact=false");
        }
        private void NextMaterial()
        {
            materialMode=(materialMode+1)%(sourceSavedCandidateAvailable?5:4);
            UpdateMaterials("material_mode_changed");
        }
        private void Update()
        {
            if(viewingCamera==null || models==null || models.Length<1)return;
            if(Time.unscaledTime>=nextPeriodicSnapshot)
            {
                nextPeriodicSnapshot=Time.unscaledTime+15f;
                WriteReport("periodic_15s_state");
            }
            if(!automatedTestRunning)
            {
            if(spin)yaw+=Time.deltaTime*16f;
            if(Input.touchCount==1)
            {
                var t=Input.GetTouch(0);
                // Left side lists models; top and bottom are HUD, not orbit.
                if(t.phase==TouchPhase.Moved && t.position.x>Screen.width*.23f &&
                   t.position.y>Screen.height*.06f && t.position.y<Screen.height*.79f)
                {
                    yaw+=t.deltaPosition.x*.16f;
                    pitch=Mathf.Clamp(pitch-t.deltaPosition.y*.12f,-65f,65f);
                }
                pinchPrevious=0;
            }
            else if(Input.touchCount>=2)
            {
                float pinch=Vector2.Distance(Input.GetTouch(0).position,Input.GetTouch(1).position);
                if(pinchPrevious>0) distance=Mathf.Clamp(distance+(pinchPrevious-pinch)*.007f,1.35f,9f);
                pinchPrevious=pinch;
            }
            else
            {
                pinchPrevious=0;
                distance=Mathf.Clamp(distance-Input.mouseScrollDelta.y*.3f,1.35f,9f);
                if(Input.GetMouseButton(0))
                {
                    yaw+=Input.GetAxis("Mouse X")*3f;
                    pitch=Mathf.Clamp(pitch-Input.GetAxis("Mouse Y")*3f,-65f,65f);
                }
            }
            }
            var look=new Vector3(0,1.0f,0);
            Quaternion angle=Quaternion.Euler(pitch,yaw,0);
            viewingCamera.transform.position=look+angle*new Vector3(0,0,-distance);
            viewingCamera.transform.LookAt(look);
        }
        private string Report()
        {
            if(models==null || models.Length==0)return "{}";
            var m=models[modelIndex];
            return JsonUtility.ToJson(new DeviceLog
            {
                experiment=string.IsNullOrEmpty(experimentOverride)?Experiment:experimentOverride,modelId=m.id,category=m.category,
                originalGeometryKind=m.geometryKind,materialMode=ModeName(),
                deviceModel=SystemInfo.deviceModel,
                gfxDevice=SystemInfo.graphicsDeviceName,
                gfxApi=SystemInfo.graphicsDeviceType.ToString(),
                gfxVersion=SystemInfo.graphicsDeviceVersion,
                unityVersion=Application.unityVersion,
                colorSpace=QualitySettings.activeColorSpace.ToString(),
                sourceGeometryVerified=m.sourceVerified,
                sourceTextureChainVerified=m.sourceTextures>0,
                originalShaderRestored=m.exactShaderRestored,
                originalAnimationRestored=m.originalAnimationRestored,
                coloredPixelsAutomaticallyVerified=false,
                cameraYaw=yaw,cameraPitch=pitch,cameraDistance=distance,
                frameTimeMs=Time.smoothDeltaTime*1000f,
                approximateFps=Time.smoothDeltaTime>0.001f?1f/Time.smoothDeltaTime:0f,
                autoSpin=spin,studioHelpersVisible=helpersVisible,
                autoLogSession=sessionRecorder==null?"UNAVAILABLE":sessionRecorder.SessionId,
                autoLogEnabled=sessionRecorder!=null&&string.IsNullOrEmpty(sessionRecorder.Failure),
                diagnosticProbeStatus=ProbeStatus,
                diagnosticRole=DiagnosticRoleNames[Mathf.Clamp(diagnosticRole,0,2)],
                diagnosticChannel=DiagnosticChannelNames[Mathf.Clamp(diagnosticChannel,0,4)],
                diagnosticSampling=diagnosticForceLinear?"FORCE_LINEAR_IMPORT":"SOURCE_TEXTURE_COLORSPACE_IMPORT",
                diagnosticTextureAssigned=ActiveDiagnosticTexture()!=null,
                diagnosticShaderSupported=diagnosticChannelMaterial!=null &&
                    diagnosticChannelMaterial.shader!=null && diagnosticChannelMaterial.shader.isSupported,
                diagnosticMaterialSurface=diagnosticSurface,
                diagnosticSurfaces=m.diagnosticSlots==null?0:m.diagnosticSlots.Length,
                availableModels=models.Length,sourceBones=m.sourceBones,
                vertices=m.vertices,triangles=m.triangles,
                sourceMaterials=m.sourceMaterials,sourceTextures=m.sourceTextures,
                errors=loggedErrors,firstError=firstError,
                utc=DateTime.UtcNow.ToString("o")
            },true);
        }
        private void WriteReport(string reason="state_updated")
        {
            try
            {
                string report=Report();
                string d=Path.Combine(Application.persistentDataPath,"gfxlab");
                Directory.CreateDirectory(d);
                File.WriteAllText(Path.Combine(d,"multi-report.json"),report);
                if(sessionRecorder!=null)sessionRecorder.RecordState(reason,report);
            }
            catch(Exception e){Debug.LogWarning("GFX_MULTI_LOG_IO "+e.GetType().Name);}
        }
        private IEnumerator ExportAllLogs()
        {
            if(exporting)yield break;
            exporting=true;
            exportStatus="Creating ZIP of ALL test sessions...";
            WriteReport("export_all_zip_button");
            yield return null;
            string path="";
            string error="";
            bool ok=false;
            if(sessionRecorder!=null)
                ok=sessionRecorder.ExportAll(out path,out error);
            else
                error="Session recorder is missing";
            exportStatus=ok?"ZIP SAVED: "+path:"EXPORT FAILED: "+error;
            if(sessionRecorder!=null)sessionRecorder.RecordExportResult(ok,exportStatus);
            exporting=false;
        }
        private void OnApplicationPause(bool paused){if(paused)WriteReport("application_paused");}
        private void OnApplicationQuit(){WriteReport("application_quit");}
        private void OnGUI()
        {
            if(models==null || models.Length==0)return;
            Rect viewport=GfxLabViewport.BeginContent();
            float width=viewport.width,height=viewport.height;
            GUI.enabled=!automatedTestRunning;
            float scale=Mathf.Clamp(width/1750f,.65f,1.25f);
            float pad=12f*scale;
            float top=168f*scale;
            float panelWidth=285f*scale;
            var label=new GUIStyle(GUI.skin.label);
            label.fontSize=Mathf.RoundToInt(24f*scale);
            label.normal.textColor=Color.white;
            var small=new GUIStyle(label);
            small.fontSize=Mathf.RoundToInt(18f*scale);
            var button=new GUIStyle(GUI.skin.button);
            button.fontSize=Mathf.RoundToInt(21f*scale);
            GUI.Box(new Rect(8,7,width-16,top),"");
            GUI.Label(new Rect(20,10,width-36,37*scale),
                "RAFT GFX MULTI — six original meshes, source textures (Standard fallback)",label);
            var current=models[modelIndex];
            GUI.Label(new Rect(20,46*scale,width-36,30*scale),
                "Model "+current.id+" • "+current.category+" • "+current.vertices+
                " vertices • "+ModeName(),small);
            GUI.Label(new Rect(20,76*scale,width-36,30*scale),
                "GPU "+SystemInfo.graphicsDeviceName+" / "+SystemInfo.graphicsDeviceType+
                " | Original shader: NOT RESTORED",small);
            float buttonY=110f*scale;
            float buttonWidth=(width-40f)/5f;
            if(GUI.Button(new Rect(10,buttonY,buttonWidth,44*scale),"NEXT MATERIAL",button))NextMaterial();
            if(GUI.Button(new Rect(13+buttonWidth,buttonY,buttonWidth,44*scale),spin?"STOP SPIN":"SPIN",button))
            {spin=!spin;WriteReport("spin_toggled");}
            if(GUI.Button(new Rect(16+2*buttonWidth,buttonY,buttonWidth,44*scale),"RESET VIEW",button))
            {yaw=-30;pitch=15;distance=3.5f;WriteReport("camera_reset");}
            if(GUI.Button(new Rect(19+3*buttonWidth,buttonY,buttonWidth,44*scale),
                helpersVisible?"HIDE HELPERS":"SHOW HELPERS",button))
            {helpersVisible=!helpersVisible;if(studioFloor!=null)studioFloor.SetActive(helpersVisible);WriteReport("helpers_toggled");}
            float lastX=22+4*buttonWidth;
            if(GUI.Button(new Rect(lastX,buttonY,buttonWidth*.44f,44*scale),"COPY LOG",button))
            {WriteReport("copy_log_clicked");GUIUtility.systemCopyBuffer=Report();}
            if(GUI.Button(new Rect(lastX+buttonWidth*.46f,buttonY,buttonWidth*.54f,44*scale),
                exporting?"EXPORTING...":"EXPORT ZIP",button) && !exporting)
                StartCoroutine(ExportAllLogs());

            float rows=height-top-62*scale;
            GUI.Box(new Rect(8,top+10*scale,panelWidth,Mathf.Max(rows,260*scale)),"");
            GUI.Label(new Rect(18,top+14*scale,panelWidth-20,31*scale),"Original models (6)",small);
            float itemHeight=Mathf.Min(62*scale,Mathf.Max(42*scale,(rows-53*scale)/6f));
            for(int i=0;i<models.Length;i++)
            {
                string title=(i==modelIndex?"● ":"○ ")+models[i].id+"  "+models[i].category.Replace("_"," ");
                if(GUI.Button(new Rect(16,top+48*scale+i*itemHeight,panelWidth-17,itemHeight-3*scale),title,button))
                    ChangeModel(i);
            }
            // Explicit GPU channel test of the original Texture2D samples.
            // This is a NEW inspector shader: never relabel it as Shader48 or claim PC parity.
            float probeWidth=Mathf.Clamp(width*.28f,190f,560f);
            float px=width-probeWidth-14*scale;
            float py=top+13*scale;
            float pbH=43*scale;
            GUI.Box(new Rect(px-7*scale,py-6*scale,probeWidth+14*scale,
                Mathf.Min(height-py-53*scale,probeWidth+170*scale)),"");
            GUI.Label(new Rect(px,py,probeWidth,29*scale),"SOURCE TEXTURE / GPU CHANNEL (diagnostic only)",small);
            if(GUI.Button(new Rect(px,py+30*scale,probeWidth*.48f,pbH),
                DiagnosticRoleNames[diagnosticRole],button))StepDiagnosticRole();
            if(GUI.Button(new Rect(px+probeWidth*.5f,py+30*scale,probeWidth*.48f,pbH),
                DiagnosticChannelNames[diagnosticChannel],button))StepDiagnosticChannel();
            if(GUI.Button(new Rect(px,py+78*scale,probeWidth*.48f,pbH),
                diagnosticForceLinear?"FORCE LINEAR":"SOURCE COLORSPACE",button))
            {diagnosticForceLinear=!diagnosticForceLinear;WriteReport("sampling_mode_changed");}
            var mm=models[modelIndex];
            if(GUI.Button(new Rect(px+probeWidth*.5f,py+78*scale,probeWidth*.48f,pbH),
                "SURFACE "+(diagnosticSurface+1)+"/"+(mm.diagnosticSlots==null?0:mm.diagnosticSlots.Length),button))
            {
                diagnosticSurface=(diagnosticSurface+1)%Mathf.Max(1,mm.diagnosticSlots==null?1:mm.diagnosticSlots.Length);
                WriteReport("material_surface_changed");
            }
            var tex=ActiveDiagnosticTexture();
            float previewH=Mathf.Max(30f,Mathf.Min(probeWidth*.82f,
                height-(py+166*scale)-61*scale));
            var previewRect=new Rect(px+6*scale,py+132*scale,probeWidth-12*scale,previewH);
            if(tex!=null && diagnosticChannelMaterial!=null &&
                diagnosticChannelMaterial.shader!=null && diagnosticChannelMaterial.shader.isSupported)
            {
                if(Event.current.type==EventType.Repaint)
                {
                    diagnosticChannelMaterial.SetFloat("_Channel",diagnosticChannel);
                    Graphics.DrawTexture(previewRect,tex,diagnosticChannelMaterial);
                }
            }
            else GUI.Label(previewRect,"NO SOURCE TEXTURE / PROBE UNSUPPORTED",small);
            GUI.Label(new Rect(px,py+139*scale+previewH,probeWidth,24*scale),
                "Not original Shader48. Copy log + screenshot.",small);
            GUI.Label(new Rect(panelWidth+20,height-63*scale,width-panelWidth-35,27*scale),
                exportStatus,small);
            GUI.Label(new Rect(panelWidth+20,height-39*scale,width-panelWidth-40,30*scale),
                "AUTO LOG: every mode/channel/sampling/surface + full errors. EXPORT ZIP to Download/Games/cl/test/g/",small);
            GUI.enabled=true;
            GUI.EndGroup();
        }
    }
}
