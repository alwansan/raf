import unittest
from tools.gt_top_resource_closure import selected_merged_abi as m

class MergedABITests(unittest.TestCase):
    def fixture(self):
        member=dict(name="_Other",index=16,type=0,columns=4,matrix=False,array_size=0)
        return dict(role="fs",members=[dict(member=member,original_block="Camera",merged_block="Camera",category="external")],
                    resources=[dict(name="_Outside",source_name="_Outside",kind="t",external=True)])
    def test_reflection_exact_and_missing(self):
        s=self.fixture()
        data=dict(ubos=[dict(name="Camera",type="_1")],types={"_1":{"members":[dict(name="_Other",offset=16,type="vec4")]}},
                  separate_images=[dict(name="_Outside")])
        good=m.reflection_counts(s,data)
        self.assertEqual(good["external_exact_block_offset_type"],1)
        self.assertEqual(good["external_t_resource_reflected"],1)
        data["types"]["_1"]["members"][0]["offset"]=20
        self.assertEqual(m.reflection_counts(s,data)["offset_mismatch"],1)
        data["types"]["_1"]["members"][0]["type"]="vec3"
        self.assertEqual(m.reflection_counts(s,data)["type_or_stride_mismatch"],1)
        missing=m.reflection_counts(s,{})
        self.assertEqual(missing["external_absent"],1)
        self.assertEqual(missing["external_t_resource_missing"],1)
    def test_promotion_and_ambiguous_not_exact(self):
        s=self.fixture()
        row=dict(name="_Other",offset=16,type="vec4")
        data=dict(ubos=[dict(name="$Global",type="_1")],types={"_1":{"members":[row]}})
        self.assertEqual(m.reflection_counts(s,data)["block_relocated"],1)
        data["ubos"].append(dict(name="Camera",type="_1"))
        self.assertEqual(m.reflection_counts(s,data)["ambiguous"],1)
    def test_wrapper_offsets_and_loose_uniform(self):
        code="cbuffer Camera {\nfloat4 _Other : packoffset(c1.x);\n};\nfloat _Loose;\nTexture2D<float4> _Outside;\n"
        cb,res,loose=m.collect_wrapper(code)
        self.assertEqual(cb["Camera"]["_Other"],("float4","",16))
        self.assertEqual(res["_Outside"],"Texture2D<float4>")
        self.assertEqual(loose["_Loose"],("float",""))
        with self.assertRaises(ValueError):m.collect_wrapper(code+code)
    def test_matrix_stride_and_array_not_equivalent(self):
        s=self.fixture()
        s["members"][0]["member"].update(matrix=True,array_size=2)
        e=dict(name="_Other",offset=16,type="mat4",matrix_stride=16,array=[2],array_stride=64)
        data=dict(ubos=[dict(name="Camera",type="_1")],types={"_1":{"members":[e]}})
        self.assertEqual(m.reflection_counts(s,data)["exact_block_offset_type"],1)
        e["array_stride"]=32
        self.assertEqual(m.reflection_counts(s,data)["type_or_stride_mismatch"],1)

if __name__=="__main__":unittest.main()
