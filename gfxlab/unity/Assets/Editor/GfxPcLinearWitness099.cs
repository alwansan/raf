using System;
using System.IO;
using UnityEditor;
using UnityEngine;
namespace RaftGraphicsLabEditor
{
    public static class GfxPcLinearWitness099
    {
        [Serializable] private class Baseline {public string sourceSHA;public int sourceColorSpaceCode;}
        [Serializable] private class Safe
        {
            public string experiment="GFX-MULTI-099";
            public string activePlayerSettingsColorSpace;
            public bool originalColorBaselinePinnedLinear;
            public GfxOriginalStandardPcWitness098.SafeReport originalStageCompile;
            public bool originalShaderRestored=false,phase_closed=false;
        }
        public static void Build()
        {
            var baseline=JsonUtility.FromJson<Baseline>(File.ReadAllText("Assets/Gfx098Private/pc-compile-requests.json"));
            if(baseline.sourceSHA!="15964ea8f246b6e076ce26b60931ee2e1a9a2385"||baseline.sourceColorSpaceCode!=1)throw new InvalidOperationException("GFX099_SOURCE_BASELINE");
            PlayerSettings.colorSpace=ColorSpace.Linear;
            var before=PlayerSettings.colorSpace;
            var compile=GfxOriginalStandardPcWitness098.Run();
            if(PlayerSettings.colorSpace!=before||before!=ColorSpace.Linear)throw new InvalidOperationException("GFX099_REFERENCE_COLOR_DRIFT");
            var report=new Safe{activePlayerSettingsColorSpace=before.ToString(),originalColorBaselinePinnedLinear=true,originalStageCompile=compile};
            File.WriteAllText("gfx099-PC-linear-safe.json",JsonUtility.ToJson(report,true));
            Debug.Log("GFX099_PC_LINEAR_REFERENCE_SAFE "+JsonUtility.ToJson(report,false));
        }
    }
}
