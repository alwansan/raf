using System;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace RaftGraphicsLab
{
    public static class GfxLabViewport
    {
        public static Rect SafeGuiRect()
        {
            var a=Screen.safeArea;
            return new Rect(a.x,Screen.height-a.y-a.height,a.width,a.height);
        }
        public static Rect BeginContent()
        {
            var safe=SafeGuiRect();float h=GfxUnifiedLabMenu098.Active?GfxUnifiedLabMenu098.ToolbarHeight:0;
            var area=new Rect(safe.x,safe.y+h,safe.width,Mathf.Max(1,safe.height-h));
            GUI.BeginGroup(area);return new Rect(0,0,area.width,area.height);
        }
    }
    public sealed class GfxUnifiedLabMenu098 : MonoBehaviour
    {
        public static bool Active {get;private set;}
        public static float ToolbarHeight {get{return Mathf.Clamp(Screen.width/1400f,.7f,1.5f)*52f;}}
        private string status="GFX098 | original models + saved-material candidate + affine GPU reference";
        private void Awake()
        {
            if(Active){Destroy(gameObject);return;}
            Active=true;DontDestroyOnLoad(gameObject);Screen.orientation=ScreenOrientation.LandscapeLeft;
        }
        private void OnDestroy(){if(gameObject.scene.name=="DontDestroyOnLoad")Active=false;}
        private void OnGUI()
        {
            GUI.depth=-1000;var safe=GfxLabViewport.SafeGuiRect();float h=ToolbarHeight;
            GUI.BeginGroup(new Rect(safe.x,safe.y,safe.width,h));
            GUI.Box(new Rect(0,0,safe.width,h),"");
            var style=new GUIStyle(GUI.skin.button);style.fontSize=Mathf.RoundToInt(h*.25f);
            float w=safe.width*.17f;
            var matrix=FindObjectOfType<GfxModelMatrixProbe098>();bool running=matrix!=null&&matrix.Running;
            GUI.enabled=!running;
            if(GUI.Button(new Rect(5,5,w,h-10),"6 MODELS",style)&&SceneManager.GetActiveScene().buildIndex!=0)SceneManager.LoadScene(0);
            if(GUI.Button(new Rect(w+9,5,w,h-10),"AFFINE / GPU",style)&&SceneManager.GetActiveScene().buildIndex!=1)SceneManager.LoadScene(1);
            if(GUI.Button(new Rect(2*w+13,5,w,h-10),"AUTO 12 CASES",style)&&matrix!=null)matrix.RunMatrix();
            GUI.enabled=true;
            if(GUI.Button(new Rect(3*w+17,5,w,h-10),"EXPORT ALL ZIP",style))
            {
                var recorder=FindObjectOfType<GfxSessionRecorder>();string path="",error="";
                bool ok=recorder!=null&&recorder.ExportAll(out path,out error);
                status=ok?"SAVED: "+path:"EXPORT FAILED: "+error;
                if(recorder!=null)recorder.RecordExportResult(ok,status);
            }
            var label=new GUIStyle(GUI.skin.label);label.fontSize=Mathf.RoundToInt(h*.22f);label.wordWrap=true;
            GUI.Label(new Rect(4*w+24,6,safe.width-4*w-30,h-8),running?"Auto captures running; wait for ZIP export":status,label);
            GUI.EndGroup();
        }
    }
}
