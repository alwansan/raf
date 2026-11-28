import copy
import unittest
from pathlib import Path
from tools.gt_light_same_export import audit as a, stage_trace

GUID="ab"*16
INSTANCE="cd"*16
def row(i,cid,fid):
    return {"class_id":cid,"source":{"owner":"level38","path_id":i},"export":{"guid":GUID,"file_id":fid,"type":2}}
def trace(rows):
    return {"schema_version":1,"export_instance":INSTANCE,"objects":rows}
def p(i):return {"fileID":i}
def v(keys,values):return dict(zip(keys,values))
TRS={"m_LocalPosition":(1.,2.,3.),"m_LocalRotation":(0.,0.,0.,1.),"m_LocalScale":(1.,1.,1.)}
class TestSameExport(unittest.TestCase):
    def setUp(self):
        self.model={-1:{"class":108,"owner":2,"fields":{"m_Enabled":True,"m_Type":1,"m_Color":(1.,.5,.25,1.),"m_Intensity":2.,"m_Range":5.}},
                    2:{"class":1,"active":True,"components":[3,-1]},
                    3:{"class":4,"owner":2,"parent":4,"children":[5],"trs":TRS},
                    4:{"class":4,"parent":None,"children":[3],"trs":TRS},
                    5:{"class":224,"parent":3}}
        self.rows=[row(i,s["class"],101+n) for n,(i,s) in enumerate(self.model.items())]
        self.w=trace([{"class_id":21}]); self.b=trace([])
        self.m=a.trace_map(self.model,trace(self.rows),self.w,self.b)
        self.docs={101:(108,{"m_GameObject":p(102),"m_Enabled":1,"m_Type":1,"m_Color":v(("r","g","b","a"),(1.,.5,.25,1.)),"m_Intensity":2.,"m_Range":5.}),
            102:(1,{"m_IsActive":1,"m_Component":[{"component":p(103)},{"component":p(101)}]}),
            103:(4,{"m_GameObject":p(102),"m_Father":p(104),"m_Children":[p(105)],**{k:v(a.FIELDS[k],x) for k,x in TRS.items()}}),
            104:(4,{"m_Father":p(0),"m_Children":[p(103)],**{k:v(a.FIELDS[k],x) for k,x in TRS.items()}}),
            105:(224,{"m_Father":p(103)})}
    def test_positive_and_signed_source(self):
        r=a.compare(self.model,self.m,self.docs)
        self.assertTrue(r["same_export_hierarchy_parity"])
        self.assertEqual(r["adjacent_child_transforms"],1)
    def test_different_instance(self):
        bad=trace([]);bad["export_instance"]="ef"*16
        with self.assertRaisesRegex(a.Rejected,"different_export_instance"):a.trace_map(self.model,trace(self.rows),self.w,bad)
    def test_collapsed_pointer(self):
        rows=copy.deepcopy(self.rows); rows[-1]["export"]=rows[0]["export"]
        with self.assertRaisesRegex(a.Rejected,"duplicate_or_collapsed"):a.trace_map(self.model,trace(rows),self.w,self.b)
    def test_missing_transform(self):
        with self.assertRaisesRegex(a.Rejected,"missing_selected_source_trace"):a.trace_map(self.model,trace(self.rows[:-1]),self.w,self.b)
    def test_wrong_trace_class(self):
        rows=copy.deepcopy(self.rows);rows[-1]["class_id"]=4
        with self.assertRaisesRegex(a.Rejected,"trace_class_mismatch"):a.trace_map(self.model,trace(rows),self.w,self.b)
    def test_wrong_source_collection(self):
        rows=copy.deepcopy(self.rows);rows[-1]["source"]["owner"]="level37"
        with self.assertRaisesRegex(a.Rejected,"invalid_trace_identity"):a.trace_map(self.model,trace(rows),self.w,self.b)
    def test_zero_guid(self):
        rows=copy.deepcopy(self.rows);rows[0]["export"]["guid"]="0"*32
        with self.assertRaisesRegex(a.Rejected,"invalid_trace_pointer"):a.trace_map(self.model,trace(rows),self.w,self.b)
    def test_wrong_owner(self):
        self.docs[101][1]["m_GameObject"]=p(104)
        self.assertEqual(a.compare(self.model,self.m,self.docs)["mismatches"],{"component_owner":1})
    def test_active_and_enabled_drift(self):
        self.docs[102][1]["m_IsActive"]=0;self.docs[101][1]["m_Enabled"]=0
        self.assertEqual(a.compare(self.model,self.m,self.docs)["mismatches"],{"gameobject_activeSelf":1,"light_m_Enabled":1})
    def test_local_trs_drift(self):
        self.docs[103][1]["m_LocalPosition"]["x"]=9
        self.assertEqual(a.compare(self.model,self.m,self.docs)["mismatches"],{"m_LocalPosition":1})
    def test_missing_child_and_parent(self):
        self.docs[103][1]["m_Children"]=[];self.docs[105][1]["m_Father"]=p(104)
        self.assertEqual(a.compare(self.model,self.m,self.docs)["mismatches"],{"ordered_transform_children":1,"transform_parent":1})
    def test_external_pointer(self):
        self.docs[103][1]["m_Father"]={"fileID":104,"guid":GUID}
        with self.assertRaisesRegex(a.Rejected,"actual_nonlocal"):a.compare(self.model,self.m,self.docs)
    def test_wrong_actual_class(self):
        self.docs[105]=(4,self.docs[105][1])
        self.assertEqual(a.compare(self.model,self.m,self.docs)["mismatches"],{"native_class":1})
    def test_stage_pinned_and_optional(self):
        raw=Path("android-port/Experiments/ExportLineage/RaftExportLineage.cs").read_bytes()
        out=stage_trace.render(raw).decode()
        self.assertIn("asset.ClassID is not (1 or 4 or 108 or 224)",out)
        self.assertIn("nonexportable_transforms_skipped",out)
        self.assertEqual(out.count('json.WriteString("export_instance", exportInstance);'),3)
        self.assertEqual(out.count("FileMode.CreateNew"),3)
        with self.assertRaises(ValueError):stage_trace.render(raw+b"\n// drift")

    def test_actual_yaml_guid_and_duplicate_field(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as td:
            root=Path(td);assets=root/"Assets";assets.mkdir()
            scene=assets/"scene.unity";meta=assets/"scene.unity.meta"
            meta.write_text("guid: "+GUID+"\n")
            scene.write_text("%YAML 1.1\n--- !u!4 &-123\nTransform:\n  m_Father: {fileID: 0}\n")
            self.assertEqual(a.yaml_docs(root,GUID,{-123}),{-123:(4,{"m_Father":{"fileID":0}})})
            scene.write_text("%YAML 1.1\n--- !u!4 &-123\nTransform:\n  m_Father: {fileID: 0}\n  m_Father: {fileID: 1}\n")
            with self.assertRaisesRegex(a.Rejected,"duplicate_yaml_field"):a.yaml_docs(root,GUID,{-123})
            (assets/"other.unity.meta").write_text("guid: "+GUID+"\n")
            with self.assertRaisesRegex(a.Rejected,"duplicate_export_guid"):a.yaml_docs(root,GUID,{-123})

    def test_light_color_type_intensity_and_range_drift(self):
        d=self.docs[101][1]
        d["m_Type"]=2;d["m_Color"]["g"]=0.125;d["m_Intensity"]=4.0;d["m_Range"]=8.0
        self.assertEqual(a.compare(self.model,self.m,self.docs)["mismatches"],
                         {"light_m_Type":1,"light_m_Color":1,"light_m_Intensity":1,"light_m_Range":1})
