import hashlib
import io
import tempfile
from pathlib import Path
import unittest
from scripts.fetch_verified_mesh_ranges import fetch_range, validate_manifest, fetch, cache_path


class Response(io.BytesIO):
    def __init__(self, raw, status=206, content_range='bytes 2-4/7'):
        super().__init__(raw)
        self.status = status
        self.headers = {'Content-Range': content_range, 'Content-Length': str(len(raw))}
        self.reads = 0

    def read(self, size=-1):
        self.reads += 1
        return super().read(size)


class Opener:
    def __init__(self, response):
        self.response = response
        self.request = None

    def open(self, request, **kwargs):
        self.request = request
        return self.response


class VerifiedMeshRangeTests(unittest.TestCase):
    def chunk(self, raw=b'CDE', offset=2):
        return {'offset': offset, 'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

    def test_valid_http_range_is_hashed_and_github_token_is_not_forwarded(self):
        opener = Opener(Response(b'CDE'))
        raw = fetch_range({'href': 'https://example.invalid/object'}, {'size': 7}, self.chunk(), opener)
        self.assertEqual(raw, b'CDE')
        self.assertEqual(opener.request.get_header('Range'), 'bytes=2-4')
        self.assertIsNone(opener.request.get_header('Authorization'))

    def test_server_ignoring_range_is_closed_without_reading_whole_body(self):
        response = Response(b'ignored', status=200)
        with self.assertRaisesRegex(ValueError, 'fallback is forbidden'):
            fetch_range({'href': 'https://example.invalid/object'}, {'size': 7}, self.chunk(), Opener(response))
        self.assertEqual(response.reads, 0)

    def test_wrong_content_range_and_wrong_checksum_are_refused(self):
        for response in (Response(b'CDE', content_range='bytes 1-3/7'), Response(b'XYZ')):
            with self.subTest(response=response), self.assertRaises(ValueError):
                fetch_range({'href': 'https://example.invalid/object'}, {'size': 7}, self.chunk(), Opener(response))

    def test_manifest_refuses_overlap_or_unsafe_source_name(self):
        stream = {'size': 7, 'sha256': 'a' * 64, 'chunks': [self.chunk(), self.chunk()]}
        manifest = {'format': 1, 'max_chunk_bytes': 1024, 'streams': {'sharedassets34.assets.resS': stream}}
        with self.assertRaises(ValueError):
            validate_manifest(manifest)
        manifest['streams'] = {'../unsafe.resS': {'size': 7, 'sha256': 'a' * 64, 'chunks': [self.chunk()]}}
        with self.assertRaises(ValueError):
            validate_manifest(manifest)

    def test_verified_full_original_reused_without_network(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, cache = root / 'source', root / 'cache'
            source.mkdir()
            raw = bytes(range(100)) * 3
            name = 'sharedassets34.assets.resS'
            (source / name).write_bytes(raw)
            chunk = self.chunk(raw[13:63], 13)
            manifest = {'format': 1, 'max_chunk_bytes': 1024, 'streams': {name: {
                'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'chunks': [chunk]}}}
            report = fetch(manifest, source, cache, token='')
            self.assertEqual(report['remote_range_bytes'], 0)
            self.assertEqual(cache_path(cache, name, chunk).read_bytes(), raw[13:63])
