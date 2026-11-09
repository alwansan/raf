using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Globalization;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace RaftGraphicsLabEditor
{
    /// <summary>
    /// Source-authentic fallback when Unity 2021 ModelImporter returns an empty mesh
    /// for a valid UnityPy Mesh.export() OBJ (observed M02 in CI42712833407).
    /// Reconstructs original vertex positions, UV and normals and original
    /// material-group triangles; does not fabricate a source shader or animation.
    /// </summary>
    internal static class GfxOriginalObjImporter
    {
        private struct Corner
        {
            public int p,uv,n;
            public Corner(int a,int b,int c){p=a;uv=b;n=c;}
        }
        private static readonly CultureInfo Inv=CultureInfo.InvariantCulture;

        private static float Float(string token)
        {
            float value=float.Parse(token,NumberStyles.Float,Inv);
            if(float.IsInfinity(value)||float.IsNaN(value))
                throw new InvalidOperationException("GFX_MULTI_NONFINITE_OBJ_VERTEX");
            return value;
        }
        private static int Index(string value,int count)
        {
            if(string.IsNullOrEmpty(value))
                throw new InvalidOperationException("GFX_MULTI_MISSING_OBJ_INDEX");
            int index=int.Parse(value,NumberStyles.Integer,Inv);
            if(index==0)throw new InvalidOperationException("GFX_MULTI_OBJ_ZERO_INDEX");
            index=index>0?index-1:count+index;
            if(index<0||index>=count)
                throw new InvalidOperationException("GFX_MULTI_OBJ_OUT_OF_BOUNDS");
            return index;
        }
        private static string[] Split(string line)
        {
            return line.Split((char[])null,StringSplitOptions.RemoveEmptyEntries);
        }
        private static Corner ParseCorner(string corner,int pCount,int uvCount,int nCount)
        {
            string[] tokens=corner.Split('/');
            if(tokens.Length<1||tokens.Length>3)
                throw new InvalidOperationException("GFX_MULTI_OBJ_CORNER_MALFORMED");
            int p=Index(tokens[0],pCount);
            int uv=tokens.Length>1&&!string.IsNullOrEmpty(tokens[1])?Index(tokens[1],uvCount):-1;
            int n=tokens.Length>2&&!string.IsNullOrEmpty(tokens[2])?Index(tokens[2],nCount):-1;
            return new Corner(p,uv,n);
        }

        public static GameObject Load(string objFile,string originalId)
        {
            if(!File.Exists(objFile))
                throw new InvalidOperationException("GFX_MULTI_SOURCE_OBJ_NOT_FOUND");
            var positions=new List<Vector3>();
            var uvs=new List<Vector2>();
            var normals=new List<Vector3>();
            var finalPositions=new List<Vector3>();
            var finalUV=new List<Vector2>();
            var finalNormals=new List<Vector3>();
            var compositeToIndex=new Dictionary<string,int>();
            var groups=new List<List<int>>();
            var materialIndices=new Dictionary<string,int>(StringComparer.Ordinal);
            int activeGroup=-1;
            int faces=0;
            foreach(string raw in File.ReadLines(objFile))
            {
                string line=raw.Trim();
                if(line.StartsWith("v ",StringComparison.Ordinal))
                {
                    var v=Split(line);
                    if(v.Length<4)throw new InvalidOperationException("GFX_MULTI_OBJ_VERTEX_BAD");
                    positions.Add(new Vector3(Float(v[1]),Float(v[2]),Float(v[3])));
                }
                else if(line.StartsWith("vt ",StringComparison.Ordinal))
                {
                    var v=Split(line);
                    if(v.Length<3)throw new InvalidOperationException("GFX_MULTI_OBJ_UV_BAD");
                    uvs.Add(new Vector2(Float(v[1]),Float(v[2])));
                }
                else if(line.StartsWith("vn ",StringComparison.Ordinal))
                {
                    var v=Split(line);
                    if(v.Length<4)throw new InvalidOperationException("GFX_MULTI_OBJ_NORMAL_BAD");
                    normals.Add(new Vector3(Float(v[1]),Float(v[2]),Float(v[3])));
                }
                else if(line.StartsWith("usemtl ",StringComparison.Ordinal))
                {
                    string material=line.Substring(7);
                    if(string.IsNullOrWhiteSpace(material))
                        throw new InvalidOperationException("GFX_MULTI_OBJ_MATERIAL_ID_EMPTY");
                    if(!materialIndices.TryGetValue(material,out activeGroup))
                    {
                        activeGroup=groups.Count;
                        materialIndices[material]=activeGroup;
                        groups.Add(new List<int>());
                    }
                }
                else if(line.StartsWith("f ",StringComparison.Ordinal))
                {
                    if(activeGroup<0)
                    {
                        activeGroup=0;
                        if(groups.Count==0)groups.Add(new List<int>());
                    }
                    var f=Split(line);
                    if(f.Length<4||f.Length>7)
                        throw new InvalidOperationException("GFX_MULTI_OBJ_FACE_BAD");
                    Corner[] corners=new Corner[f.Length-1];
                    for(int i=1;i<f.Length;i++)
                        corners[i-1]=ParseCorner(f[i],positions.Count,uvs.Count,normals.Count);
                    for(int k=1;k<corners.Length-1;k++)
                    {
                        Corner[] tri={corners[0],corners[k],corners[k+1]};
                        foreach(Corner corner in tri)
                        {
                            if(corner.uv<0)
                                throw new InvalidOperationException("GFX_MULTI_SOURCE_OBJ_UV_UNBOUND");
                            string key=corner.p+"/"+corner.uv+"/"+corner.n;
                            if(!compositeToIndex.TryGetValue(key,out int index))
                            {
                                index=finalPositions.Count;
                                compositeToIndex[key]=index;
                                finalPositions.Add(positions[corner.p]);
                                finalUV.Add(uvs[corner.uv]);
                                finalNormals.Add(corner.n<0 ? Vector3.up : normals[corner.n]);
                            }
                            groups[activeGroup].Add(index);
                        }
                        faces++;
                    }
                }
            }
            if(positions.Count<128||positions.Count>140000||faces==0||
               finalPositions.Count<1||groups.Count<1)
                throw new InvalidOperationException("GFX_MULTI_OBJ_TOPOLOGY_NOT_REAL");
            if(groups.Any(g=>g.Count==0))
                throw new InvalidOperationException("GFX_MULTI_EMPTY_SOURCE_MATERIAL_SUBMESH");
            Mesh mesh=new Mesh();
            mesh.name="OriginalSourceMesh_"+originalId;
            if(finalPositions.Count>65535)mesh.indexFormat=IndexFormat.UInt32;
            mesh.SetVertices(finalPositions);
            mesh.SetUVs(0,finalUV);
            mesh.SetNormals(finalNormals);
            mesh.subMeshCount=groups.Count;
            for(int i=0;i<groups.Count;i++)mesh.SetTriangles(groups[i],i);
            mesh.RecalculateBounds();
            if(finalNormals.All(n=>n.sqrMagnitude<.00001f))mesh.RecalculateNormals();
            try{mesh.RecalculateTangents();}catch(Exception){/* source normal map mode still diagnostic; preserve geometry */}
            string assetPath="Assets/GfxMultiGenerated/"+originalId+"_NativeMesh.asset";
            if(AssetDatabase.LoadAssetAtPath<Mesh>(assetPath)!=null)
                throw new InvalidOperationException("GFX_MULTI_MESH_ASSET_COLLISION");
            AssetDatabase.CreateAsset(mesh,assetPath);
            var root=new GameObject("TypedOriginalSource_"+originalId);
            var filter=root.AddComponent<MeshFilter>();
            filter.sharedMesh=mesh;
            root.AddComponent<MeshRenderer>();
            Debug.Log("GFX_MULTI_OBJ_AUTHENTIC_FALLBACK model="+originalId+
                " source_vertices="+positions.Count+" parsed_triangles="+faces+
                " material_submeshes="+groups.Count+" unity_vertices="+finalPositions.Count+
                " original_shader_exact=false");
            return root;
        }
    }
}
