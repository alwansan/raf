"""GFX-MULTI-043 source-free checks for original Shader48 sidecar/CLR #US evidence.

No original owner PC assets are checked in; all fixtures are synthetic.
"""
import unittest
from types import SimpleNamespace

from gfxlab.tools.multi_shader_managed_literal_sidecar import (
    ASSEMBLIES, validate_manifest, literal_heap_values,
    member_reference_name_counts, WEAK_METHOD_NAMES,
)


def synthetic_manifest(source_sidecar=False):
    d={
        "Raft_Data/Synthetic/safe-%03d.assets"%i:{
            "kind":"plain","bytes":"512","sha256":"c"*64
        } for i in range(364)
    }
    for a in ASSEMBLIES.values():
        d[a["path"]]={
            "kind":"plain",
            "bytes":str(a["bytes"]),
            "sha256":a["sha"],
        }
    if source_sidecar:
        del d["Raft_Data/Synthetic/safe-000.assets"]
        d["Raft_Data/Synthetic/opt-in-original.shader"]={
            "kind":"plain","bytes":"512","sha256":"c"*64
        }
    return d


class MockUsHeap:
    rva=0
    def __init__(self,items):
        self.items=items
        self.size=len(items)+1
    def sizeof(self):
        return self.size
    def get(self,offset,errors=None):
        text=self.items[offset-1]
        return SimpleNamespace(value=text,raw_size=1)


class MockPe:
    def __init__(self,items,memberrefs=None):
        self.net=SimpleNamespace(
            user_strings=MockUsHeap(items),
            mdtables=SimpleNamespace(
                MemberRef=SimpleNamespace(rows=[
                    SimpleNamespace(Name=name) for name in (memberrefs or [])
                ])
            )
        )
    def get_data(self,offset,length):
        return b"x"


class TestManagedOriginalSourceSidecarSafety(unittest.TestCase):
    def test_manifest_original_366_no_standalone_shader_extensions(self):
        self.assertEqual(validate_manifest(synthetic_manifest()),0)

    def test_manifest_source_candidate_detected_without_name_export(self):
        self.assertEqual(validate_manifest(synthetic_manifest(True)),1)

    def test_sha_pin_detects_modified_original_assembly_manifest(self):
        d=synthetic_manifest()
        d["Custom.dll"]["sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"MANIFEST_PIN_FAILED"):
            validate_manifest(d)

    def test_reject_manifest_unexpected_count(self):
        d=synthetic_manifest()
        d.pop("Raft_Data/Synthetic/safe-001.assets")
        with self.assertRaisesRegex(ValueError,"ENTRY_COUNT_DRIFT"):
            validate_manifest(d)

    def test_user_string_heap_is_typed_not_arbitrary_byte_scan(self):
        literals,count,has=literal_heap_values(MockPe([
            "_SourceOnlyProperty","Unrelated","_SourceOnlyProperty"]))
        self.assertTrue(has)
        self.assertEqual(count,3)
        self.assertEqual(literals,{"_SourceOnlyProperty","Unrelated"})

    def test_member_names_are_only_weak_evidence(self):
        counts,total=member_reference_name_counts(MockPe([],[
            "PropertyToID","SetFloat","SetTexture","CustomMethod","SetTexture"]))
        self.assertEqual(total,5)
        self.assertEqual(counts["PropertyToID"],1)
        self.assertEqual(counts["SetTexture"],2)
        self.assertEqual(counts["SetFloat"],1)
        self.assertNotIn("CustomMethod",counts)
        self.assertEqual(set(counts),WEAK_METHOD_NAMES)

    def test_reject_corrupt_user_string_heap_entries(self):
        x=MockPe(["ok"])
        x.net.user_strings.items[0]=None
        with self.assertRaisesRegex(ValueError,"NOT_TEXT"):
            literal_heap_values(x)
        y=MockPe(["ok"])
        y.net.user_strings.size=0
        with self.assertRaisesRegex(ValueError,"HEAP_UNBOUNDED"):
            literal_heap_values(y)
