"""Focused counterfactuals for the new byte edge; no original or Unity inputs."""
import copy
import struct
import unittest

from scripts.gt_next23b_route_provenance import derive_source_contract
from tools.gt_next23b_source_program_admission.audit import verify, canonical, digest
from test_gt_next23b_route_provenance import fixture


def dxbc(stage, i):
    # Structural parser-only authored container; not executable shader proof.
    payload = struct.pack("<II", (stage << 16) | 0x50, i)
    chunk = b"SHEX" + struct.pack("<I", len(payload)) + payload
    return b"DXBC" + bytes(16) + struct.pack("<IIII", 1, 36 + len(chunk), 1, 36) + chunk


def authored():
    source, _ = fixture()
    source.update(source_owner="AUTHORED.assets", source_PathID=-7)
    identity = dict(source_commit="a"*40, owner="AUTHORED.assets", owner_sha256="b"*64,
                    object_sha256="c"*64, class_id=48, path_id=-7, platform_code=4)
    files, entries, directory = {}, [], []
    segment = bytearray(b"segment-prefix")
    for i in range(134):
        code = dxbc(1 if i < 67 else 0, i)
        files[f"program-{i:03d}"] = code
        entry = b"prefix" + code + b"suffix"
        directory.append(struct.pack("<III", len(segment), len(entry), 1))
        segment.extend(entry)
        entries.append(entry)
    for pair in source["paired"]:
        for lane in ("vs", "fs"):
            row = pair[lane]
            meta = row["original_variant_metadata"]
            i = meta["m_BlobIndex"]
            row["original_D3D11_link"] = dict(blob_index=i, segment_index=1,
                metadata_sha256=digest(canonical(meta)), entry_sha256=digest(entries[i]))
    segments = (struct.pack("<I", len(entries)) + b"".join(directory), bytes(segment))
    parsed = copy.deepcopy(source["original_shader_ParsedForm_full_private"])
    return source, identity, parsed, segments, files


class SourceByteAdmission(unittest.TestCase):
    def setUp(self):
        self.source, self.identity, self.parsed, self.segments, self.files = authored()

    def audit(self):
        return verify(self.source, identity=self.identity, parsed=self.parsed,
                      segments=self.segments, program_files=self.files)

    def test_byte_edge_complete_and_private(self):
        private, report = self.audit()
        self.assertEqual(report["stage_slots_byte_joined"], 2312)
        self.assertEqual(report["distinct_stage_programs_byte_joined"], 134)
        self.assertEqual(report["distinct_blob_stage_links"], 134)
        self.assertEqual(len(private["slots"]), 2312)
        self.assertTrue(all(r["dxbc_offset_in_entry"] == 6 and r["segment_index"] == 1
                            for r in private["slots"]))
        self.assertFalse(report["compiled_route_program_identity_verified"])
        self.assertFalse(report["owner_and_object_bytes_authenticated_by_this_tool"])
        self.assertFalse(report["production_install_allowed"])
        self.assertNotIn("AUTHORED", str(report))

    def test_old_gate_accepts_same_stage_reference_swap_new_rejects(self):
        old = derive_source_contract(self.source)
        a,b = (r["vs"] for r in self.source["paired"][:2])
        a["program_ref"],b["program_ref"] = b["program_ref"],a["program_ref"]
        self.assertEqual(old, derive_source_contract(self.source))
        with self.assertRaisesRegex(ValueError, "program_ref_dxbc_bytes_mismatch"):
            self.audit()

    def test_old_gate_accepts_forged_original_link_new_rejects(self):
        old = derive_source_contract(self.source)
        self.source["paired"][0]["vs"]["original_D3D11_link"]["entry_sha256"] = "0"*64
        self.assertEqual(old, derive_source_contract(self.source))
        with self.assertRaisesRegex(ValueError, "packet_entry_link_mismatch"):
            self.audit()

    def test_same_length_file_replacement(self):
        self.files["program-000"] = self.files["program-001"]
        with self.assertRaisesRegex(ValueError, "program_ref_dxbc_bytes_mismatch"):
            self.audit()

    def test_changed_entry_even_with_unchanged_dxbc(self):
        seg = bytearray(self.segments[1])
        seg[len(b"segment-prefix")] ^= 1
        self.segments = (self.segments[0], bytes(seg))
        with self.assertRaisesRegex(ValueError, "packet_entry_link_mismatch"):
            self.audit()

    def test_independent_identity_and_parsed_form_not_copied_from_packet(self):
        self.identity["path_id"] = -8
        with self.assertRaisesRegex(ValueError, "source_owner_pathid_mismatch"):
            self.audit()
        self.identity["path_id"] = -7
        self.parsed["m_KeywordFlags"][0] = 99
        with self.assertRaisesRegex(ValueError, "independent_parsed_form_mismatch"):
            self.audit()

    def test_out_of_range_entry_rejects(self):
        t = bytearray(self.segments[0])
        struct.pack_into("<I", t, 4, len(self.segments[1]))
        self.segments = (bytes(t), self.segments[1])
        with self.assertRaisesRegex(ValueError, "invalid_entry_range"):
            self.audit()

    def test_labels_can_change_when_actual_program_bytes_follow(self):
        # Program ordinals are labels, not m_BlobIndex. Relabeling bijectively
        # is valid only if every slot and actual file is consistently relabeled.
        a,b = "program-000","program-001"
        self.files[a],self.files[b] = self.files[b],self.files[a]
        for pair in self.source["paired"]:
            r=pair["vs"]
            if r["program_ref"] in (a,b):
                r["program_ref"] = b if r["program_ref"] == a else a
        _, report = self.audit()
        self.assertEqual(report["distinct_stage_programs_byte_joined"],134)


if __name__ == "__main__":
    unittest.main()
