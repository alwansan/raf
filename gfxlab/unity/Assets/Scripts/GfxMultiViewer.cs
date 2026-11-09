using System;
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
        }

        public Camera viewingCamera;
        public Model[] models;
        public GameObject studioFloor;
        public bool defaultHideHelpers = true;

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
        private const string Experiment="GFX-MULTI-003";

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
            helpersVisible=!defaultHideHelpers;
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
            UpdateMaterials();
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
                default:return "SOURCE_PBR_STANDARD_APPROX";
            }
        }
        private void UpdateMaterials()
        {
            var model=models[modelIndex];
            foreach(var slot in model.slots)
            {
                if(slot==null || slot.renderer==null)continue;
                Material[] materials = materialMode==0 ? slot.whiteLit :
                    materialMode==1 ? slot.whiteUnlit :
                    materialMode==2 ? slot.sourceAlbedo : slot.sourcePbr;
                if(materials==null || materials.Length==0)
                    throw new InvalidOperationException("GFX_MULTI_MATERIAL_MODE_EMPTY");
                slot.renderer.sharedMaterials=materials;
            }
            WriteReport();
        }
        private void ChangeModel(int index)
        {
            if(models==null||models.Length==0)return;
            modelIndex=(index+models.Length)%models.Length;
            for(int i=0;i<models.Length;i++)models[i].root.SetActive(i==modelIndex);
            yaw=-30f;pitch=15f;distance=3.5f;pinchPrevious=0;
            UpdateMaterials();
            Debug.Log("GFX_MULTI_SELECTED model="+models[modelIndex].id+" shader_exact=false");
        }
        private void NextMaterial()
        {
            materialMode=(materialMode+1)%4;
            UpdateMaterials();
        }
        private void Update()
        {
            if(viewingCamera==null || models==null || models.Length<1)return;
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
                experiment=Experiment,modelId=m.id,category=m.category,
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
                availableModels=models.Length,sourceBones=m.sourceBones,
                vertices=m.vertices,triangles=m.triangles,
                sourceMaterials=m.sourceMaterials,sourceTextures=m.sourceTextures,
                errors=loggedErrors,firstError=firstError,
                utc=DateTime.UtcNow.ToString("o")
            },true);
        }
        private void WriteReport()
        {
            try
            {
                string d=Path.Combine(Application.persistentDataPath,"gfxlab");
                Directory.CreateDirectory(d);
                File.WriteAllText(Path.Combine(d,"multi-report.json"),Report());
            }
            catch(Exception e){Debug.LogWarning("GFX_MULTI_LOG_IO "+e.GetType().Name);}
        }
        private void OnApplicationPause(bool paused){if(paused)WriteReport();}
        private void OnApplicationQuit(){WriteReport();}
        private void OnGUI()
        {
            if(models==null || models.Length==0)return;
            float scale=Mathf.Clamp(Screen.width/1750f,.65f,1.25f);
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
            GUI.Box(new Rect(8,7,Screen.width-16,top),"");
            GUI.Label(new Rect(20,10,Screen.width-36,37*scale),
                "RAFT GFX MULTI — six original meshes, source textures (Standard fallback)",label);
            var current=models[modelIndex];
            GUI.Label(new Rect(20,46*scale,Screen.width-36,30*scale),
                "Model "+current.id+" • "+current.category+" • "+current.vertices+
                " vertices • "+ModeName(),small);
            GUI.Label(new Rect(20,76*scale,Screen.width-36,30*scale),
                "GPU "+SystemInfo.graphicsDeviceName+" / "+SystemInfo.graphicsDeviceType+
                " | Original shader: NOT RESTORED",small);
            float buttonY=110f*scale;
            float buttonWidth=(Screen.width-40f)/5f;
            if(GUI.Button(new Rect(10,buttonY,buttonWidth,44*scale),"NEXT MATERIAL",button))NextMaterial();
            if(GUI.Button(new Rect(13+buttonWidth,buttonY,buttonWidth,44*scale),spin?"STOP SPIN":"SPIN",button))spin=!spin;
            if(GUI.Button(new Rect(16+2*buttonWidth,buttonY,buttonWidth,44*scale),"RESET VIEW",button))
            {yaw=-30;pitch=15;distance=3.5f;}
            if(GUI.Button(new Rect(19+3*buttonWidth,buttonY,buttonWidth,44*scale),
                helpersVisible?"HIDE HELPERS":"SHOW HELPERS",button))
            {helpersVisible=!helpersVisible;if(studioFloor!=null)studioFloor.SetActive(helpersVisible);}
            if(GUI.Button(new Rect(22+4*buttonWidth,buttonY,buttonWidth,44*scale),"COPY LOG",button))
            {WriteReport();GUIUtility.systemCopyBuffer=Report();}

            float rows=Screen.height-top-62*scale;
            GUI.Box(new Rect(8,top+10*scale,panelWidth,Mathf.Max(rows,260*scale)),"");
            GUI.Label(new Rect(18,top+14*scale,panelWidth-20,31*scale),"Original models (6)",small);
            float itemHeight=Mathf.Min(62*scale,Mathf.Max(42*scale,(rows-53*scale)/6f));
            for(int i=0;i<models.Length;i++)
            {
                string title=(i==modelIndex?"● ":"○ ")+models[i].id+"  "+models[i].category.Replace("_"," ");
                if(GUI.Button(new Rect(16,top+48*scale+i*itemHeight,panelWidth-17,itemHeight-3*scale),title,button))
                    ChangeModel(i);
            }
            GUI.Label(new Rect(panelWidth+20,Screen.height-39*scale,Screen.width-panelWidth-40,30*scale),
                "Rotate: drag | Zoom: pinch | Materials: WHITE / UNLIT / ALBEDO / PBR | COPY LOG",small);
        }
    }
}
