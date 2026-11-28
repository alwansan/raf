import struct
import unittest
from tools.gt_skybox_binding_calibration import probe as p
def ins(op,*a):return [(1+len(a))*65536+op,*a]
def module(a):
    words=[0x07230203,0x10000,0,64,0]+a
    return struct.pack("<"+"I"*len(words),*words)
def slot(kind,b,typ):
    return {"kind":kind,"set":0,"binding":b,"type":typ,"array":()}
class Control(unittest.TestCase):
    def test_sources_differ(self):
        a,b=map(p.shader,p.CASES)
        self.assertNotEqual(a,b)
        self.assertIn("packoffset(c2)",b)
        self.assertIn("register(b4)",b)
    def test_sample_pair(self):
        code=ins(71,1,33,2)+ins(71,1,34,0)+ins(71,2,33,3)+ins(71,2,34,0)+ins(59,10,1,0)+ins(59,11,2,0)+ins(61,12,3,1)+ins(61,13,4,2)+ins(86,14,5,3,4)+ins(87,15,6,5,7)
        self.assertEqual(p.sampled_pairs(module(code)),{((0,2),(0,3))})
    def test_sample_pair_missing(self):
        with self.assertRaises(ValueError):p.sampled_pairs(module(ins(87,15,6,5,7)))
    def test_pair_swap(self):
        known={"A":"texture2D","B":"textureCube"}
        meta={"textures":{"A":(2,4),"B":(3,5)}}
        slots=[slot("separate_images",2,"texture2D"),slot("separate_images",3,"textureCube"),
               slot("separate_samplers",4,"sampler"),slot("separate_samplers",5,"sampler")]
        pairs={((0,2),(0,4)),((0,3),(0,5))}
        self.assertTrue(p.pair_profile(known,meta,slots,pairs,"direct")["all_sample_pairs_accounted"])
        meta["textures"]={"A":(2,5),"B":(3,4)}
        self.assertEqual(p.pair_profile(known,meta,slots,pairs,"direct")["independently_used_sample_pairs"],0)
    def test_packed_pair(self):
        meta={"textures":{"A":(258,259)}}
        slots=[slot("separate_images",2,"texture2D"),slot("separate_samplers",3,"sampler")]
        pairs={((0,2),(0,3))}
        self.assertFalse(p.pair_profile({"A":"texture2D"},meta,slots,pairs,"direct")["all_sample_pairs_accounted"])
        self.assertTrue(p.pair_profile({"A":"texture2D"},meta,slots,pairs,"low8")["all_sample_pairs_accounted"])
    def test_numeric_shape(self):
        meta={"groups":{"C":{"members":{"a":16}}},"buffers":{"C":258}}
        u={"kind":"ubos","set":0,"binding":2,"members":[{"offset":16,"type":"vec4"}]}
        self.assertEqual(p.numeric_profile({"a":"vec4"},meta,[u],"low8")["unique_descriptor_offset_type"],1)
        self.assertEqual(p.numeric_profile({"a":"float"},meta,[u],"low8")["unique_descriptor_offset_type"],0)
    def test_numeric_wrong_offset(self):
        meta={"groups":{"C":{"members":{"a":20}}},"buffers":{"C":2}}
        u={"kind":"ubos","set":0,"binding":2,"members":[{"offset":16,"type":"vec4"}]}
        self.assertEqual(p.numeric_profile({"a":"vec4"},meta,[u],"direct")["unique_descriptor_offset_type"],0)
    def test_numeric_duplicate(self):
        meta={"groups":{"C":{"members":{"a":16,"b":16}}},"buffers":{"C":2}}
        u={"kind":"ubos","set":0,"binding":2,"members":[{"offset":16,"type":"vec4"}]}
        self.assertEqual(p.numeric_profile({"a":"vec4","b":"vec4"},meta,[u],"direct")["non_injective"],2)
if __name__=="__main__":unittest.main()
