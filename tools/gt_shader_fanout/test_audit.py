"""Independent authored YAML: exact GUID fanout and stale aggregate controls."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts import t3_audit_exported_material_programs as old_material
from scripts import t3_exported_renderer_shader_impact as old_impact
from tools.gt_shader_fanout.audit import scan,compare_receipt

A="1"*32; B="2"*32; C="3"*32; N="4"*32
M1="a"*32; M2="b"*32; M3="c"*32; M4="d"*32
R="e"*32; P="f"*32
HEADER="%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n"
SHADER='Shader "GT Authored Shared" { SubShader { Pass { CGPROGRAM\nfloat4 frag():SV_Target{return 1;}\nENDCG } } }\n'

def ptr(g,f=2100000,t=2):
    return "{fileID: %d, guid: %s, type: %d}"%(f,g,t)
def renderer(fid,slots,cls=23,root="MeshRenderer",stripped=False):
    return f"--- !u!{cls} &{fid}"+(" stripped" if stripped else "")+f"\n{root}:\n  m_Materials:"+("\n"+"".join("  - "+v+"\n" for v in slots) if slots else " []\n")

class Fanout(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name);self.assets=self.root/"Assets";self.assets.mkdir()
        for label,g in (("a",A),("b",B),("c",C),("n",N)):
            self.write(label+".shader",SHADER if g==N else "//DummyShaderTextExporter\n"+SHADER,g,importer="ShaderImporter")
        for label,g,s in (("one",M1,A),("two",M2,B),("three",M3,C),("four",M4,N)):
            self.write(label+".mat",HEADER+"--- !u!21 &2100000\nMaterial:\n  m_Shader: "+ptr(s,4800000,3)+"\n",g)
        self.write("scene.unity",HEADER+renderer(1,[ptr(M2)]*4+ [ptr(M1)])+renderer(2,[ptr(M2),ptr(M4)])+renderer(3,[ptr(M1)]),R)
        self.write("prefab.prefab",HEADER+renderer(1,[ptr(M2)],137,"SkinnedMeshRenderer"),P)
    def write(self,name,raw,g,importer="NativeFormatImporter"):
        p=self.assets/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(raw)
        p.with_name(p.name+".meta").write_text("fileFormatVersion: 2\nguid: "+g+"\n"+importer+":\n  userData:\n")
        return p
    def report(self):return scan(self.root)[0]
    def edit(self,name,old,new):
        p=self.assets/name;s=p.read_text();self.assertIn(old,s);p.write_text(s.replace(old,new))
    def test_exact_guid_rank(self):
        report,private=scan(self.root)
        self.assertEqual([k for k,_ in private],[B,A,C])
        self.assertEqual(report["dummy_shader_guid_targets"],3)
        self.assertEqual(report["dummy_shader_name_groups"],1)
        self.assertEqual(report["shared_name_groups"],1)
        self.assertEqual(report["dummy_targets_without_serialized_renderer_use"],1)
        rows=report["ranked_anonymous_targets"]
        self.assertEqual([x["renderer_slots"] for x in rows],[6,2,0])
        self.assertEqual([x["renderer_objects"] for x in rows],[3,2,0])
        self.assertEqual([x["scene_slots"] for x in rows],[5,2,0])
        self.assertEqual([x["prefab_slots"] for x in rows],[1,0,0])
        self.assertEqual([x["exclusive_dummy_renderer_objects"] for x in rows],[2,1,0])
        self.assertEqual(report["counts"]["renderers_with_multiple_dummy_targets"],1)
        self.assertEqual(report["counts"]["renderers_with_dummy_slots"],4)
        old=old_material.audit(self.root,rank_dummy_targets=True)
        self.assertEqual(list(old["dummy_shader_material_counts_by_name_digest"].values()),[3])
        for k in ("source_shader48_identity_proven","prefab_instance_expansion_proven","shader_program_or_runtime_variant_proven","gpu_or_white_mesh_repair_proven","production_install_allowed"):
            self.assertIs(report[k],False)
    def test_stale_material_report_old_accepts_same_totals(self):
        old=old_material.audit(self.root,rank_dummy_targets=True)
        before=self.report()
        self.edit("one.mat",A,B)
        self.edit("two.mat",B,A)
        now=self.report()
        self.assertEqual(old,old_material.audit(self.root,rank_dummy_targets=True))
        self.assertEqual(old_impact.audit(self.root,old)["status"],old_impact.RESULT_STATUS)
        self.assertNotEqual(before["snapshot_commitment_sha256"],now["snapshot_commitment_sha256"])
        self.assertEqual(scan(self.root)[1][0][0],A)
        with self.assertRaisesRegex(ValueError,"different_export_snapshot"):compare_receipt(now,before)
    def test_repeat_snapshot(self):
        compare_receipt(self.report(),self.report())
    def test_folder_collision_old_accepts(self):
        p=self.assets/"folder";p.mkdir()
        (self.assets/"folder.meta").write_text("fileFormatVersion: 2\nguid: "+B+"\nfolderAsset: yes\n")
        self.assertEqual(old_impact.audit(self.root)["counts"]["renderer_slots_dummy_shader"],8)
        with self.assertRaisesRegex(ValueError,"duplicate_or_reserved"):self.report()
    def test_valid_folder(self):
        (self.assets/"folder").mkdir()
        (self.assets/"folder.meta").write_text("fileFormatVersion: 2\nguid: "+"9"*32+"\nfolderAsset: yes\n")
        self.assertEqual(self.report()["dummy_shader_guid_targets"],3)
    def test_texture_collision(self):
        self.write("texture.png","authored identity only",M1,importer="TextureImporter")
        with self.assertRaisesRegex(ValueError,"duplicate_or_reserved"):self.report()
    def test_missing_external_type_not_resolved(self):
        self.edit("scene.unity",ptr(M2),"{fileID: 2100000, guid: "+M2+"}")
        with self.assertRaisesRegex(ValueError,"pointer_shape"):self.report()
    def test_importer_type_material_is_unverified(self):
        self.edit("scene.unity",ptr(M2),ptr(M2,t=3))
        report=self.report()
        self.assertEqual(report["counts"]["slot_unsupported_material_pointer"],5)
        self.assertEqual(report["counts"]["slot_dummy"],3)
    def test_duplicate_slot_key_reject(self):
        self.edit("scene.unity","  m_Materials:\n","  m_Materials: []\n  m_Materials:\n")
        with self.assertRaisesRegex(ValueError,"duplicate_or_invalid_yaml_key"):self.report()
    def test_malformed_header_reject(self):
        p=self.assets/"scene.unity";p.write_text(p.read_text()+"--- !u!23 &oops\nMeshRenderer:\n  m_Materials: []\n")
        with self.assertRaisesRegex(ValueError,"malformed_yaml_document_header"):self.report()
    def test_stripped_not_real_renderer(self):
        p=self.assets/"scene.unity";p.write_text(p.read_text()+renderer(9,[ptr(M2)],stripped=True))
        report=self.report()
        self.assertEqual(report["counts"]["stripped_renderer_documents"],1)
        self.assertEqual(report["renderer_documents"],4)
    def test_native_shader_document_unverified(self):
        g="5"*32
        self.write("native.asset",HEADER+"--- !u!48 &4800000\nShader:\n  m_Name: GT Authored Identity\n",g)
        self.edit("one.mat",ptr(A,4800000,3),ptr(g,4800000,2))
        report=self.report()
        self.assertEqual(report["counts"]["slot_native_shader_document_unverified"],2)
        self.assertEqual(report["dummy_shader_guid_targets"],2)
    def test_duplicate_anchor_reject(self):
        self.edit("scene.unity","&2\n","&1\n")
        with self.assertRaisesRegex(ValueError,"duplicate_or_zero_yaml_anchor"):self.report()
    def test_local_embedded_material(self):
        p=self.assets/"scene.unity";p.write_text(p.read_text()+"--- !u!21 &-100\nMaterial:\n  m_Shader: "+ptr(A,4800000,3)+"\n"+renderer(11,["{fileID: -100}"]))
        report=self.report()
        self.assertEqual(report["material_documents"],5)
        self.assertEqual(report["counts"]["slot_dummy"],9)
    def test_no_private_identifiers(self):
        serial=json.dumps(self.report())
        for token in (A,B,C,N,M1,M2,M3,M4,R,P,"GT Authored Shared","scene.unity",str(self.root)):
            self.assertNotIn(token,serial)
    def test_unknown_slot_blocks_exclusivity(self):
        self.edit("prefab.prefab",ptr(M2),ptr(M2)+"\n  - "+ptr("8"*32))
        self.assertEqual(self.report()["ranked_anonymous_targets"][0]["exclusive_dummy_renderer_objects"],1)
    def test_invalid_null_pointer(self):
        self.edit("prefab.prefab",ptr(M2),ptr(M2,f=0))
        with self.assertRaisesRegex(ValueError,"ambiguous_null_pointer"):self.report()

if __name__=="__main__":unittest.main()
