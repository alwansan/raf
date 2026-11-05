"""Private-source synthetic controls for original Particle Shader48 same-export GUID.

No original Raft GUIDs, PathIDs or Material names in test fixtures.
"""
import copy
import json
import unittest

from scripts import t3_particle_same_export_bindings as m


OWNERS=("resources.assets","sharedassets0.assets",
        "sharedassets1.assets","sharedassets6.assets")
INSTANCE="e"*32


def source():
    # Authenticated six-scene originals have Material21 only in the first
    # three owners; sharedassets6 is a Shader48 owner, not Material21 owner.
    materials=[(OWNERS[0],101),(OWNERS[0],102),(OWNERS[1],103),
               (OWNERS[1],104),(OWNERS[2],105)]
    textures=[(OWNERS[0],201),(OWNERS[1],202),(OWNERS[2],203)]
    # For m_FileID=0 a source material texture must be in the SAME
    # serialized owner, not merely share an arbitrary PathID.
    keys=[textures[0]]*4+[textures[1]]*4+[textures[2]]*2
    src, counts={},{}
    for i,key in enumerate(materials):
        slots={}
        for j in range(2):
            t=keys[2*i+j]
            slots["fixture_slot_"+str(j)]=((0,t[1]),(1.,1.,0.,0.))
            counts[t]=counts.get(t,0)+1
        src[key]=slots
    assert len(src)==5 and len(counts)==3 and sum(counts.values())==10
    return src,counts


def build():
    src,targets=source()
    w1={"schema_version":1,"export_instance":INSTANCE,"objects":[]}
    b02={"schema_version":1,"export_instance":INSTANCE,"objects":[]}
    exported={}
    texture_ptr={}
    for i,key in enumerate(targets):
        dst=(2800000+i,"f"*31+str(i))
        texture_ptr[key]=(*dst,2)
        b02["objects"].append({
            "class_id":28,"source":{"owner":"Raft_Data/"+key[0],"path_id":key[1]},
            "export":{"file_id":dst[0],"guid":dst[1],"type":2}})
    for i,(key,slots) in enumerate(src.items()):
        mat=(2100000+i,"c"*31+str(i))
        w1["objects"].append({
            "class_id":21,"source":{"owner":"Raft_Data/"+key[0],"path_id":key[1]},
            "export":{"file_id":mat[0],"guid":mat[1],"type":2}})
        exported[mat]={
            label:(texture_ptr[(key[0],ptr[1])],uv)
            for label,(ptr,uv) in slots.items()}
    return src,targets,w1,b02,exported


class OriginalParticleSameInstanceExport(unittest.TestCase):
    def test_all_five_materials_three_textures_ten_links_exact(self):
        source,targets,w1,b02,actual=build()
        r=m.assess(source,targets,w1,b02,actual)
        self.assertEqual(r["status"],m.STATUS_MATCH)
        self.assertEqual(r["traced_selected_material21"],5)
        self.assertEqual(r["traced_selected_texture2d28"],3)
        self.assertEqual(r["original_source_material_texture_slots"],10)
        self.assertEqual(r["selected_exact_material_texenv_pointer_matches"],10)
        self.assertEqual(r["selected_uv_scale_offset_matches"],10)
        self.assertFalse(r["compiled_Unity_ShaderLab_or_Android_pixels_verified"])
        public=json.dumps(r)
        for secret in ("fixture_slot_","resources.assets","sharedassets0.assets",
                       "e"*32,"c"*31,"f"*31,"source_owner","path_id","2100000"):
            self.assertNotIn(secret,public)

    def test_cross_instance_W1_B02_traces_are_rejected(self):
        s,t,w,b,exp=build()
        b["export_instance"]="d"*32
        with self.assertRaisesRegex(ValueError,"Different exporter instances"):
            m.assess(s,t,w,b,exp)

    def test_missing_export_texture_trace_is_not_called_a_verified_match(self):
        s,t,w,b,exp=build()
        b["objects"].pop()
        r=m.assess(s,t,w,b,exp)
        self.assertEqual(r["status"],m.STATUS_MISMATCH)
        self.assertEqual(r["traced_selected_texture2d28"],2)
        self.assertEqual(r["selected_texture2d28_missing_export_trace"],1)
        self.assertLess(r["selected_exact_material_texenv_pointer_matches"],10)

    def test_untraced_original_texture_explicitly_skipped_nonexportable_collection(self):
        s,t,w,b,exp=build()
        missed=b["objects"].pop()
        b["nonexportable_texture_sources"]=[{"source":missed["source"]}]
        b["nonexportable_texture_objects_skipped"]=1
        r=m.assess(s,t,w,b,exp)
        self.assertEqual(r["status"],m.STATUS_MISMATCH)
        self.assertEqual(r["selected_texture2d28_missing_export_trace"],1)
        self.assertEqual(r["selected_missing_texture_skipped_nonexportable_collection"],1)
        self.assertEqual(r["selected_missing_texture_absent_all_export_collections"],0)
        self.assertEqual(r["selected_missing_texture_reason_unclassified"],0)
        # This synthetic third source texture is shared by TWO material slots;
        # missing one original Texture2D trace means 8/10 pointer matches.
        self.assertEqual(r["selected_exact_material_texenv_pointer_matches"],8)
        safe=json.dumps(r)
        self.assertNotIn(missed["source"]["owner"],safe)
        self.assertNotIn('"path_id"',safe)

    def test_untraced_original_texture_absent_all_collections_is_distinct(self):
        s,t,w,b,exp=build()
        b["objects"].pop()
        b["nonexportable_texture_sources"]=[]
        b["nonexportable_texture_objects_skipped"]=0
        r=m.assess(s,t,w,b,exp)
        self.assertEqual(r["selected_missing_texture_skipped_nonexportable_collection"],0)
        self.assertEqual(r["selected_missing_texture_absent_all_export_collections"],1)
        self.assertEqual(r["selected_missing_texture_reason_unclassified"],0)

    def test_nonexportable_source_trace_malformed_or_overlap_rejected(self):
        s,t,w,b,exp=build()
        b["nonexportable_texture_sources"]="wrong"
        with self.assertRaisesRegex(ValueError,"malformed_private_B02"):
            m.assess(s,t,w,b,exp)
        s,t,w,b,exp=build()
        b["nonexportable_texture_sources"]=[{"source":b["objects"][0]["source"]}]
        with self.assertRaisesRegex(ValueError,"both_exportable_and_nonexportable"):
            m.assess(s,t,w,b,exp)

    def test_missing_material_trace_is_not_called_a_verified_match(self):
        s,t,w,b,exp=build()
        w["objects"].pop()
        r=m.assess(s,t,w,b,exp)
        self.assertEqual(r["status"],m.STATUS_MISMATCH)
        self.assertEqual(r["selected_material21_missing_export_trace"],1)
        self.assertEqual(r["traced_selected_material21"],4)

    def test_exported_Material_Texture2D_pointer_to_wrong_guid_detected(self):
        s,t,w,b,exp=build()
        key=next(iter(exp))
        label=next(iter(exp[key]))
        ptr,uv=exp[key][label]
        exp[key][label]=((ptr[0],"d"*32,ptr[2]),uv)
        r=m.assess(s,t,w,b,exp)
        self.assertEqual(r["status"],m.STATUS_MISMATCH)
        self.assertEqual(r["selected_source_texture_to_other_exported_target"],1)
        self.assertEqual(r["selected_exact_material_texenv_pointer_matches"],9)

    def test_null_exported_texture_or_missing_Material_YAML_detected(self):
        s,t,w,b,exp=build()
        k=next(iter(exp))
        label=next(iter(exp[k]))
        ptr,uv=exp[k][label]
        exp[k][label]=((0,"0"*32,0),uv)
        r=m.assess(s,t,w,b,exp)
        self.assertEqual(r["selected_source_nonnull_texture_to_null"],1)
        self.assertEqual(r["status"],m.STATUS_MISMATCH)
        s,t,w,b,exp=build()
        del exp[next(iter(exp))]
        r=m.assess(s,t,w,b,exp)
        self.assertEqual(r["selected_material21_without_exported_YAML"],1)
        self.assertEqual(r["status"],m.STATUS_MISMATCH)

    def test_uv_drift_or_missing_property_detected(self):
        s,t,w,b,exp=build()
        k=next(iter(exp));slot=next(iter(exp[k]))
        ptr,uv=exp[k][slot]
        exp[k][slot]=(ptr,(uv[0],uv[1],uv[2]+.5,uv[3]))
        r=m.assess(s,t,w,b,exp)
        self.assertEqual(r["selected_uv_missing_or_mismatched"],1)
        self.assertEqual(r["status"],m.STATUS_MISMATCH)
        s,t,w,b,exp=build()
        del exp[next(iter(exp))]["fixture_slot_0"]
        r=m.assess(s,t,w,b,exp)
        self.assertEqual(r["selected_material21_source_slots_missing_after_export"],1)
        self.assertEqual(r["status"],m.STATUS_MISMATCH)

    def test_duplicate_private_identity_or_export_guid_collision_rejected(self):
        s,t,w,b,exp=build()
        w["objects"].append(copy.deepcopy(w["objects"][0]))
        with self.assertRaisesRegex(ValueError,"duplicate_selected_original_material"):
            m.assess(s,t,w,b,exp)
        s,t,w,b,exp=build()
        b["objects"][1]["export"]=dict(b["objects"][0]["export"])
        with self.assertRaisesRegex(ValueError,"alias_collision"):
            m.assess(s,t,w,b,exp)

    def test_private_source_graph_requires_exact_five_ten_three_targets(self):
        s,t,w,b,exp=build()
        s.pop(next(iter(s)))
        with self.assertRaisesRegex(ValueError,"scope"):
            m.assess(s,t,w,b,exp)
        s,t,w,b,exp=build()
        first=next(iter(t));t[first]+=1
        with self.assertRaisesRegex(ValueError,"source_linkage"):
            m.assess(s,t,w,b,exp)

if __name__=="__main__":
    unittest.main()
