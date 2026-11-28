import copy
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from tools.gt_ambient_same_export import audit as a, stage_trace

GUID="ab"*16
INSTANCE="cd"*16
def tr(rows,**extra):return {"schema_version":1,"export_instance":INSTANCE,"objects":rows,**extra}
def row(owner,i,cid,fid):
    return {"source":{"owner":owner,"path_id":i},"class_id":cid,"exportable":True,"export":{"guid":GUID,"file_id":fid,"type":2}}
def fields():
    d={k:{"r":.1,"g":.2,"b":.3,"a":1.} for k in a.COLORS}
    d.update({k:.5 for k in a.NUMBERS})
    d.update({k:min(v) for k,v in a.ENUMS.items()})
    d.update({k:1 for k in a.INTS});d["m_Fog"]=True
    return d
class TestAmbient(unittest.TestCase):
    def setUp(self):
        self.s=tr([row("level24",-10,104,52)],nonexportable_render_settings_skipped=0)
        self.w=tr([row("sharedassets24.assets",11,21,2100000)])
        self.b=tr([])
    def test_all_fields_equal(self):
        x=fields(); r=a.field_report(x,copy.deepcopy(x))
        self.assertEqual(r["fields_equal"],len(a.FIELDS));self.assertFalse(r["field_unknown"]);self.assertFalse(r["field_mismatches"])
    def test_drift_fields(self):
        x=fields();y=copy.deepcopy(x)
        y["m_AmbientMode"]=3;y["m_AmbientSkyColor"]["r"]=.75;y["m_Fog"]=False;y["m_ReflectionIntensity"]=.8
        self.assertEqual(set(a.field_report(x,y)["field_mismatches"]),{"m_AmbientMode","m_AmbientSkyColor","m_Fog","m_ReflectionIntensity"})
    def test_missing_schema_not_pass(self):
        x=fields();y=copy.deepcopy(x);del y["m_AmbientIntensity"];x["m_FogMode"]="bad"
        r=a.field_report(x,y)
        self.assertEqual(r["field_unknown"],{"m_AmbientIntensity":"export_field_missing","m_FogMode":"source_schema_unknown"})
    def test_signed_settings_identity(self):
        self.assertEqual(a.settings_mapping(self.s,self.w,self.b,-10),(GUID,52,2))
    def test_wrong_instance(self):
        self.b["export_instance"]="ee"*16
        with self.assertRaisesRegex(a.Rejected,"different_export_instance"):a.settings_mapping(self.s,self.w,self.b,-10)
    def test_wrong_settings_owner(self):
        self.s["objects"][0]["source"]["owner"]="level38"
        with self.assertRaisesRegex(a.Rejected,"settings_trace_identity"):a.settings_mapping(self.s,self.w,self.b,-10)
    def test_nonexportable_settings(self):
        self.s["nonexportable_render_settings_skipped"]=1
        with self.assertRaisesRegex(a.Rejected,"settings_nonexportable"):a.settings_mapping(self.s,self.w,self.b,-10)
    def test_typed_material_trace(self):
        self.assertEqual(a.material_mapping(self.w,"sharedassets24.assets",11),(GUID,2100000,2))
    def test_collapsed_material_trace(self):
        self.w["objects"].append(row("sharedassets25.assets",12,21,2100000))
        with self.assertRaisesRegex(a.Rejected,"collapsed"):a.material_mapping(self.w,"sharedassets24.assets",11)
    def test_missing_material_trace(self):
        with self.assertRaisesRegex(a.Rejected,"missing_or_duplicate"):a.material_mapping(self.w,"sharedassets25.assets",11)
    def test_null_sun_control(self):
        s={"m_Sun":{"m_FileID":0,"m_PathID":0}}
        self.assertEqual(a.null_sun(s,{"m_Sun":{"fileID":0}})["status"],"MATCH_NULL")
        self.assertEqual(a.null_sun(s,{"m_Sun":{"fileID":22}})["status"],"DRIFT_NULL_TO_NON_NULL")
        self.assertEqual(a.null_sun({"m_Sun":{"m_FileID":1,"m_PathID":22}},{"m_Sun":{"fileID":0}})["status"],"UNKNOWN")
    def test_skybox_null_and_nonnull(self):
        s={"m_SkyboxMaterial":{"m_FileID":0,"m_PathID":0}}
        try:import UnityPy
        except ImportError:self.skipTest("UnityPy not installed")
        self.assertEqual(a.skybox_binding(None,None,s,{"m_SkyboxMaterial":{"fileID":0}},self.w)["status"],"MATCH_NULL")
        self.assertEqual(a.skybox_binding(None,None,s,{"m_SkyboxMaterial":{"fileID":23}},self.w)["status"],"DRIFT_NULL_TO_NON_NULL")
    def test_guid_and_class_actual_yaml(self):
        with TemporaryDirectory() as d:
            root=Path(d);(root/"Assets").mkdir();p=root/"Assets/a.unity"
            p.write_text("%YAML 1.1\n--- !u!104 &52\nRenderSettings:\n  m_Fog: 1\n")
            Path(str(p)+".meta").write_text("guid: "+GUID+"\n")
            self.assertEqual(a.doc_body(a.file_for_guid(root,GUID,{".unity"}),104,52,"RenderSettings"),{"m_Fog":1})
            with self.assertRaisesRegex(a.Rejected,"wrong_class"):a.doc_body(p,21,52,"Material")
            p.write_text("%YAML 1.1\n--- !u!104 &52\nRenderSettings:\n  m_Fog: 1\n  m_Fog: 0\n")
            with self.assertRaisesRegex(a.Rejected,"duplicate_yaml"):a.doc_body(p,104,52,"RenderSettings")
    def test_stage_preserves_existing_captures(self):
        p=Path("android-port/Experiments/ExportLineage/RaftExportLineage.cs")
        b=p.read_bytes();s=stage_trace.render(b).decode()
        self.assertIn('asset.ClassID != 104 || asset.Collection.Name != "level24"',s)
        self.assertIn("RAFT_PRIVATE_EXPORT_AMBIENT_LINEAGE",s)
        self.assertIn("nonexportable_render_settings_skipped",s)
        self.assertEqual(s.count('json.WriteString("export_instance", exportInstance);'),3)
        with self.assertRaises(ValueError):stage_trace.render(b+b"\n//changed")
