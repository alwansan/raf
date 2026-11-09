import unittest
from gfxlab.tools.shears_stream_transport import (
    PART_RE, MAX_STREAM_BYTES, MAX_CHUNKS, IMAGE_SEMANTICS
)
class ShearsStreamTransportTests(unittest.TestCase):
    def test_chunk_naming(self):
        self.assertTrue(PART_RE.fullmatch("part-00000"))
        self.assertTrue(PART_RE.fullmatch("part-00025"))
        self.assertFalse(PART_RE.fullmatch("part-0001"))
        self.assertFalse(PART_RE.fullmatch("part-00000.tmp"))
        self.assertFalse(PART_RE.fullmatch("../part-00000"))
    def test_fixed_semantics(self):
        self.assertEqual(IMAGE_SEMANTICS,{"basecolor","normal","metallic"})
    def test_limits(self):
        self.assertLess(MAX_STREAM_BYTES,4_000_000_000)
        self.assertLess(MAX_CHUNKS,100)
if __name__=="__main__":unittest.main()
