"""Authored full-document and inline stream identity for the actual Mesh consumer."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

from scripts.gt_verify_original_mesh_export import export_geometry, geometry
from test_gt_verify_original_mesh_export import YAML, TREE, FID

IDENTITY="wrong_exported_mesh_yaml_identity"
STORAGE="invalid_exported_mesh_vertex_storage"
BODY="invalid_exported_mesh_yaml_body"
HEADER="--- !u!43 &4300000"
STREAM="  m_StreamData:\n    size: 0\n"
HEX="0000803f"*3


def replace_once(text, old, new):
    assert text.count(old)==1, old
    return text.replace(old,new,1)


def stream(fields):
    return replace_once(YAML,STREAM,"  m_StreamData:\n"+fields)


def cases():
    # All cases must yield the same complete geometry dictionary on the
    # immutable pre-fix consumer, not merely avoid an exception.
    out=[
        ("stripped_mesh",replace_once(YAML,HEADER,HEADER+" stripped"),FID,IDENTITY),
        ("extra_root_before_mesh",replace_once(YAML,"\nMesh:\n","\nOther: {}\nMesh:\n"),FID,IDENTITY),
        ("extra_root_after_mesh",YAML+"Other: {}\n",FID,IDENTITY),
        ("unknown_prologue_directive","%UNEXPECTED ignored\n"+YAML,FID,IDENTITY),
        ("duplicate_yaml_directive","%YAML 1.1\n"+YAML,FID,IDENTITY),
        ("ignored_body_directive",YAML+"%UNEXPECTED ignored\n",FID,BODY),
        ("zero_fileid",replace_once(YAML,HEADER,"--- !u!43 &0"),0,IDENTITY),
        ("out_of_range_positive_fileid",replace_once(YAML,HEADER,"--- !u!43 &"+str(2**63)),2**63,IDENTITY),
        ("out_of_range_negative_fileid",replace_once(YAML,HEADER,"--- !u!43 &"+str(-(2**63)-1)),-(2**63)-1,IDENTITY),
        ("float_trace_fileid",YAML,float(FID),IDENTITY),
        ("bool_trace_fileid",replace_once(YAML,HEADER,"--- !u!43 &1"),True,IDENTITY),
        ("float_inline_size",stream("    size: 0.0\n"),FID,STORAGE),
        ("bool_inline_size",stream("    size: false\n"),FID,STORAGE),
        ("nonzero_offset",stream("    size: 0\n    offset: 1\n"),FID,STORAGE),
        ("negative_offset",stream("    size: 0\n    offset: -1\n"),FID,STORAGE),
        ("float_offset",stream("    size: 0\n    offset: 0.0\n"),FID,STORAGE),
        ("bool_offset",stream("    size: 0\n    offset: false\n"),FID,STORAGE),
        ("string_offset",stream("    size: 0\n    offset: '0'\n"),FID,STORAGE),
        ("stale_provider",stream("    size: 0\n    offset: 0\n    path: authored.resS\n"),FID,STORAGE),
        ("whitespace_provider",stream("    size: 0\n    path: ' '\n"),FID,STORAGE),
        ("numeric_provider",stream("    size: 0\n    path: 0\n"),FID,STORAGE),
        ("sequence_provider",stream("    size: 0\n    path: []\n"),FID,STORAGE),
        ("float_vertex_data_size",replace_once(YAML,"    m_DataSize: 12","    m_DataSize: 12.0"),FID,STORAGE),
    ]
    return out


def backends():
    assert yaml.__with_libyaml__ and yaml.CSafeLoader is not yaml.SafeLoader
    return (("libyaml",yaml.CSafeLoader),("python",yaml.SafeLoader))


class MeshDocumentStreamIdentity(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path=Path(tmp.name)/"mesh.asset"
        self.expected=geometry(TREE,bytes.fromhex(HEX),b"\0\0")

    def result(self,text,fid=FID):
        self.path.write_text(text,encoding="utf-8")
        return export_geometry(self.path,fid)

    def reject(self,text,fid,reason):
        with self.assertRaisesRegex(ValueError,"^"+reason+"$"):
            self.result(text,fid)

    def test_old_false_geometry_equalities_rejected_both_backends(self):
        for label,loader in backends():
            with patch.object(yaml,"CSafeLoader",loader):
                for name,text,fid,reason in cases():
                    with self.subTest(loader=label,case=name):
                        self.assertEqual(self.result(YAML),self.expected)
                        self.reject(text,fid,reason)

    def test_clean_legacy_and_complete_inline_stream(self):
        for label,loader in backends():
            with patch.object(yaml,"CSafeLoader",loader):
                for text in (YAML,
                             stream("    offset: 0\n    size: 0\n    path:\n"),
                             stream('    offset: 0\n    size: 0\n    path: ""\n'),
                             stream("    size: 0\n    offset: 0\n"),
                             stream("    size: 0\n    path: null\n")):
                    with self.subTest(loader=label,variant=text[-80:]):
                        self.assertEqual(self.result(text),self.expected)

    def test_signed_nonzero_int64_fileids_preserved(self):
        for label,loader in backends():
            with patch.object(yaml,"CSafeLoader",loader):
                for fid in (-(2**63),-1,1,2**63-1):
                    with self.subTest(loader=label,fid=fid):
                        self.assertEqual(self.result(replace_once(YAML,HEADER,"--- !u!43 &"+str(fid)),fid),self.expected)

    def test_optional_prologue_comments_bom_crlf_and_nested_marker_text(self):
        bare=YAML[YAML.index(HEADER):]
        texts=(bare,"# authored header\n\n"+YAML,"\ufeff"+YAML.replace("\n","\r\n"),
               YAML+"  m_Notes: |\n    --- !u!43 &4300000 stripped\n",
               replace_once(YAML,HEADER,"---  !u!43  &4300000  "))
        for label,loader in backends():
            with patch.object(yaml,"CSafeLoader",loader):
                for i,text in enumerate(texts):
                    with self.subTest(loader=label,variant=i):
                        self.assertEqual(self.result(text),self.expected)

    def test_wrong_class_wrong_id_and_multiple_or_malformed_markers(self):
        texts=(
            replace_once(YAML,HEADER,"--- !u!43 &4300001"),
            replace_once(YAML,HEADER,"--- !u!28 &4300000"),
            YAML+"--- !u!43 &4300000\nMesh: {}\n",
            YAML+"--- !u!43 &4300000 invalid\nMesh: {}\n",
            YAML+"---\nOther: {}\n",
            replace_once(YAML,HEADER,"--- !u!43 &"+("9"*5000)),
            "Other: {}\n"+YAML,
        )
        for label,loader in backends():
            with patch.object(yaml,"CSafeLoader",loader):
                for i,text in enumerate(texts):
                    with self.subTest(loader=label,variant=i):
                        self.reject(text,FID,IDENTITY)

    def test_noninline_size_and_missing_descriptor_size_rejected(self):
        for label,loader in backends():
            with patch.object(yaml,"CSafeLoader",loader):
                for i,text in enumerate((stream("    size: 12\n"),stream("    offset: 0\n    path:\n"),
                                         replace_once(YAML,STREAM,"  m_StreamData: []\n"))):
                    with self.subTest(loader=label,variant=i):
                        self.reject(text,FID,STORAGE)

    def test_real_payload_and_index_drift_still_visible(self):
        changed=replace_once(YAML,HEX,"00000000"*3)
        idx=replace_once(YAML,"  m_IndexBuffer: 0000","  m_IndexBuffer: 0100")
        for label,loader in backends():
            with self.subTest(loader=label),patch.object(yaml,"CSafeLoader",loader):
                self.assertNotEqual(self.result(changed)["vertex_buffer"],self.expected["vertex_buffer"])
                self.assertNotEqual(self.result(idx)["index_buffer"],self.expected["index_buffer"])
                self.reject(replace_once(YAML,"    m_DataSize: 12","    m_DataSize: 11"),FID,STORAGE)

    def test_previous_duplicate_mapping_error_unchanged(self):
        self.reject(replace_once(YAML,"    m_DataSize: 12","    m_DataSize: 11\n    m_DataSize: 12"),
                    FID,"mesh_yaml_duplicate_mapping_key")


if __name__=="__main__":
    unittest.main()
