import unittest
import tempfile
from pathlib import Path
from tools.gt_skybox_actual_abi import audit as a
class Controls(unittest.TestCase):
    def test_read_compiler_output_label_first(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            for stage in ("vs","fs"):(p/("abi-reference-"+stage+".spv")).write_bytes(b"fixture")
            seen=[]
            def reader(path):
                seen.append(path.name)
                return {"entryPoints":[{"name":"gt_vs_main" if path.stem.endswith("-vs") else "gt_fs_main"}]}
            self.assertEqual(len(a.read_compiled_reference(p,a.REFERENCE_LABEL,reader)),2)
            self.assertEqual(seen,["abi-reference-vs.spv","abi-reference-fs.spv"])
    def test_reversed_output_names_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            for stage in ("vs","fs"):(p/(stage+"-abi-reference.spv")).write_bytes(b"fixture")
            with self.assertRaisesRegex(ValueError,"source_abi_reference_file_missing"):
                a.read_compiled_reference(p,a.REFERENCE_LABEL,lambda _:None)
    def test_stage_identity_required(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            for stage in ("vs","fs"):(p/("abi-reference-"+stage+".spv")).write_bytes(b"fixture")
            with self.assertRaisesRegex(ValueError,"source_abi_reference_stage_identity"):
                a.read_compiled_reference(p,a.REFERENCE_LABEL,lambda _:{"entryPoints":[{"name":"gt_fs_main"}]})
    def test_descriptor_different_name_same_slot(self):
        def r(name):return {"separate_images":[{"name":name,"type":"texture2D","set":0,"binding":2}]}
        result=a.descriptor_profile(r("original"),r("other"))
        self.assertEqual(result["shared_different_name_or_kind_shape"],1)
        self.assertEqual(result["shared_exact_name_kind_shape"],0)
    def test_descriptor_duplicate_slot_not_overwritten(self):
        item={"name":"tex","type":"texture2D","set":0,"binding":2}
        left={"separate_images":[item,item]}
        right={"separate_images":[item]}
        result=a.descriptor_profile(left,right)
        self.assertEqual(result["vertex_duplicate_slots"],1)
        self.assertEqual(result["shared_ambiguous_slots"],1)
        self.assertEqual(result["shared_exact_name_kind_shape"],0)
    def test_exact_map(self):
        self.assertTrue(a.map_profile({"x":4},{"x":4})["exact_map"])
    def test_name_not_offset(self):
        self.assertFalse(a.map_profile({"x":4},{"x":8})["exact_map"])
    def test_extra(self):
        self.assertEqual(a.map_profile({"x":4},{"x":4,"y":8})["extra"],1)
    def test_missing_owner(self):
        r=a.map_profile({("old","x"):4},{("new","x"):4})
        self.assertEqual((r["exact"],r["missing"],r["extra"]),(0,1,1))
    def test_stride(self):
        def r(stride):return {"ubos":[{"name":"B","type":"T"}],"types":{"T":{"members":[{"name":"x","offset":0,"type":"mat4","matrix_stride":stride}]}}}
        self.assertFalse(a.map_profile(a.members(r(16)),a.members(r(32)))["exact_map"])
    def test_duplicate(self):
        r={"ubos":[{"name":"B","type":"T"}],"types":{"T":{"members":[{"name":"x","offset":0},{"name":"x","offset":4}]}}}
        with self.assertRaises(ValueError):a.members(r)
    def test_serialized_member(self):
        p={"m_CommonParameters":{"m_ConstantBuffers":[{"m_NameIndex":0,"m_VectorParams":[{"m_NameIndex":1,"m_Index":16}]}],
           "m_ConstantBufferBindings":[{"m_NameIndex":0,"m_Index":2}],"m_TextureParams":[{"m_NameIndex":2}]}}
        m,t,b,v=a.metadata_members(p,(None,0,{}),[],{0:"B",1:"x",2:"Tex"})
        self.assertEqual(m,{("B","x"):16});self.assertEqual(t,{"Tex"});self.assertEqual(b,{"B":2});self.assertFalse(v)
    def test_serialized_wrong_offset(self):
        p={"m_CommonParameters":{"m_ConstantBuffers":[{"m_NameIndex":0,"m_VectorParams":[{"m_NameIndex":1,"m_Index":32}]}]}}
        m,_,_,_=a.metadata_members(p,(None,0,{}),[],{0:"B",1:"x"})
        self.assertFalse(a.map_profile({("B","x"):16},m)["exact_map"])
if __name__=="__main__":unittest.main()
