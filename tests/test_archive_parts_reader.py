import io
from pathlib import Path
import tempfile
import unittest
import zipfile
from scripts.archive_parts_reader import ArchivePartsReader


class ArchivePartsReaderTests(unittest.TestCase):
    def test_zip_member_and_directory_can_cross_part_boundaries(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            stream = io.BytesIO()
            with zipfile.ZipFile(stream, 'w') as archive:
                archive.writestr('synthetic.rar', b'example-data' * 100)
            data = stream.getvalue()
            parts = []
            for i, start in enumerate(range(0, len(data), 137)):
                path = root / str(i)
                path.write_bytes(data[start:start + 137])
                parts.append(path)
            with ArchivePartsReader(parts) as reader, zipfile.ZipFile(reader) as archive:
                self.assertEqual(archive.read('synthetic.rar'), b'example-data' * 100)

    def test_seek_and_memory_bound(self):
        with tempfile.TemporaryDirectory() as temporary:
            a, b = Path(temporary) / 'a', Path(temporary) / 'b'
            a.write_bytes(b'abc')
            b.write_bytes(b'def')
            with ArchivePartsReader([a, b], max_read=4) as reader:
                self.assertEqual(reader.read(4), b'abcd')
                reader.seek(-3, io.SEEK_END)
                self.assertEqual(reader.read(3), b'def')
                reader.seek(0)
                with self.assertRaises(ValueError):
                    reader.read()
                with self.assertRaises(ValueError):
                    reader.seek(-1)
