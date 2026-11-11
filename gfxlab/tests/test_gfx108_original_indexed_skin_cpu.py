"""GFX108 mocked exact original Mesh/Renderer/Transform source bridge."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from gfxlab.tools.gfx108_original_indexed_skin_cpu import inspect_exact_source_skin

OWNER="resources.assets"
def ptr(x):return {"m_FileID":0,"m_PathID":x}
def obj(kind,d,parsed=None):
    return SimpleNamespace(type=SimpleNamespace(name=kind),
        read_typetree=lambda check_read=False:d,
        parse_as_object=lambda:parsed)
def matrix(tx=0.):
    m={"e%d%d"%(r,c):(1. if r==c else 0.) for r in range(4) for c in range(4)}
    m["e03"]=tx;return m
def transform(x=0.,parent=0):
    return {"m_LocalPosition":{"x":x,"y":0.,"z":0.},
            "m_LocalRotation":{"x":0.,"y":0.,"z":0.,"w":1.},
            "m_LocalScale":{"x":1.,"y":1.,"z":1.},
            "m_Father":ptr(parent)}
def case(missing_vertices=False,corrupt_weights=False):
    mesh={"m_VertexData":{"m_VertexCount":2},
          "m_BindPose":[matrix(0.),matrix(-5.)],
          "m_Skin":[{"weight":[1.,0.,0.,0.],"boneIndex":[0,0,0,0]},
                    {"weight":[.5,.5,0.,0.],"boneIndex":[0,1,0,0]}]}
    if corrupt_weights:mesh["m_Skin"][1]["weight"][0]=.8
    positions=SimpleNamespace(
        m_BoneWeights=[tuple(row["weight"]) for row in mesh["m_Skin"]],
        m_BoneIndices=[tuple(row["boneIndex"]) for row in mesh["m_Skin"]])
    if not missing_vertices:
        positions.m_Vertices=[(1.,0.,0.),(1.,0.,0.)]
    renderer={"m_Mesh":ptr(100),"m_GameObject":ptr(300),
              "m_Bones":[ptr(11),ptr(12)]}
    types={OWNER:{
        100:obj("Mesh",mesh,positions),
        200:obj("SkinnedMeshRenderer",renderer),
        11:obj("Transform",transform(0.)),
        12:obj("Transform",transform(5.,11))}}
    entry={"id":"M01","owner":OWNER,"mesh_pid":100,
           "game_object_pid":300,"source_bones":2}
    return entry,types,{OWNER:[]}

class TestGFX108AuthenticSourceBridge(unittest.TestCase):
    def run_source_mock(self,entry,types,externals):
        with patch("gfxlab.tools.gfx108_original_indexed_skin_cpu.direct_mesh_handler",
                   side_effect=lambda reader:reader.parse_as_object()):
            return inspect_exact_source_skin(entry,types,externals)
    def test_two_vertex_original_same_position_kept(self):
        a,t,e=case()
        out=self.run_source_mock(a,t,e)
        self.assertEqual(out["status"],"SOURCE_INDEXED_LBS_COMPUTED")
        self.assertEqual(out["source_vertex_count"],2)
        self.assertEqual(out["vertices_cpu_deformed"],2)
        self.assertTrue(out["original_indexed_vertex_weights_preserved"])
        self.assertFalse(out["android_gpu_skinning_verified"])
    def test_missing_direct_source_vertex_stream_is_not_fabricated(self):
        a,t,e=case(missing_vertices=True)
        out=self.run_source_mock(a,t,e)
        self.assertEqual(out["status"],"GFX108_DIRECT_VERTEX_POSITIONS_UNAVAILABLE")
        self.assertFalse(out["cpu_original_vertices_deformed"])
    def test_invalid_original_skin_weight_fails_closed(self):
        a,t,e=case(corrupt_weights=True)
        out=self.run_source_mock(a,t,e)
        self.assertEqual(out["status"],"GFX108_BONE_WEIGHT_SUM_NOT_NORMALIZED")
        self.assertFalse(out["cpu_original_vertices_deformed"])
    def test_source_mesh_renderer_collision_without_go_identity_rejected(self):
        a,t,e=case()
        a.pop("game_object_pid")
        t[OWNER][201]=obj("SkinnedMeshRenderer",{
            "m_Mesh":ptr(100),"m_GameObject":ptr(301),"m_Bones":[ptr(11),ptr(99)]})
        out=self.run_source_mock(a,t,e)
        self.assertEqual(out["status"],"AUTHENTIC_RENDERER_AMBIGUOUS")
        self.assertFalse(out["cpu_original_vertices_deformed"])

if __name__=="__main__": unittest.main()
