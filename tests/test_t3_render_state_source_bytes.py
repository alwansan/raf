"""Private byte-provenance checks for T3 render-state pair gate."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from scripts.t3_render_state_pair_identity import pair, pair_verified

STATES = dict(blend_src='One', blend_dst='Zero', blend_op='Add',
              zwrite=True, ztest='LEqual', cull='Back', color_mask=15,
              alpha_clip=False, render_queue=2000)

def record(data):
    return dict(material_guid='a'*32, shader_guid='b'*32, pass_index=0,
                source_sha256=hashlib.sha256(data).hexdigest(), states=dict(STATES))

class SourceByteVerification(unittest.TestCase):
    def test_valid_private_bytes_are_verified(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=Path(d)/'original.bin',Path(d)/'exported.bin'
            a.write_bytes(b'private original'); b.write_bytes(b'private export')
            result=pair_verified(record(a.read_bytes()),record(b.read_bytes()),a,b)
            self.assertEqual(result['status'],'MATCH')
            self.assertTrue(result['source_digests_content_verified'])
            self.assertFalse(result['device_fix_proven'])

    def test_tampered_original_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=Path(d)/'original.bin',Path(d)/'exported.bin'
            a.write_bytes(b'changed'); b.write_bytes(b'export')
            with self.assertRaisesRegex(ValueError,'source_digest_mismatch'):
                pair_verified(record(b'original'),record(b'export'),a,b)

    def test_tampered_export_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=Path(d)/'original.bin',Path(d)/'exported.bin'
            a.write_bytes(b'original'); b.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'source_digest_mismatch'):
                pair_verified(record(b'original'),record(b'export'),a,b)

    def test_legacy_format_only_is_explicit(self):
        self.assertFalse(pair(record(b'original'),record(b'export'))['source_digests_content_verified'])

if __name__ == '__main__':
    unittest.main()
