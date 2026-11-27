"""Authored independent per-material and complete V3 route controls."""
from copy import deepcopy
import struct
import unittest

import test_gt_mesh_vertex_payload as byte_fixture
import test_gt_renderer_submesh_routes as route_fixture
from scripts import gt_material_route_values as values
from scripts import gt_renderer_submesh_routes as routes


class MaterialValueRoutes(unittest.TestCase):
    def setUp(self):
        self.b=byte_fixture.ByteRoutes("test_inline_exact_same_route")
        self.b.setUp()
        self.addCleanup(self.b.doCleanups)
        self.f=self.b.f
        self.source=[]
        self.actual=[]
        for n in (5,6):
            s=self.f.objects[(self.f.owner,n)][1]["m_SavedProperties"]
            a=self.f.docs[(route_fixture.guid(n),2100000)][1]["m_SavedProperties"]
            rgba={"r":.125*n,"g":-0.0,"b":2.25,"a":.5}
            s.update(m_Colors=[["_Tint",deepcopy(rgba)]],
                     m_Floats=[["_Value",.1],["_Other",-2.5]],
                     m_Ints=[["_ExactInt",16777217+n]])
            a.update(m_Colors=[{"_Tint":deepcopy(rgba)}],
                     m_Floats=[{"_Value":.10000000149011612},{"_Other":-2.5}],
                     m_Ints=[{"_ExactInt":16777217+n}])
            self.source.append(s);self.actual.append(a)

    def check(self,strict=True):
        objects,proofs=self.b.evidence()
        self.f.write()
        mapping={(r["source"]["owner"],r["source"]["path_id"]):
                 (r["class_id"],routes.trace_pointer(r["export"]),r["exportable"])
                 for r in self.f.mappings}
        files,docs=routes.actual_index(self.f.project,mapping)
        return routes.compare(objects,{self.f.owner:[]},mapping,files,docs,
                              vertex_payloads=proofs,material_values=strict)

    def rejected(self,reason,old_pass=True):
        if old_pass:
            self.assertTrue(self.check(False)["selected_same_route_vertex_and_UV_bytes_verified"])
        result=self.check()
        self.assertFalse(result["selected_renderer_routes_preserved"],result)
        self.assertFalse(result["selected_same_route_material_values_verified"])
        self.assertFalse(result["counts"].get("complete_material_value_bound_renderer_routes",0))
        self.assertIn(reason,result["reason_counts"])
        self.assertNotIn("_Tint",str(result))
        self.assertNotIn("_ExactInt",str(result))

    def test_exact_values_and_vertex_same_route(self):
        r=self.check()
        self.assertTrue(r["selected_same_route_material_values_verified"],r)
        self.assertEqual(r["schema_version"],3)
        self.assertEqual(r["counts"]["complete_material_value_bound_submesh_routes"],2)
        self.assertEqual(r["counts"]["material_color_slots_matched"],2)
        self.assertEqual(r["counts"]["material_float_slots_matched"],4)
        self.assertEqual(r["counts"]["material_int_slots_matched"],2)
        self.assertFalse(r["shader_program_color_scalar_or_GPU_parity_verified"])

    def test_v2_does_not_claim_value_proof(self):
        r=self.check(False)
        self.assertEqual(r["schema_version"],2)
        self.assertFalse(r["selected_same_route_material_values_verified"])

    def test_color_RGB_drift(self):
        self.actual[0]["m_Colors"][0]["_Tint"]["r"]=1
        self.rejected("material_color_value_drift")

    def test_color_alpha_drift(self):
        self.actual[0]["m_Colors"][0]["_Tint"]["a"]=0
        self.rejected("material_color_value_drift")

    def test_float_one_ULP_drift(self):
        original=struct.unpack("<I",struct.pack("<f",.1))[0]
        self.actual[0]["m_Floats"][0]["_Value"]=struct.unpack("<f",struct.pack("<I",original+1))[0]
        self.rejected("material_float_value_drift")

    def test_integer_precision_not_float32(self):
        self.actual[0]["m_Ints"][0]["_ExactInt"]+=1
        self.rejected("material_int_value_drift")

    def test_missing_color(self):
        self.actual[0]["m_Colors"]=[]
        self.rejected("missing_material_color_slot")

    def test_unexpected_color(self):
        self.actual[0]["m_Colors"].append({"_Added":{"r":1,"g":1,"b":1,"a":1}})
        self.rejected("unexpected_material_color_slot")

    def test_missing_float(self):
        self.actual[0]["m_Floats"].pop()
        self.rejected("missing_material_float_slot")

    def test_unexpected_integer(self):
        self.actual[0]["m_Ints"].append({"_Added":1})
        self.rejected("unexpected_material_int_slot")

    def test_integer_migrated_to_float(self):
        pair=self.actual[0]["m_Ints"].pop()
        self.actual[0]["m_Floats"].append(pair)
        self.rejected("unexpected_material_float_slot")

    def test_float_not_integer_type(self):
        self.actual[0]["m_Ints"][0]["_ExactInt"]=float(16777222)
        self.rejected("invalid_material_serialized_value")

    def test_missing_container_not_empty(self):
        del self.actual[0]["m_Ints"]
        self.rejected("missing_material_value_container")

    def test_duplicate_slot(self):
        self.actual[0]["m_Floats"].append({"_Value":.1})
        self.rejected("invalid_material_serialized_value")

    def test_nonfinite_color(self):
        self.actual[0]["m_Colors"][0]["_Tint"]["r"]=float("inf")
        self.rejected("invalid_material_serialized_value")

    def test_bool_float_rejected(self):
        self.actual[0]["m_Floats"][0]["_Value"]=True
        self.rejected("invalid_material_serialized_value")

    def test_signed_zero_drift(self):
        self.actual[0]["m_Colors"][0]["_Tint"]["g"]=0.0
        self.rejected("material_color_value_drift")

    def test_material_values_do_not_hide_vertex_drift(self):
        self.b.f.docs[self.b.target][1]["m_VertexData"]["_typelessdata"]=self.b.other.hex()
        self.rejected("same_route_vertex_or_UV_bytes_drift",old_pass=False)

    def test_material_values_do_not_hide_wrong_shader(self):
        self.f.docs[(route_fixture.guid(5),2100000)][1]["m_Shader"]=route_fixture.ext(4800000,route_fixture.guid(16))
        self.rejected("ordered_pointer_target_mismatch",old_pass=False)

    def test_exported_mapping_form_and_explicit_empty(self):
        self.actual[0]["m_Floats"]={"_Value":.1,"_Other":-2.5}
        self.actual[0]["m_Ints"]={"_ExactInt":16777222}
        self.actual[0]["m_Colors"]={"_Tint":deepcopy(self.source[0]["m_Colors"][0][1])}
        self.assertTrue(self.check()["selected_same_route_material_values_verified"])
        self.source[0]["m_Ints"]=[]
        self.actual[0]["m_Ints"]={}
        self.assertTrue(self.check()["selected_same_route_material_values_verified"])

    def test_literal_yaml_negative_zero_preserved(self):
        tree=routes.yaml_tree("Material:\n  m_SavedProperties:\n    m_Colors:\n      - _Tint: {r: -0, g: 0, b: 1, a: 1}\n    m_Floats:\n      - _F: -0\n    m_Ints: []\n",21)
        normalized=values.normalize(tree,exported=True)
        self.assertEqual(normalized["m_Colors"]["_Tint"][0],0x80000000)
        self.assertEqual(normalized["m_Floats"]["_F"],0x80000000)

    def test_value_gate_requires_vertex_binding(self):
        with self.assertRaisesRegex(routes.Unknown,"material_value_gate_requires_vertex_binding"):
            routes.compare({}, {}, {}, {}, {}, material_values=True)


if __name__=="__main__":
    unittest.main()
