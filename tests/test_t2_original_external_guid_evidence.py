"""T2 source-free tests: never include original asset identifiers or raw files."""
import unittest
from types import SimpleNamespace

from scripts.t2_original_external_guid_evidence import (
    classify_guid_edges, normalized_guid, target_recipient_catalog,
)

ZERO = b"\x00" * 16
G1 = b"\x01" * 16
G2 = b"\x02" * 16


def ext(path, guid, typeid=0):
    return SimpleNamespace(path=path, guid=guid, type=typeid)


def mat(fid, pid):
    return SimpleNamespace(
        type=SimpleNamespace(name="Material"),
        read_typetree=lambda: {"m_Shader":{"m_FileID":fid,"m_PathID":pid}},
    )


def shader():
    return SimpleNamespace(type=SimpleNamespace(name="Shader"))


def file(externals, objects):
    return SimpleNamespace(externals=externals,
                           objects={i:item for i,item in enumerate(objects)})


class SourceExternalGuidTests(unittest.TestCase):
    def test_two_same_original_fileID_and_zero_guid(self):
        r=classify_guid_edges([(1,"alpha",ZERO,0),(1,"alpha",ZERO,0)])
        self.assertEqual(r["external_original_Shader_refs"],2)
        self.assertEqual(r["external_unique_fileIDs"],1)
        self.assertEqual(r["external_GUID_zero_rows"],2)
        self.assertEqual(r["external_distinct_nonzero_GUIDs"],0)
        self.assertFalse(r["GUID_is_independent_original_target_authority"])

    def test_two_distinct_nonzero_guid_types(self):
        r=classify_guid_edges([(1,"alpha",G1,0),(2,"beta",G2,2)])
        self.assertEqual((r["external_GUID_nonzero_rows"],
                          r["external_distinct_nonzero_GUIDs"]), (2,2))
        self.assertEqual(r["external_type_2_rows"],1)

    def test_same_file_target_conflicting_guid_not_guaranteed(self):
        r=classify_guid_edges([(1,"same",G1,0),(2,"same",G2,0)])
        self.assertEqual(r["external_same_target_distinct_GUID_conflicts"],1)
        self.assertFalse(r["GUID_is_independent_original_target_authority"])

    def test_one_fileID_conflicting_identity_fails(self):
        for rows in [
            [(1,"same",G1,0),(1,"different",G1,0)],
            [(1,"same",G1,0),(1,"same",G2,0)],
            [(1,"same",G1,0),(1,"same",G1,2)],
        ]:
            with self.subTest(rows=rows),self.assertRaises(ValueError):
                classify_guid_edges(rows)

    def test_guid_strict_bytes_length(self):
        self.assertEqual(normalized_guid(ZERO),ZERO)
        for value in ("a"*16,b"123",bytearray(G1),None,b"x"*17):
            with self.subTest(value=type(value)),self.assertRaises(ValueError):
                normalized_guid(value)

    def test_invalid_rows_and_fileid(self):
        bads=[
            [(1,"a",G1,0)], [],
            [(True,"a",G1,0),(2,"b",G2,0)],
            [(0,"a",G1,0),(2,"b",G2,0)],
            [(1,"a",G1,4),(2,"b",G2,0)],
            [(1,"a",G1,True),(2,"b",G2,0)],
            [(1,"a",G1,0),("2","b",G2,0)],
        ]
        for rows in bads:
            with self.subTest(rows=str(rows)[:25]),self.assertRaises(ValueError):
                classify_guid_edges(rows)

    def test_reciprocal_foam_candidate_and_typed_material(self):
        obj=file(
            [ext("archive:/Raft_Data/sharedassets0.assets",G1,2),
             ext("archive:/elsewhere.assets",ZERO,0)],
            [mat(1,2420),mat(2,2420),mat(0,2420),mat(1,100),shader()])
        r=target_recipient_catalog(obj)
        self.assertEqual(r["target_reciprocal_original_Foam_owner_name_candidates"],1)
        self.assertEqual(r["target_material_to_Foam_owner_and_PathID_candidates"],1)
        self.assertEqual(r["target_reciprocal_original_Foam_owner_nonzero_GUID_count"],1)
        self.assertEqual(r["target_file_material_count"],4)
        self.assertFalse(r["reciprocal_owner_name_is_independent_GUID_proof"])

    def test_no_reciprocal_does_not_imply_no_runtime_link(self):
        r=target_recipient_catalog(file([ext("other.assets",G1)],[shader()]))
        self.assertEqual(r["target_reciprocal_original_Foam_owner_name_candidates"],0)
        self.assertEqual(r["target_material_to_Foam_owner_and_PathID_candidates"],0)

    def test_target_external_malformed_guid(self):
        with self.assertRaisesRegex(ValueError, "GUID"):
            target_recipient_catalog(file([ext("sharedassets0.assets",b"x")],[shader()]))

    def test_target_external_invalid_type(self):
        with self.assertRaisesRegex(ValueError,"type"):
            target_recipient_catalog(file([ext("sharedassets0.assets",G1,9)],[shader()]))

    def test_target_malformed_material_reference(self):
        with self.assertRaisesRegex(ValueError,"pointer_malformed"):
            target_recipient_catalog(file([ext("sharedassets0.assets",G1)],[mat(1,-1)]))


if __name__=="__main__":
    unittest.main()
