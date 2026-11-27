"""Serialized state V4 regression and V3-pass/V4-reject route controls."""
from copy import deepcopy
import unittest
import test_gt_material_route_values as value_fixture
import test_gt_renderer_submesh_routes as route_fixture
from scripts import gt_renderer_submesh_routes as routes
from scripts import gt_material_route_keyword_state as state


class KeywordPassRoutes(unittest.TestCase):
    def setUp(self):
        self.v=value_fixture.MaterialValueRoutes("test_exact_values_and_vertex_same_route")
        self.v.setUp()
        self.addCleanup(self.v.doCleanups)
        self.f=self.v.f
        self.source=[];self.actual=[]
        for n in (5,6):
            s=self.f.objects[(self.f.owner,n)][1]
            a=self.f.docs[(route_fixture.guid(n),2100000)][1]
            fields=dict(m_ValidKeywords=["AUTHORED_SHARED","AUTHORED_MODE_"+str(n)],
                        m_InvalidKeywords=["AUTHORED_INVALID_"+str(n)],
                        disabledShaderPasses=["AuthoredDepth"+str(n)])
            s.update(deepcopy(fields));a.update(deepcopy(fields))
            self.source.append(s);self.actual.append(a)

    def check(self,strict=True):
        objects,proofs=self.v.b.evidence()
        self.f.write()
        mapping={(r["source"]["owner"],r["source"]["path_id"]):
                 (r["class_id"],routes.trace_pointer(r["export"]),r["exportable"])
                 for r in self.f.mappings}
        files,docs=routes.actual_index(self.f.project,mapping)
        return routes.compare(objects,{self.f.owner:[]},mapping,files,docs,
                              vertex_payloads=proofs,material_values=True,material_keywords=strict)

    def reject(self,reason,old_pass=True):
        if old_pass:
            self.assertTrue(self.check(False)["selected_same_route_material_values_verified"])
        r=self.check()
        self.assertFalse(r["selected_renderer_routes_preserved"],r)
        self.assertFalse(r["selected_same_route_material_keyword_pass_state_verified"])
        self.assertFalse(r["counts"].get("complete_material_keyword_bound_renderer_routes",0))
        self.assertIn(reason,r["reason_counts"])
        self.assertNotIn("AUTHORED_SHARED",str(r))

    def test_all_state_bound(self):
        r=self.check()
        self.assertEqual(r["schema_version"],4)
        self.assertTrue(r["selected_same_route_material_keyword_pass_state_verified"],r)
        self.assertEqual(r["counts"]["complete_material_keyword_bound_submesh_routes"],2)
        self.assertEqual(r["counts"]["material_valid_keyword_entries_matched"],4)
        self.assertEqual(r["counts"]["material_invalid_keyword_entries_matched"],2)
        self.assertEqual(r["counts"]["material_disabled_pass_entries_matched"],2)
        self.assertFalse(r["active_shader_variant_or_runtime_keyword_scope_verified"])

    def test_v3_does_not_claim_state(self):
        r=self.check(False)
        self.assertEqual(r["schema_version"],3)
        self.assertFalse(r["selected_same_route_material_keyword_pass_state_verified"])

    def test_order_of_set_does_not_matter(self):
        self.actual[0]["m_ValidKeywords"].reverse()
        self.assertTrue(self.check()["selected_same_route_material_keyword_pass_state_verified"])

    def test_explicit_empty_arrays(self):
        for k in state.FIELDS:self.source[0][k]=[];self.actual[0][k]=[]
        self.assertTrue(self.check()["selected_same_route_material_keyword_pass_state_verified"])

    def test_bucket_swap(self):
        self.actual[0]["m_ValidKeywords"][1],self.actual[0]["m_InvalidKeywords"][0]=self.actual[0]["m_InvalidKeywords"][0],self.actual[0]["m_ValidKeywords"][1]
        self.reject("material_keyword_bucket_drift")

    def test_valid_removed(self):
        self.actual[0]["m_ValidKeywords"].pop()
        self.reject("missing_material_valid_keyword")

    def test_valid_added(self):
        self.actual[0]["m_ValidKeywords"].append("AUTHORED_ADDED")
        self.reject("unexpected_material_valid_keyword")

    def test_invalid_removed(self):
        self.actual[0]["m_InvalidKeywords"].clear()
        self.reject("missing_material_invalid_keyword")

    def test_invalid_added(self):
        self.actual[0]["m_InvalidKeywords"].append("AUTHORED_ADDED")
        self.reject("unexpected_material_invalid_keyword")

    def test_pass_removed(self):
        self.actual[0]["disabledShaderPasses"].clear()
        self.reject("missing_material_disabled_pass")

    def test_pass_added(self):
        self.actual[0]["disabledShaderPasses"].append("AuthoredOther")
        self.reject("unexpected_material_disabled_pass")

    def test_case_sensitive(self):
        self.actual[0]["disabledShaderPasses"][0]="authoreddepth5"
        self.reject("missing_material_disabled_pass")

    def test_missing_field(self):
        del self.actual[0]["m_InvalidKeywords"]
        self.reject("missing_material_keyword_pass_container")

    def test_missing_source_field(self):
        del self.source[0]["m_ValidKeywords"]
        self.reject("missing_material_keyword_pass_container")

    def test_legacy_nonempty_not_a_modern_lane(self):
        self.actual[0]["m_ShaderKeywords"]="AUTHORED_SHARED"
        self.reject("unsupported_legacy_material_keyword_state")

    def test_legacy_only_missing_modern(self):
        for k in state.FIELDS:del self.actual[0][k]
        self.actual[0]["m_ShaderKeywords"]="AUTHORED_SHARED"
        self.reject("missing_material_keyword_pass_container")

    def test_duplicate_keyword(self):
        self.actual[0]["m_ValidKeywords"].append("AUTHORED_SHARED")
        self.reject("invalid_material_keyword_set")

    def test_duplicate_pass(self):
        self.actual[0]["disabledShaderPasses"]*=2
        self.reject("invalid_material_disabled_pass_set")

    def test_overlap_buckets(self):
        self.actual[0]["m_InvalidKeywords"].append("AUTHORED_SHARED")
        self.reject("overlapping_material_keyword_buckets")

    def test_private_selector(self):
        self.actual[0]["m_ValidKeywords"].append("GT_ORIGINAL_921_AUTHORED")
        self.reject("invalid_material_keyword_set")

    def test_invalid_keyword_type(self):
        self.actual[0]["m_InvalidKeywords"]=[True]
        self.reject("invalid_material_keyword_set")

    def test_invalid_pass_name(self):
        self.actual[0]["disabledShaderPasses"]=["bad name"]
        self.reject("invalid_material_disabled_pass_set")

    def test_null_not_explicit_empty(self):
        self.actual[0]["m_InvalidKeywords"]=None
        self.reject("invalid_material_keyword_pass_container")

    def test_state_does_not_hide_value_drift(self):
        self.v.actual[0]["m_Colors"][0]["_Tint"]["a"]=0
        self.reject("material_color_value_drift",old_pass=False)

    def test_requires_value_binding(self):
        with self.assertRaisesRegex(routes.Unknown,"material_keyword_gate_requires_value_binding"):
            routes.compare({}, {}, {}, {}, {}, material_keywords=True)


if __name__=="__main__":
    unittest.main()
