"""Source-only external serialized Texture document identity regression tests."""
import io
import contextlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.verify_exported_material_texture_links import audit, GuardError, main

A,B,C,D=("a"*32,"b"*32,"c"*32,"d"*32)
FID=2800000
ROOTS={28:"Texture2D",84:"RenderTexture",86:"CustomRenderTexture",89:"Cubemap",
       117:"Texture3D",187:"Texture2DArray",188:"CubemapArray"}
PROLOG="%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n"


def material(pointer):
    return (PROLOG+"--- !u!21 &2100000\nMaterial:\n"
            "  m_SavedProperties:\n    m_TexEnvs:\n    - _MainTex:\n"
            "        m_Texture: "+pointer+"\n"
            "        m_Scale: {x: 1, y: 1}\n        m_Offset: {x: 0, y: 0}\n"
            "    m_Ints: []\n")


def ref(guid=B,fid=FID):
    return "{fileID: "+str(fid)+", guid: "+guid+", type: 3}"


def doc(cls=28,anchor=FID,root="Texture2D",suffix=""):
    return "--- !u!"+str(cls)+" &"+str(anchor)+suffix+"\n"+root+":\n"


class ExternalTextureDocuments(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)
        self.assets=self.root/"Assets"
        self.assets.mkdir()
        self.mat=self.assets/"Material.mat"
        self.texture=self.assets/"Texture.asset"
        self.mat.write_text(material(ref()))
        self.texture.write_text(PROLOG+doc())
        self.meta(self.mat,A)
        self.meta(self.texture,B)

    def meta(self,path,guid):
        Path(str(path)+".meta").write_text("guid: "+guid+"\nNativeFormatImporter:\n")

    def write(self,body):
        self.texture.write_text(PROLOG+body)

    def reject(self,reason):
        with self.assertRaises(GuardError) as ctx:
            audit(self.root)
        self.assertEqual(str(ctx.exception),reason)

    def resolved(self,count=1):
        report=audit(self.root)
        self.assertEqual(report["resolved_local_texture_refs"],count)
        self.assertFalse(report["source_export_equivalence_verified"])
        self.assertFalse(report["texture_pixel_color_verified"])
        self.assertFalse(report["device_render_verified"])
        self.assertFalse(report["ready_for_build"])

    def test_duplicate_same_class_target(self):
        self.write(doc()+doc())
        self.reject("duplicate_serialized_texture_object_id")

    def test_duplicate_other_class_after_target(self):
        self.write(doc()+doc(43,FID,"Mesh"))
        self.reject("duplicate_serialized_texture_object_id")

    def test_duplicate_other_class_before_target(self):
        self.write(doc(43,FID,"Mesh")+doc())
        self.reject("duplicate_serialized_texture_object_id")

    def test_duplicate_unreferenced_object_ids(self):
        self.write(doc()+doc(43,99,"Mesh")+doc(114,99,"MonoBehaviour"))
        self.reject("duplicate_serialized_texture_object_id")

    def test_numeric_alias_anchor_is_duplicate(self):
        self.write(doc()+doc(28,"02800000"))
        self.reject("duplicate_serialized_texture_object_id")

    def test_zero_unreferenced_anchor(self):
        self.write(doc()+doc(43,0,"Mesh"))
        self.reject("invalid_serialized_texture_object_id")

    def test_out_of_range_unreferenced_anchor(self):
        for anchor in (2**63,-(2**63)-1):
            with self.subTest(anchor=anchor):
                self.write(doc()+doc(43,anchor,"Mesh"))
                self.reject("invalid_serialized_texture_object_id")

    def test_malformed_marker_cannot_hide_duplicate(self):
        self.write(doc()+doc(43,FID,"Mesh"," unexpected"))
        self.reject("malformed_serialized_texture_header")

    def test_bare_document_marker_rejected(self):
        self.write(doc()+"---\nMesh:\n")
        self.reject("malformed_serialized_texture_header")

    def test_oversized_decimal_header_rejected(self):
        self.write(doc()+"--- !u!43 &"+"9"*5000+"\nMesh:\n")
        self.reject("malformed_serialized_texture_header")

    def test_stripped_texture_not_full_document(self):
        self.write(doc(suffix=" stripped"))
        self.reject("reference_target_not_verified_texture")

    def test_class_header_wrong_root(self):
        self.write(doc(root="Mesh"))
        self.reject("reference_target_not_verified_texture")

    def test_header_without_root(self):
        self.write("--- !u!28 &2800000\n")
        self.reject("reference_target_not_verified_texture")

    def test_two_root_mappings_rejected(self):
        self.write(doc()+"Texture2D:\n")
        self.reject("reference_target_not_verified_texture")

    def test_lodgroup_external_not_texture(self):
        self.write(doc(205,FID,"LODGroup"))
        self.reject("reference_target_not_verified_texture")

    def test_lodgroup_local_not_texture(self):
        self.mat.write_text(material("{fileID: 2800000}")+doc(205,FID,"LODGroup"))
        self.reject("unresolved_local_texture")

    def test_all_existing_real_texture_classes(self):
        for cls,root in ROOTS.items():
            with self.subTest(cls=cls):
                self.write(doc(cls,FID,root))
                self.resolved()

    def test_distinct_signed_and_stripped_unreferenced_anchors(self):
        self.write(doc(43,-(2**63),"Mesh")+doc(114,2**63-1,"MonoBehaviour"," stripped")+doc())
        self.resolved()

    def test_same_anchor_in_two_guids_is_not_duplicate(self):
        other=self.assets/"Other.asset"
        other.write_text(PROLOG+doc(89,FID,"Cubemap"))
        self.meta(other,C)
        other_mat=self.assets/"Other.mat"
        other_mat.write_text(material(ref(C)))
        self.meta(other_mat,D)
        self.resolved(2)

    def test_distinct_targets_in_one_container(self):
        self.write(doc()+doc(187,18700000,"Texture2DArray"))
        other_mat=self.assets/"Other.mat"
        other_mat.write_text(material(ref(B,18700000)))
        self.meta(other_mat,C)
        self.resolved(2)

    def test_bom_crlf_and_nested_marker_text(self):
        body=PROLOG+doc()+"  m_Text: |\n    --- !u!43 &2800000\n"
        self.texture.write_bytes(b"\xef\xbb\xbf"+body.replace("\n","\r\n").encode())
        self.resolved()

    def test_all_serialized_extensions(self):
        for suffix,cls,root in ((".asset",28,"Texture2D"),
                                 (".cubemap",89,"Cubemap"),
                                 (".rendertexture",84,"RenderTexture")):
            with self.subTest(suffix=suffix):
                target=self.texture.with_suffix(suffix)
                if target!=self.texture:
                    self.texture.rename(target)
                    Path(str(self.texture)+".meta").rename(Path(str(target)+".meta"))
                    self.texture=target
                self.write(doc(cls,FID,root))
                self.resolved()
                self.write(doc(cls,FID,root)*2)
                self.reject("duplicate_serialized_texture_object_id")

    def test_unique_wrong_class_stays_rejected(self):
        self.write(doc(43,FID,"Mesh"))
        self.reject("reference_target_not_verified_texture")

    def test_missing_anchor_stays_rejected(self):
        self.write(doc(anchor=FID+1))
        self.reject("reference_target_not_verified_texture")

    def test_cli_error_is_structured_and_private(self):
        self.write(doc()+doc(43,FID,"Mesh"))
        buf=io.StringIO()
        with contextlib.redirect_stdout(buf):
            result=main(["--project",str(self.root)])
        self.assertEqual(result,2)
        raw=buf.getvalue()
        report=json.loads(raw.removeprefix("RAFT_B46_TEXTURE_LINKS "))
        self.assertEqual(report["error_code"],"duplicate_serialized_texture_object_id")
        self.assertFalse(report["ready_for_build"])
        for forbidden in (str(self.root),"Texture.asset",B,str(FID)):
            self.assertNotIn(forbidden,raw)


if __name__=="__main__":
    unittest.main()
