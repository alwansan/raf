"""Synthetic strict source provider SHA and range tests for T3 particle pipeline.

No proprietary Raft stream bytes, provider names, IDs or SHA are in fixtures.
"""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.t3_original_particle_stream_provider import (
    STATUS, REL_COLUMNS, plan_contract, range_fingerprints, ZIP2_SHA
)


def plan():
    provider="synthetic_stream_fixture.resS"
    return {"schema_version":1,"source_sha":ZIP2_SHA,
            "source_scope":"T3_private_108_particle_original_Texture2D",
            "providers":{provider:{
                "bytes":32,"sha256":"a"*64,
                "ranges":[[0,5],[8,5],[20,5]]}}}


def manifest(path,kind="plain",size=32,digest="a"*64):
    path.write_text("\t".join(REL_COLUMNS)+"\n"+"\t".join((
        kind,str(size),digest,"660",
        "Raft_Data/synthetic_stream_fixture.resS"))+"\n")


class ParticleSourceStreamStage(unittest.TestCase):
    def test_real_manifest_shape_and_three_range_scope(self):
        with tempfile.TemporaryDirectory() as d:
            doc=Path(d)/"RAFT_FILE_MANIFEST.tsv"
            manifest(doc)
            r=plan_contract(plan(),doc)
            self.assertEqual(r["kind"],"plain")
            self.assertEqual(r["pin"],(32,"a"*64))
            self.assertEqual(r["extents"]["extents"],3)
            self.assertEqual(r["extents"]["partial_overlaps"],0)
            self.assertEqual(r["extents"]["duplicate_ranges"],0)

    def test_split_provider_is_allowed_after_manifest_pin(self):
        with tempfile.TemporaryDirectory() as d:
            doc=Path(d)/"RAFT_FILE_MANIFEST.tsv"
            manifest(doc,kind="split")
            self.assertEqual(plan_contract(plan(),doc)["kind"],"split")

    def test_manifest_sha_and_size_or_kind_mismatch_never_accepted(self):
        for kind,size,digest in (("plain",33,"a"*64),
                                 ("plain",32,"b"*64),
                                 ("lfs",32,"a"*64)):
            with self.subTest(kind=kind,size=size),tempfile.TemporaryDirectory() as d:
                file=Path(d)/"RAFT_FILE_MANIFEST.tsv"
                manifest(file,kind=kind,size=size,digest=digest)
                with self.assertRaisesRegex(ValueError,"manifest_pin_mismatch"):
                    plan_contract(plan(),file)

    def test_missing_or_wrong_source_scope_or_extra_provider_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            doc=Path(d)/"RAFT_FILE_MANIFEST.tsv"
            manifest(doc)
            for prop,val in (
                ("source_sha","not-zip2"),
                ("source_scope","forged-target"),
                ("schema_version",True),
            ):
                p=plan();p[prop]=val
                with self.subTest(prop=prop),self.assertRaises(ValueError):
                    plan_contract(p,doc)
            p=plan()
            p["providers"]["other.resS"]=p["providers"]["synthetic_stream_fixture.resS"]
            with self.assertRaises(ValueError):
                plan_contract(p,doc)

    def test_only_positive_manifest_bounded_integer_extents(self):
        with tempfile.TemporaryDirectory() as d:
            doc=Path(d)/"RAFT_FILE_MANIFEST.tsv"
            manifest(doc)
            for offsets in (
                [[30,3],[8,5],[20,5]], # overflow
                [[0,0],[8,5],[20,5]], # empty
                [[0,True],[8,5],[20,5]], # boolean
                [[-1,3],[8,5],[20,5]], # negative
                [[0,5]], # no three targets
            ):
                p=plan();p["providers"]["synthetic_stream_fixture.resS"]["ranges"]=offsets
                with self.subTest(offsets=offsets),self.assertRaises(ValueError):
                    plan_contract(p,doc)

    def test_real_bytes_three_seeks_and_private_digests_not_in_results(self):
        with tempfile.TemporaryDirectory() as d:
            file=Path(d)/"synthetic_stream_fixture.resS"
            file.write_bytes(bytes(range(32)))
            v=range_fingerprints(file,[(0,5),(8,5),(20,5)],expected_size=32)
            self.assertEqual(v["read_count"],3)
            self.assertEqual(v["read_bytes"],15)
            self.assertEqual(v["distinct_source_range_fingerprints"],3)
            self.assertEqual(v["nonzero_source_image_ranges"],3)
            self.assertNotIn("sha256",json.dumps(v))
            self.assertNotIn("synthetic_stream_fixture",json.dumps(v))

    def test_duplicate_shared_original_range_counts_separate_references(self):
        with tempfile.TemporaryDirectory() as d:
            file=Path(d)/"private.resS"
            file.write_bytes(b"abcde12345"+bytes(22))
            dct=range_fingerprints(file,[(0,5),(0,5),(5,5)],expected_size=32)
            self.assertEqual(dct["read_count"],3)
            self.assertEqual(dct["distinct_source_range_fingerprints"],2)
            self.assertEqual(dct["nonzero_source_image_ranges"],3)

    def test_staged_source_byte_length_and_range_bounds_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            file=Path(d)/"private.resS"
            file.write_bytes(b"abcde")
            with self.assertRaisesRegex(ValueError,"unauthenticated"):
                range_fingerprints(file,[(0,5)],expected_size=6)
            for spans in ([(4,2)],[(1,0)],[(-1,2)],[(True,2)]):
                with self.subTest(spans=spans),self.assertRaises(ValueError):
                    range_fingerprints(file,spans,expected_size=5)

    def test_source_only_result_never_claims_export_or_mobile_pixels(self):
        self.assertIn("SOURCE",STATUS)
        self.assertNotIn("ANDROID",STATUS)
        self.assertEqual(REL_COLUMNS[0],"kind")


if __name__=="__main__":
    unittest.main()
