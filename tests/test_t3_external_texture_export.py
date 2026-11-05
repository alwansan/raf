"""T3 original cross-owner Texture2D identity: guarded fake same-export fixtures."""
import unittest
from scripts import t3_external_texture_export as m

class ExternalPointerContract(unittest.TestCase):
    def fixture(self):
        originals={(m.OWNER,i):{} for i in range(1,42)}
        external_names=["archive:/Raft_Data/sharedassets0.assets",
                        "archive:/Raft_Data/sharedassets1.assets"]
        kind={name:{} for name in m.TARGETS}
        trace={"schema_version":1,"export_instance":"a"*32,"objects":[]}
        textures={"schema_version":1,"export_instance":"a"*32,"objects":[]}
        exported={}
        for i in range(1,42):
            dst=(2100000+i,"b"*32)
            trace["objects"].append(
                {"class_id":21,"source":{"owner":m.OWNER,"path_id":i},
                 "export":{"file_id":dst[0],"guid":dst[1],"type":2},
                 "exportable":True})
            exported[dst]={}
        for i in range(1,26):
            name="sharedassets0.assets" if i<=22 else "sharedassets1.assets"
            fid=1 if i<=22 else 2
            pid=i if i<=22 else i-22
            namekey="F%03d"%i
            key=(m.OWNER,(i-1)%41+1)
            originals[key][namekey]=((fid,pid),(1.,1.,0.,0.))
            kind[name][pid]="Texture2D"
            ptr=(2800000+i,"c"*32,3)
            textures["objects"].append({
                "class_id":28,
                "source":{"owner":name,"path_id":pid},
                "export":{"file_id":ptr[0],"guid":ptr[1],"type":ptr[2]}})
            exported[trace["objects"][(i-1)%41]["export"]["file_id"],"b"*32][namekey]=(ptr,(1.,1.,0.,0.))
        for i in range(202):
            mid=(i%41)+1
            key="NULL_%d"%i
            originals[(m.OWNER,mid)][key]=((0,0),(1.,1.,0.,0.))
            exported[(2100000+mid,"b"*32)][key]=((0,"0"*32,0),(1.,1.,0.,0.))
        return originals,external_names,kind,trace,textures,exported
    def call(self,objs=None):
        return m.compare_external(*(objs or self.fixture()))
    def test_all_25_authentic_original_targets_and_export_links_match(self):
        a=self.call()
        self.assertEqual(a["status"],"SCOPED_25_EXTERNAL_TEXTURE_MATCH")
        self.assertEqual(a["exact_external_texture_targets_matched"],25)
        self.assertEqual(a["source_target_Texture2D_verified"],25)
        self.assertEqual(a["authentic_external_source_owner_counts"],m.TARGETS)
        self.assertFalse(a["full_game_or_android_gpu_pixels_verified"])
    def test_cross_export_instance_never_mixed(self):
        a=list(self.fixture());a[4]["export_instance"]="d"*32
        with self.assertRaisesRegex(ValueError,"Different exporter"):
            self.call(a)
    def test_original_target_class_not_texture_rejected_as_match(self):
        a=list(self.fixture());a[2]["sharedassets0.assets"][1]="Mesh"
        r=self.call(a)
        self.assertNotEqual(r["status"],"SCOPED_25_EXTERNAL_TEXTURE_MATCH")
        self.assertEqual(r["original_external_wrong_class_or_missing"],1)
    def test_missing_original_target_not_assumed_present(self):
        a=list(self.fixture());del a[2]["sharedassets1.assets"][1]
        r=self.call(a)
        self.assertEqual(r["original_external_wrong_class_or_missing"],1)
    def test_missing_export_texture_trace_never_guessed(self):
        a=list(self.fixture());a[4]["objects"].pop()
        r=self.call(a)
        self.assertEqual(r["missing_target_trace_records"],1)
    def test_mutated_export_guid_causes_pointer_mismatch(self):
        a=list(self.fixture())
        key=(2100001,"b"*32)
        before=a[5][key]["F001"]
        a[5][key]["F001"]=((before[0][0],"d"*32,3),before[1])
        r=self.call(a)
        self.assertEqual(r["wrong_external_texture_pointer_targets"],1)
    def test_missing_export_mat_slot_not_silenced(self):
        a=list(self.fixture());del a[5][(2100001,"b"*32)]["F001"]
        r=self.call(a)
        self.assertEqual(r["missing_export_material_slots"],1)
    def test_exported_null_not_same_as_source_binding(self):
        a=list(self.fixture());a[5][(2100001,"b"*32)]["F001"]=((0,"0"*32,0),None)
        r=self.call(a)
        self.assertEqual(r["exported_external_slots_became_null"],1)
    def test_malformed_dependency_provider_index_fails_closed(self):
        a=list(self.fixture())
        a[0][(m.OWNER,1)]["F001"]=((3,1),(1.,1.,0.,0.))
        with self.assertRaisesRegex(ValueError,"fileid_out_of_bounds"):
            self.call(a)
    def test_same_pathid_across_different_original_owners_not_alias(self):
        a=list(self.fixture())
        tex=a[4]["objects"]
        # This deliberately makes sharedassets1 target #1 point to the
        # sharedassets0 target #1 export pointer, while PathIDs are equal.
        target=next(i for i in tex if i["source"]["owner"]=="sharedassets1.assets")
        other=next(i for i in tex if i["source"]["owner"]=="sharedassets0.assets")
        target["export"]=other["export"].copy()
        self.assertEqual(self.call(a)["wrong_external_texture_pointer_targets"],1)
    def test_private_names_and_guids_not_emitted(self):
        summary=str(self.call())
        self.assertNotIn("F001",summary)
        self.assertNotIn("a"*32,summary)
        self.assertNotIn("b"*32,summary)
    def test_material_trace_duplicate_identity_refused(self):
        a=list(self.fixture())
        a[3]["objects"].append(a[3]["objects"][0].copy())
        with self.assertRaisesRegex(ValueError,"duplicate"):
            self.call(a)
if __name__=="__main__": unittest.main()
