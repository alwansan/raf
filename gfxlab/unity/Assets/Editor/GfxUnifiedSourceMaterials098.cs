using System;
using System.IO;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using RaftGraphicsLab;

namespace RaftGraphicsLabEditor
{
    public static class GfxUnifiedSourceMaterials098
    {
        [Serializable] public class FloatValue{public string name;public float value;}
        [Serializable] public class ColorValue{public string name;public float[] value;}
        [Serializable] public class Tag{public string name;public string value;}
        [Serializable] public class TextureLink
        {
            public string property,role,file,alias,normalCandidateFile;
            public bool sRGB;public int sourceMipCount;public float[] scale,offset;
        }
        [Serializable] public class SourceMaterial
        {
            public string alias;public FloatValue[] floats;public ColorValue[] colors;
            public string[] keywords,disabledPasses;public Tag[] tags;
            public int renderQueue,lightmapFlags;public bool instancing,doubleSidedGI;
            public TextureLink[] textures;
        }
        [Serializable] public class Config{public string model,sourceSHA;public SourceMaterial[] materials;}
        private static readonly Dictionary<string,Material> Materials=new Dictionary<string,Material>();
        private static readonly Dictionary<string,Texture2D> Textures=new Dictionary<string,Texture2D>();
        private static Texture2D Import(string folder,TextureLink link)
        {
            if(Textures.TryGetValue(link.alias,out var found))return found;
            string file=link.role=="normal"?link.normalCandidateFile:link.file;
            if(string.IsNullOrEmpty(file)||file.Contains("/")||file.Contains("\\")||file.Contains(".."))throw new InvalidOperationException("GFX098_TEXTURE_FILE");
            string original=folder+"/"+file;string copy="Assets/Gfx098Generated/"+link.alias+".png";
            File.Copy(original,copy,true);AssetDatabase.ImportAsset(copy,ImportAssetOptions.ForceSynchronousImport);
            var imp=AssetImporter.GetAtPath(copy) as TextureImporter;
            if(imp==null)throw new InvalidOperationException("GFX098_TEXTURE_IMPORTER");
            imp.textureType=link.role=="normal"?TextureImporterType.NormalMap:TextureImporterType.Default;
            imp.sRGBTexture=link.role=="normal"?false:link.sRGB;
            // Original level zero is decoded in the private runner. Mips are
            // explicitly regenerated; original mip-chain equality is unproven.
            imp.mipmapEnabled=true;imp.textureCompression=TextureImporterCompression.Uncompressed;
            imp.maxTextureSize=4096;imp.filterMode=FilterMode.Bilinear;imp.wrapMode=TextureWrapMode.Repeat;
            imp.anisoLevel=1;imp.mipMapBias=0;imp.SaveAndReimport();
            var texture=AssetDatabase.LoadAssetAtPath<Texture2D>(copy);
            if(texture==null)throw new InvalidOperationException("GFX098_TEXTURE_FAILED");
            Textures.Add(link.alias,texture);return texture;
        }
        private static Material MaterialFor(string folder,SourceMaterial source)
        {
            if(Materials.TryGetValue(source.alias,out var found))return found;
            var shader=Shader.Find("Standard");if(shader==null)throw new InvalidOperationException("GFX098_STANDARD_MISSING");
            var mat=new Material(shader);mat.name=source.alias+"_SOURCE_SAVED_STANDARD_CANDIDATE";
            foreach(var p in source.floats)
            {if(!mat.HasProperty(p.name))throw new InvalidOperationException("GFX098_SOURCE_FLOAT_NOT_DECLARED");mat.SetFloat(p.name,p.value);}
            foreach(var p in source.colors)
            {if(!mat.HasProperty(p.name)||p.value==null||p.value.Length!=4)throw new InvalidOperationException("GFX098_SOURCE_COLOR_NOT_DECLARED");mat.SetColor(p.name,new Color(p.value[0],p.value[1],p.value[2],p.value[3]));}
            foreach(var link in source.textures)
            {
                if(!mat.HasProperty(link.property))throw new InvalidOperationException("GFX098_SOURCE_TEXENV_NOT_DECLARED");
                mat.SetTexture(link.property,link.role=="null"?null:Import(folder,link));
                mat.SetTextureScale(link.property,new Vector2(link.scale[0],link.scale[1]));
                mat.SetTextureOffset(link.property,new Vector2(link.offset[0],link.offset[1]));
            }
            mat.shaderKeywords=source.keywords;mat.renderQueue=source.renderQueue;mat.enableInstancing=source.instancing;
            mat.doubleSidedGI=source.doubleSidedGI;mat.globalIlluminationFlags=(MaterialGlobalIlluminationFlags)source.lightmapFlags;
            if(source.tags!=null)foreach(var tag in source.tags)mat.SetOverrideTag(tag.name,tag.value);
            if(source.disabledPasses!=null)foreach(var name in source.disabledPasses)mat.SetShaderPassEnabled(name,false);
            foreach(var p in source.floats)if(mat.GetFloat(p.name)!=p.value)throw new InvalidOperationException("GFX098_FLOAT_READBACK_MISMATCH");
            AssetDatabase.CreateAsset(mat,"Assets/Gfx098Generated/"+source.alias+".mat");Materials.Add(source.alias,mat);return mat;
        }
        public static void Apply(GfxMultiViewer viewer)
        {
            Materials.Clear();Textures.Clear();Directory.CreateDirectory("Assets/Gfx098Generated");AssetDatabase.Refresh();
            int slots=0;
            foreach(var model in viewer.models)
            {
                string folder="Assets/MultiModels/"+model.id;
                var config=JsonUtility.FromJson<Config>(File.ReadAllText(folder+"/source098.json"));
                if(config.model!=model.id||config.sourceSHA!="15964ea8f246b6e076ce26b60931ee2e1a9a2385")throw new InvalidOperationException("GFX098_SOURCE_IDENTITY");
                int cursor=0;
                foreach(var slot in model.slots)
                {
                    int n=slot.sourcePbr.Length;slot.sourceSavedStandard=new Material[n];
                    for(int i=0;i<n;i++)slot.sourceSavedStandard[i]=MaterialFor(folder,config.materials[cursor++]);
                }
                if(cursor!=config.materials.Length)throw new InvalidOperationException("GFX098_MATERIAL_SLOT_TOPOLOGY");slots+=cursor;
            }
            if(slots!=7||Materials.Count!=6||Textures.Count!=18)throw new InvalidOperationException("GFX098_SOURCE_ALIAS_COUNTS");
            viewer.sourceSavedCandidateAvailable=true;viewer.experimentOverride="GFX-MULTI-098";
            Debug.Log("GFX098_SOURCE_SAVED_VALUES_APPLIED slots=7 unique_materials=6 unique_textures=18 originalShaderRestored=false rig_restored=false mips_regenerated=true normal_AG_candidate=true");
        }
    }
}
