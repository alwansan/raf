import hashlib
from pathlib import Path
import tempfile
import unittest

from scripts.b03_verify_archive_payload import IntakeError, intake, manifest_record, safe_relative


class ArchiveIntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.root = root
        self.source = root / "download.bin"
        self.manifest = root / "RAFT_FILE_MANIFEST.tsv"
        self.stage = root / "stage"
        self.stage.mkdir()
        self.payload = (b"original\x00binary\xff\r\n--not-a-transport-boundary\r\n" * 42)
        self.sha = hashlib.sha256(self.payload).hexdigest()
        self.path = "Raft_Data/test.assets"
        self.manifest.write_text("kind\tbytes\tsha256\tmode\trelative_path_under_Raft\n"
                                 f"plain\t{len(self.payload)}\t{self.sha}\t660\t{self.path}\n")

    def encoded(self, payload=None, boundary=b"B03-TestBoundary", header=None, trailer=b"\r\n"):
        if payload is None:
            payload = self.payload
        if header is None:
            header = b'Content-Disposition: form-data; name="file"; filename="raft.bin"\r\nContent-Type: application/octet-stream\r\n'
        return b"--" + boundary + b"\r\n" + header + b"\r\n" + payload + b"\r\n--" + boundary + b"--" + trailer

    def invoke(self, data):
        self.source.write_bytes(data)
        return intake(self.source, self.manifest, self.path, self.stage)

    def assert_bad(self, data):
        self.source.write_bytes(data)
        with self.assertRaises(IntakeError):
            intake(self.source, self.manifest, self.path, self.stage)
        self.assertFalse((self.stage / self.path).exists())
        self.assertEqual(list(self.stage.rglob(".b03-verified-*")), [])

    def test_raw_sha_pinned_and_staged(self):
        got = self.invoke(self.payload)
        self.assertTrue(got["verified"])
        self.assertEqual(got["source_format"], "raw")
        self.assertEqual((self.stage / self.path).read_bytes(), self.payload)

    def test_singlepart_multipart_sha_pinned_and_staged(self):
        got = self.invoke(self.encoded())
        self.assertEqual(got["source_format"], "multipart-single-part")
        self.assertEqual((self.stage / self.path).read_bytes(), self.payload)

    def test_same_size_tampered_payload_refused(self):
        data = bytearray(self.payload)
        data[12] ^= 1
        self.assert_bad(bytes(data))

    def test_wrapped_tampered_payload_refused(self):
        self.assert_bad(self.encoded(payload=b"X" + self.payload[1:]))

    def test_truncated_payload_refused(self):
        self.assert_bad(self.encoded()[:-15])

    def test_epilogue_or_extra_part_refused(self):
        self.assert_bad(self.encoded(trailer=b"\r\nEXTRA"))
        self.assert_bad(self.encoded(trailer=b"\r\n--B03-TestBoundary\r\n"))

    def test_bad_headers_and_boundary_refused(self):
        self.assert_bad(self.encoded(header=b"Content-Type: application/octet-stream\r\n"))
        self.assert_bad(self.encoded(boundary=b"bad\x00boundary"))
        self.assert_bad(self.encoded(header=b'Content-Disposition: form-data; name="file"\r\nContent-Disposition: form-data; name="file"\r\n'))

    def test_bad_size_even_if_envelope_is_well_formed(self):
        self.assert_bad(self.encoded(payload=self.payload + b"inserted"))
        self.assert_bad(self.payload[:-1])

    def test_manifest_traversal_refused(self):
        with self.assertRaises(IntakeError):
            safe_relative("../sneak")
        with self.assertRaises(IntakeError):
            safe_relative("x//y")
        with self.assertRaises(IntakeError):
            safe_relative("C:/absolute")

    def test_duplicate_manifest_refused(self):
        line = self.manifest.read_text().splitlines()[1]
        self.manifest.write_text(self.manifest.read_text() + line + "\n")
        self.assert_bad(self.payload)

    def test_unknown_manifest_record_refused(self):
        with self.assertRaises(IntakeError):
            manifest_record(self.manifest, "no/file")

    def test_input_symlink_refused(self):
        other = self.root / "actual"
        other.write_bytes(self.payload)
        self.source.symlink_to(other)
        with self.assertRaises(IntakeError):
            intake(self.source, self.manifest, self.path, self.stage)

    def test_output_symlink_parent_refused(self):
        target = self.root / "elsewhere"
        target.mkdir()
        (self.stage / "Raft_Data").symlink_to(target, target_is_directory=True)
        self.assert_bad(self.payload)

    def test_refuse_to_overwrite_valid_staged_file(self):
        self.invoke(self.payload)
        self.source.write_bytes(b"invalid")
        with self.assertRaises(IntakeError):
            intake(self.source, self.manifest, self.path, self.stage)
        self.assertEqual((self.stage / self.path).read_bytes(), self.payload)

    def test_input_within_stage_refused(self):
        nested = self.stage / "input.bin"
        nested.write_bytes(self.payload)
        with self.assertRaises(IntakeError):
            intake(nested, self.manifest, self.path, self.stage)


if __name__ == "__main__":
    unittest.main()
