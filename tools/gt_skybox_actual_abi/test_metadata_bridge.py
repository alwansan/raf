import struct
import unittest
from tools.gt_skybox_actual_abi import metadata_bridge as b

SHAPE=("vec4",(),None,None,False)
def expected(name="x",offset=16):return [("Original","Generated",name,offset,SHAPE)]
def metadata(name="x",offset=16,index=3):
    return {"groups":{"Generated":{"members":{name:offset},"size":64}},
            "buffers":{"Generated":index},"textures":{},"variant":True}
def slot(binding=3,offset=16,typ="vec4",set_id=0):
    return {"kind":"ubos","set":set_id,"binding":binding,"members":[{"offset":offset,"type":typ}]}

class Controls(unittest.TestCase):
    def test_direct(self):
        r=b.member_join(expected(),metadata(),[slot()],"direct")
        self.assertEqual(r["unique_descriptor_offset_shape_join"],1)
        self.assertEqual(r["original_offset_preserved"],1)
    def test_relocated_offset_not_preserved(self):
        r=b.member_join(expected(),metadata(offset=32),[slot(offset=32)],"direct")
        self.assertEqual((r["original_offset_preserved"],r["original_offset_relocated"]),(0,1))
    def test_wrong_type(self):
        r=b.member_join(expected(),metadata(),[slot(typ="float")],"direct")
        self.assertEqual(r["unique_descriptor_offset_shape_join"],0)
    def test_same_shape_wrong_offset(self):
        r=b.member_join(expected(),metadata(),[slot(offset=32)],"direct")
        self.assertEqual(r["unique_descriptor_offset_shape_join"],0)
    def test_wrong_descriptor(self):
        r=b.member_join(expected(),metadata(),[slot(binding=4)],"direct")
        self.assertEqual(r["unique_descriptor_offset_shape_join"],0)
    def test_packed_not_direct(self):
        m=metadata(index=0x103)
        self.assertEqual(b.member_join(expected(),m,[slot()],"direct")["unique_descriptor_offset_shape_join"],0)
        self.assertEqual(b.member_join(expected(),m,[slot()],"low8")["unique_descriptor_offset_shape_join"],1)
    def test_same_binding_multiple_sets_ambiguous(self):
        r=b.member_join(expected(),metadata(),[slot(),slot(set_id=1)],"direct")
        self.assertEqual((r["unique_descriptor_offset_shape_join"],r["ambiguous_join"]),(0,1))
    def test_noninjective(self):
        m=metadata();m["groups"]["Generated"]["members"]["y"]=16
        r=b.member_join(expected()+expected("y"),m,[slot()],"direct")
        self.assertEqual((r["unique_descriptor_offset_shape_join"],r["non_injective_join"]),(0,2))
    def test_unbound_name_not_proof(self):
        m=metadata();m["buffers"]={}
        r=b.member_join(expected(),m,[slot()],"direct")
        self.assertEqual((r["serialized_name_present"],r["unique_descriptor_offset_shape_join"]),(1,0))
    def test_debug_counts(self):
        words=[0x07230203,0x00010000,0,8,0,(3<<16)|5,1,0,(4<<16)|6,2,0,0]
        self.assertEqual(b.debug_op_counts(struct.pack("<"+"I"*len(words),*words)),{"op_name":1,"op_member_name":1})
    def test_descriptor_collision(self):
        ref={"separate_images":[{"set":0,"binding":1,"type":"texture2D"}],
             "separate_samplers":[{"set":0,"binding":1,"type":"sampler"}]}
        with self.assertRaisesRegex(ValueError,"duplicate_descriptor_coordinate"):b.reflected_slots(ref)
    def test_texture_and_sampler_distinct(self):
        named=[{"kind":"t","source_texture_name":"Tex"},{"kind":"s","source_texture_name":"Tex"}]
        sr={"separate_images":[{"name":"Tex","type":"texture2D"}],"separate_samplers":[{"name":"samplerTex","type":"sampler"}]}
        m={"textures":{"Tex":(2,3)}}
        slots=[{"kind":"separate_images","set":0,"binding":2,"type":"texture2D","array":()},
               {"kind":"separate_samplers","set":0,"binding":3,"type":"sampler","array":()}]
        self.assertEqual(b.resource_join(named,sr,m,slots,"direct")["unique_descriptor_type_join"],2)
        m["textures"]["Tex"]=(3,2)
        self.assertEqual(b.resource_join(named,sr,m,slots,"direct")["unique_descriptor_type_join"],0)

if __name__=="__main__":unittest.main()
