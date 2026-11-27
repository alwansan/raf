"""V7 native sampler parity on the same V6 stream and native YAML routes."""
from copy import deepcopy
import unittest

import test_gt_streamed_texture_route_payload as sf
from scripts import gt_renderer_submesh_routes as routes
from scripts import gt_native_texture_route_sampler as sampler
from scripts import gt_streamed_texture_route_payload as stream


class SamplerRoutes(unittest.TestCase):
    def setUp(self):
        self.s=sf.StreamRoutes("test_same_route_two_streams")
        self.s.setUp();self.addCleanup(self.s.doCleanups)
        self.f=self.s.f
        self.source_maps={}
        for i,(src,dst) in enumerate(zip(self.s.v.source,self.s.v.actual,strict=True)):
            settings=dict(m_FilterMode=1+i,m_Aniso=2+6*i,m_MipBias=-.625 if i==0 else .375,
                          m_WrapU=i,m_WrapV=2-i,m_WrapW=3-i)
            src["m_TextureSettings"]=deepcopy(settings)
            dst["m_TextureSettings"]={"serializedVersion":2,**deepcopy(settings)}
        self.source=self.s.v.source[0]["m_TextureSettings"]
        self.actual=self.s.v.actual[0]["m_TextureSettings"]

    def check(self,strict=True,omit_source=False,omit_export=False):
        objects,proofs=self.s.v.k.v.b.evidence()
        resolved=stream.resolve_requests(self.s.root,self.s.pins,self.s.requests())
        objects.update((key,(28,p)) for key,p in resolved.items())
        source={(self.f.owner,n+20):sampler.safe_proof(t)
                for n,t in zip((5,6),self.s.v.source,strict=True)}
        self.f.write()
        mapping={(r["source"]["owner"],r["source"]["path_id"]):
                 (r["class_id"],routes.trace_pointer(r["export"]),r["exportable"])
                 for r in self.f.mappings}
        actual={}
        files,docs=routes.actual_index(self.f.project,mapping,texture_payloads=True,samplers=actual)
        if omit_source:source={}
        if omit_export:actual={}
        return routes.compare(objects,{self.f.owner:[]},mapping,files,docs,vertex_payloads=proofs,
            material_values=True,material_keywords=True,texture_payloads=True,streamed_textures=True,
            **(dict(source_samplers=source,export_samplers=actual) if strict else {}))

    def reject(self,reason,**kwargs):
        self.assertTrue(self.check(False)["selected_same_route_streamed_texture_payloads_verified"])
        r=self.check(**kwargs)
        self.assertFalse(r["selected_renderer_routes_preserved"],r)
        self.assertFalse(r["selected_same_route_native_texture_sampler_verified"])
        self.assertIn(reason,r["reason_counts"])

    def test_native_same_route_sampler(self):
        r=self.check()
        self.assertEqual(r["schema_version"],7)
        self.assertTrue(r["selected_same_route_native_texture_sampler_verified"],r)
        self.assertEqual(r["counts"]["native_texture_sampler_slots_matched"],2)
        self.assertEqual(r["counts"]["native_texture_sampler_fields_matched_per_route"],12)
        self.assertEqual(r["counts"]["complete_native_sampler_bound_renderer_routes"],1)
        self.assertEqual(r["counts"]["complete_native_sampler_bound_submesh_routes"],2)
        self.assertFalse(r["texture_sampler_import_colorspace_or_GPU_verified"])

    def test_V6_sampler_blind(self):
        self.actual["m_WrapU"]=3
        r=self.check(False)
        self.assertEqual(r["schema_version"],6)
        self.assertTrue(r["selected_same_route_streamed_texture_payloads_verified"])
        self.assertFalse(r["selected_same_route_native_texture_sampler_verified"])

    def test_filter(self):
        self.actual["m_FilterMode"]=0
        self.reject("same_route_texture_sampler_FilterMode_drift")

    def test_aniso(self):
        self.actual["m_Aniso"]=16
        self.reject("same_route_texture_sampler_Aniso_drift")

    def test_mip_bias(self):
        self.actual["m_MipBias"]=.625
        self.reject("same_route_texture_sampler_MipBias_drift")

    def test_wrap_u(self):
        self.actual["m_WrapU"]=3
        self.reject("same_route_texture_sampler_WrapU_drift")

    def test_wrap_v(self):
        self.actual["m_WrapV"]=0
        self.reject("same_route_texture_sampler_WrapV_drift")

    def test_wrap_w(self):
        self.actual["m_WrapW"]=0
        self.reject("same_route_texture_sampler_WrapW_drift")

    def test_missing_sampler(self):
        del self.s.v.actual[0]["m_TextureSettings"]
        self.reject("missing_native_texture_sampler")

    def test_missing_source_field(self):
        del self.source["m_MipBias"]
        self.reject("missing_native_texture_sampler_field")

    def test_legacy_single_wrap(self):
        self.actual["m_WrapMode"]=self.actual.pop("m_WrapU")
        self.reject("missing_native_texture_sampler_field")

    def test_ambiguous_legacy_extra_wrap(self):
        self.actual["m_WrapMode"]=0
        self.reject("unsupported_native_texture_sampler_schema")

    def test_unknown_version(self):
        self.actual["serializedVersion"]=1
        self.reject("unsupported_native_texture_sampler_schema")

    def test_invalid_filter_enum(self):
        self.actual["m_FilterMode"]=3
        self.reject("invalid_native_texture_sampler_value")

    def test_invalid_aniso(self):
        self.actual["m_Aniso"]=17
        self.reject("invalid_native_texture_sampler_value")

    def test_invalid_wrap(self):
        self.actual["m_WrapU"]=-1
        self.reject("invalid_native_texture_sampler_value")

    def test_bool_not_enum(self):
        self.actual["m_FilterMode"]=True
        self.reject("invalid_native_texture_sampler_value")

    def test_nonfinite_bias(self):
        self.actual["m_MipBias"]=float("nan")
        self.reject("invalid_native_texture_sampler_value")

    def test_overflow_bias(self):
        self.actual["m_MipBias"]=1e100
        self.reject("invalid_native_texture_sampler_value")

    def test_unset_importer_bias_not_native(self):
        self.actual["m_MipBias"]=-100
        self.reject("invalid_native_texture_sampler_value")

    def test_signed_zero_preserved(self):
        self.source["m_MipBias"]=-0.0;self.actual["m_MipBias"]=-0.0
        self.assertTrue(self.check()["selected_same_route_native_texture_sampler_verified"])
        self.actual["m_MipBias"]=0.0
        self.reject("same_route_texture_sampler_MipBias_drift")

    def test_native_yaml_integer_spelling_negative_zero(self):
        t=routes.yaml_tree("Texture2D:\n  m_TextureSettings:\n    m_MipBias: -0\n",28)
        self.assertEqual(sampler._float_bits(t["m_TextureSettings"]["m_MipBias"]),0x80000000)

    def test_float32_roundtrip_equivalent(self):
        self.source["m_MipBias"]=0.125
        self.actual["m_MipBias"]=0.12500000001
        self.assertTrue(self.check()["selected_same_route_native_texture_sampler_verified"])

    def test_missing_source_sampler_map_entries(self):
        self.reject("missing_source_texture_sampler_proof",omit_source=True)

    def test_missing_export_sampler_map_entries(self):
        self.reject("missing_export_texture_sampler_proof",omit_export=True)

    def test_requires_V6_and_both_maps(self):
        with self.assertRaisesRegex(routes.Unknown,"native_sampler_gate_requires_both_maps_and_V6"):
            routes.compare({}, {}, {}, {}, {}, source_samplers={},export_samplers={})

    def test_payload_drift_not_hidden_by_sampler(self):
        self.s.v.change_byte(3)
        r=self.check()
        self.assertFalse(r["selected_same_route_native_texture_sampler_verified"])
        self.assertIn("same_route_texture_payload_bytes_drift",r["reason_counts"])

    def test_null_only_does_not_claim_sampler(self):
        import test_gt_renderer_submesh_routes as rf
        for n in (5,6):
            src=self.f.objects[(self.f.owner,n)][1]["m_SavedProperties"]["m_TexEnvs"][0][1]
            dst=self.f.docs[(rf.guid(n),2100000)][1]["m_SavedProperties"]["m_TexEnvs"][0]["_MainTex"]
            src["m_Texture"]=rf.src(0);dst["m_Texture"]=rf.loc(0)
        r=self.check()
        self.assertTrue(r["selected_renderer_routes_preserved"],r)
        self.assertFalse(r["selected_same_route_native_texture_sampler_verified"])
        self.assertEqual(r["counts"].get("native_texture_sampler_slots_matched",0),0)


if __name__=="__main__":
    unittest.main()
