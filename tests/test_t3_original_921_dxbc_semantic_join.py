"""Synthetic DXBC-container signature tests: no proprietary shader fixtures."""
import json
import struct
import unittest

from scripts import t3_original_921_dxbc_semantic_join as t3


SECRET = "PRIVATE_ORIGINAL_SEMANTIC_LABEL"
BASE = {"semantic": "TEXCOORD", "index": 0, "system": 0,
        "type": 3, "register": 0, "mask": 15, "rw": 15}


def sig(tag, rows):
    width = t3.SUPPORTED[tag]
    names = bytearray()
    packed = bytearray()
    offset = 8 + len(rows) * width
    for row in rows:
        r = {**BASE, **row}
        name = r["semantic"].encode("ascii") + b"\0"
        mask_word = (r["mask"] | (r["rw"] << 8))
        fields = [offset + len(names), r["index"], r["system"], r["type"],
                  r["register"], mask_word]
        if width >= 28:
            fields.insert(0, r.get("stream", 0))
        if width == 32:
            fields.append(r.get("precision", 0))
        packed.extend(struct.pack("<" + "I" * len(fields), *fields))
        names.extend(name)
    return struct.pack("<II", len(rows), 8) + bytes(packed) + names


def container(sections):
    table_len = 32 + 4 * len(sections)
    data = bytearray(b"DXBC" + b"\0" * 16 + struct.pack("<III", 1, 0, len(sections)))
    offsets = []
    buf = bytearray()
    for tag, payload in sections:
        while (table_len + len(buf)) % 4:
            buf.extend(b"\0")
        offsets.append(table_len + len(buf))
        buf.extend(tag + struct.pack("<I", len(payload)) + payload)
    data.extend(b"".join(struct.pack("<I", n) for n in offsets))
    data.extend(buf)
    struct.pack_into("<I", data, 24, len(data))
    return bytes(data)


def stage(input_tag=b"ISGN", output_tag=b"OSGN",
          inputs=None, outputs=None):
    return container([
        (input_tag, sig(input_tag, [] if inputs is None else inputs)),
        (output_tag, sig(output_tag, [] if outputs is None else outputs)),
        (b"SHDR", b"\0" * 8)
    ])


class DXBCPrivateSemanticTests(unittest.TestCase):
    def test_three_signature_layout_families_real_offsets(self):
        for input_tag, output_tag in [
            (b"ISGN", b"OSGN"), (b"ISG1", b"OSG1"),
            (b"ISG1", b"OSG5")]:
            with self.subTest(input_tag=input_tag, output_tag=output_tag):
                src = stage(input_tag, output_tag, [BASE], [BASE])
                parsed = t3.read_original_dxbc_signatures(src)
                self.assertEqual(parsed["input"][0]["semantic"], "TEXCOORD")
                self.assertEqual(parsed["output"][0]["mask"], 15)
                self.assertEqual(parsed["output_tag"], output_tag.decode())

    def test_exact_private_semantic_link(self):
        v = t3.read_original_dxbc_signatures(stage(outputs=[BASE]))
        f = t3.read_original_dxbc_signatures(stage(inputs=[BASE]))
        result = t3.compare_original_vf(v, f)
        self.assertEqual(result["original_matched_semantic_records"], 1)
        self.assertEqual(result["original_unmatched_fragment_semantic_records"], 0)
        self.assertEqual(result["original_matched_semantic_missing_output_component_lanes"], 0)

    def test_semantic_case_is_ascii_normalized_privately(self):
        v = t3.read_original_dxbc_signatures(stage(outputs=[{**BASE, "semantic": "TeXcOoRd"}]))
        f = t3.read_original_dxbc_signatures(stage(inputs=[BASE]))
        self.assertEqual(t3.compare_original_vf(v, f)["original_matched_semantic_records"], 1)

    def test_mismatching_semantic_index_is_not_a_match(self):
        v = t3.read_original_dxbc_signatures(stage(outputs=[BASE]))
        f = t3.read_original_dxbc_signatures(stage(inputs=[{**BASE, "index": 1}]))
        self.assertEqual(t3.compare_original_vf(v, f)["original_unmatched_fragment_semantic_records"], 1)

    def test_partial_mask_deficit_counts_missing_lanes(self):
        v = t3.read_original_dxbc_signatures(stage(outputs=[{**BASE, "mask": 3}]))
        f = t3.read_original_dxbc_signatures(stage(inputs=[BASE]))
        self.assertEqual(t3.compare_original_vf(v, f)["original_matched_semantic_missing_output_component_lanes"], 2)

    def test_semantic_exists_but_component_type_differs(self):
        v = t3.read_original_dxbc_signatures(stage(outputs=[{**BASE, "type": 2}]))
        f = t3.read_original_dxbc_signatures(stage(inputs=[BASE]))
        self.assertEqual(t3.compare_original_vf(v, f)["original_matched_semantic_type_mismatches"], 1)

    def test_distinct_semantics_in_same_register_nonoverlap_allowed(self):
        v = t3.read_original_dxbc_signatures(stage(outputs=[
            {**BASE, "mask": 3}, {**BASE, "semantic": "COLOR", "mask": 12}]))
        f = t3.read_original_dxbc_signatures(stage(inputs=[{**BASE, "mask": 3}]))
        r = t3.compare_original_vf(v, f)
        self.assertEqual(r["original_unused_vertex_semantic_records"], 1)
        self.assertEqual(r["original_vertex_register_components"], 4)

    def test_overlapping_original_register_components_rejected(self):
        v = t3.read_original_dxbc_signatures(stage(outputs=[
            {**BASE, "mask": 3}, {**BASE, "semantic": "COLOR", "mask": 3}]))
        f = t3.read_original_dxbc_signatures(stage(inputs=[]))
        with self.assertRaisesRegex(ValueError, "overlapping"):
            t3.compare_original_vf(v, f)

    def test_system_value_excluded_from_user_required_semantics(self):
        sys = {**BASE, "semantic": "SV_Position", "system": 1,
               "register": 0xffffffff}
        v = t3.read_original_dxbc_signatures(stage(outputs=[sys]))
        f = t3.read_original_dxbc_signatures(stage(inputs=[sys]))
        out = t3.compare_original_vf(v, f)
        self.assertEqual(out["original_user_fragment_inputs"], 0)
        self.assertEqual(out["original_input_system_value_records"], 1)
        self.assertEqual(out["original_output_system_value_records"], 1)

    def test_original_four_passes_report_only_allowlisted_aggregates(self):
        pairs = [(stage(outputs=[{**BASE, "semantic": SECRET}]),
                  stage(inputs=[{**BASE, "semantic": SECRET}])) for _ in range(4)]
        report = t3.classify_original_fourpass(pairs)
        self.assertEqual(report["status"], "ORIGINAL_921_FOURPASS_DXBC_SEMANTIC_MASK_JOIN_MEASURED")
        self.assertEqual(report["counts"]["original_matched_semantic_records"], 4)
        self.assertEqual(report["counts"]["original_programs_read"], 8)
        blob = json.dumps(report)
        self.assertNotIn(SECRET, blob)
        self.assertNotIn("TEXCOORD", blob)
        self.assertFalse(report["original_to_SPIRV_semantic_Location_mapping_verified"])
        self.assertFalse(report["Unity_Vulkan_Adreno_pixels_verified"])

    def test_untrusted_magic_version_and_declared_length(self):
        for offset, payload in [(0,b"FAKE"), (20,struct.pack("<I", 2)),
                                (24,struct.pack("<I", 4096))]:
            data = bytearray(stage())
            data[offset:offset+len(payload)] = payload
            with self.subTest(offset=offset), self.assertRaisesRegex(ValueError, "header"):
                t3.read_original_dxbc_signatures(bytes(data))

    def test_bad_chunk_pointer_and_overlap_rejected(self):
        data=bytearray(stage())
        struct.pack_into("<I",data,32,len(data)+1)
        with self.assertRaisesRegex(ValueError,"offset"):
            t3.read_original_dxbc_signatures(bytes(data))
        data=bytearray(stage())
        struct.pack_into("<I",data,36,struct.unpack_from("<I",data,32)[0])
        with self.assertRaisesRegex(ValueError,"overlapping"):
            t3.read_original_dxbc_signatures(bytes(data))

    def test_bogus_original_signature_row_count_rejected(self):
        data=bytearray(stage(inputs=[BASE]))
        first_chunk=struct.unpack_from("<I",data,32)[0]
        struct.pack_into("<I",data,first_chunk+8,999)
        with self.assertRaisesRegex(ValueError,"out_of_bounds_original_signature"):
            t3.read_original_dxbc_signatures(bytes(data))

    def test_private_name_offset_bounds_rejected(self):
        data=bytearray(stage(inputs=[BASE]))
        first=struct.unpack_from("<I",data,32)[0]
        struct.pack_into("<I",data,first+8+8,len(data)+500)
        with self.assertRaisesRegex(ValueError,"out_of_bounds_original_signature_semantic"):
            t3.read_original_dxbc_signatures(bytes(data))

    def test_duplicate_semantic_records_rejected(self):
        with self.assertRaisesRegex(ValueError,"duplicate_original_signature_semantic"):
            t3.read_original_dxbc_signatures(stage(inputs=[BASE, BASE]))

    def test_zero_mask_and_mask_high_bits_rejected(self):
        for mask,rw in ((0,0),(16,0),(15,16)):
            with self.subTest(mask=mask,rw=rw),self.assertRaisesRegex(ValueError,"invalid_original_signature_mask"):
                t3.read_original_dxbc_signatures(stage(inputs=[{**BASE, "mask":mask,"rw":rw}]))

    def test_unsupported_stream_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsupported_original_signature_stream"):
            t3.read_original_dxbc_signatures(stage(output_tag=b"OSG5",outputs=[{**BASE,"stream":1}]))

    def test_double_output_chunk_rejected(self):
        data=container([(b"ISGN",sig(b"ISGN",[])),(b"OSGN",sig(b"OSGN",[])),
                        (b"OSG1",sig(b"OSG1",[])),(b"SHDR",b"1234")])
        with self.assertRaisesRegex(ValueError,"missing_or_ambiguous"):
            t3.read_original_dxbc_signatures(data)

    def test_missing_DXBC_bytecode_chunk_rejected(self):
        data=container([(b"ISGN",sig(b"ISGN",[])),(b"OSGN",sig(b"OSGN",[]))])
        with self.assertRaisesRegex(ValueError,"missing_bytecode"):
            t3.read_original_dxbc_signatures(data)

    def test_not_four_compiled_pairs_fails(self):
        with self.assertRaisesRegex(ValueError,"not_exact_four"):
            t3.classify_original_fourpass([(b"DXBC",b"DXBC")])

    def test_no_raw_compiler_data_or_private_exception_text_emitted(self):
        # Public errors only use source-independent category codes.
        try:
            t3.read_original_dxbc_signatures(b"PRIVATE" * 50)
        except ValueError as exc:
            self.assertNotIn("PRIVATE", str(exc))
            self.assertNotIn(SECRET, str(exc))


if __name__ == "__main__":
    unittest.main()
