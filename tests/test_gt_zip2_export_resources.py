"""GT true ZIP2 -> AssetRipper input resource restoration regression tests."""
from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from scripts.gt_zip2_export_resources import CORE, choose, restore
from scripts.gt_zip2_payloads import SourceFailure


def git(root, *args):
    return subprocess.check_output(["git","-C",str(root),*args],text=True).strip()


def fixture(base, payloads):
    root=base/"zip2"
    root.mkdir()
    git(root,"init","-q")
    lines=["kind\tbytes\tsha256\tmode\trelative_path_under_Raft"]
    for name,(kind,raw) in payloads.items():
        digest=hashlib.sha256(raw).hexdigest()
        lines.append(f"{kind}\t{len(raw)}\t{digest}\t660\t{name}")
        p=root/"Raft"/name
        if kind=="split":
            p.mkdir(parents=True)
            for i,start in enumerate(range(0,len(raw),3)):
                (p/f"part-{i:05d}").write_bytes(raw[start:start+3])
            (p/"README.txt").write_text("original split test\n")
        else:
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(raw)
    (root/"RAFT_FILE_MANIFEST.tsv").write_text("\n".join(lines)+"\n")
    git(root,"add",".")
    subprocess.run(["git","-C",str(root),"-c","user.name=GT",
        "-c","user.email=gt@example.invalid","commit","-q","-m","fixture"],check=True)
    return root,git(root,"rev-parse","HEAD"),git(root,"hash-object",str(root/"RAFT_FILE_MANIFEST.tsv"))


def ptr(raw):
    return b"version https://git-lfs.github.com/spec/v1\noid sha256:"+hashlib.sha256(raw).hexdigest().encode()+b"\nsize "+str(len(raw)).encode()+b"\n"


class RestoreIntoInputTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.base=Path(self.temp.name)
        self.data={"Raft_Data/resources.assets":("split",b"RESOURCE") ,
                   "Raft_Data/resources.assets.resS":("split",b"STREAM12345")}
        self.source,self.commit,self.blob=fixture(self.base,self.data)
        self.destination=self.base/"input"/"Raft_Data"

    def tearDown(self):
        self.temp.cleanup()

    def run_restore(self, **kw):
        with mock.patch("scripts.gt_zip2_payloads.PART_SIZE", 3):
            return restore(self.source,self.destination,
                profile="selected",selected=list(self.data),
                expected_commit=self.commit,expected_blob=self.blob,
                min_free_reserve=kw.pop("min_free_reserve",0),**kw)

    def test_real_stream_content_in_export_input(self):
        result=self.run_restore()
        self.assertEqual(result["original_resources_verified"],2)
        self.assertEqual(result["files_newly_materialized"],2)
        self.assertTrue(result["assetripper_input_ready_for_selected_scope"])
        self.assertFalse(result["git_lfs_used"])
        for name,(_,raw) in self.data.items():
            p=self.destination/name.split("/")[-1]
            self.assertEqual(p.read_bytes(),raw)
            self.assertEqual(p.stat().st_nlink,1)

    def test_second_run_reuses_verified_originals(self):
        self.run_restore()
        result=self.run_restore()
        self.assertEqual(result["files_verified_and_reused"],2)
        self.assertEqual(result["files_newly_materialized"],0)

    def test_replaces_only_matching_pointer_not_other_files(self):
        p=self.destination/"resources.assets"
        p.parent.mkdir(parents=True)
        p.write_bytes(ptr(b"RESOURCE"))
        marker=self.destination/"other.meta"
        marker.write_text("guid: preserved")
        result=self.run_restore()
        self.assertEqual(result["original_placeholder_pointers_replaced"],1)
        self.assertEqual(p.read_bytes(),b"RESOURCE")
        self.assertEqual(marker.read_text(),"guid: preserved")

    def test_refuses_overwriting_modified_original(self):
        p=self.destination/"resources.assets"
        p.parent.mkdir(parents=True)
        p.write_bytes(b"ALTERED!")
        with self.assertRaisesRegex(SourceFailure,"refuse_overwrite_nonoriginal"):
            self.run_restore()
        self.assertEqual(p.read_bytes(),b"ALTERED!")
        self.assertFalse((self.destination/"resources.assets.resS").exists())

    def test_bad_second_split_is_not_partially_published(self):
        with mock.patch("scripts.gt_zip2_payloads.PART_SIZE",3):
            (self.source/"Raft"/"Raft_Data/resources.assets.resS"/"part-00001").write_bytes(b"BAD")
            with self.assertRaisesRegex(SourceFailure,"sha256_or_size"):
                restore(self.source,self.destination,profile="selected",
                    selected=list(self.data),expected_commit=self.commit,
                    expected_blob=self.blob,min_free_reserve=0)
        self.assertFalse((self.destination/"resources.assets").exists())
        self.assertFalse((self.destination/"resources.assets.resS").exists())

    def test_wrong_zip2_commit_rejected(self):
        with self.assertRaisesRegex(SourceFailure,"pinned_commit"):
            restore(self.source,self.destination,profile="selected",
                selected=list(self.data),expected_commit="0"*40,
                expected_blob=self.blob,min_free_reserve=0)

    def test_insufficient_disk_and_budget_fail_before_writes(self):
        with self.assertRaisesRegex(SourceFailure,"exceeds_budget"):
            self.run_restore(budget=10)
        self.assertFalse(self.destination.exists())
        with self.assertRaisesRegex(SourceFailure,"insufficient_space"):
            self.run_restore(min_free_reserve=10**16)
        self.assertFalse(self.destination.exists())

    def test_unlisted_payload_or_duplicate_rejected(self):
        records={name:(kind,len(raw),hashlib.sha256(raw).hexdigest())
                 for name,(kind,raw) in self.data.items()}
        for selected in (["Raft_Data/malicious.exe"],["Raft_Data/resources.assets"]*2):
            with self.subTest(selected=selected),self.assertRaises(SourceFailure):
                choose(records,"selected",selected)

    def test_core_profile_needs_all_five_manifest_records(self):
        records={name:("plain",1,"0"*64) for name in CORE}
        self.assertEqual(choose(records,"core"),list(CORE))
        del records["Raft_Data/resources.assets.resS"]
        with self.assertRaisesRegex(SourceFailure,"missing_from_manifest"):
            choose(records,"core")

    def test_full_profile_requires_all_82_owners_48_streams_and_engine(self):
        from scripts.gt_stage_serialized_owners import OWNERS
        records={"Raft_Data/"+name:("plain",1,"0"*64) for name in OWNERS}
        records.update({"Raft_Data/level"+str(i)+".resS":("plain",1,"0"*64)
                        for i in range(40)})
        records.update({"Raft_Data/sharedassets"+str(i)+".assets.resS":("plain",1,"0"*64)
                        for i in range(8)})
        from scripts.gt_zip2_export_resources import ENGINE_FILES
        records.update({name:("plain",1,"0"*64) for name in ENGINE_FILES})
        self.assertEqual(len(choose(records,"full")),132)
        del records["Raft_Data/level0.resS"]
        with self.assertRaisesRegex(SourceFailure,"unexpected_full_graphics"):
            choose(records,"full")


if __name__ == "__main__":
    unittest.main()
