"""BC3 four-color canonicalization invariants, independent Pillow DDS oracle."""
from random import Random
import unittest
from unittest.mock import patch
from scripts import gt_patch_bc3_export_decoder as fix
from scripts.gt_compare_original_bc3_to_flipbook_pixels import dds_bc3

def canonical(block):
    # Independent reference transformation, not the production C# routine.
    c0=int.from_bytes(block[8:10],"little");c1=int.from_bytes(block[10:12],"little")
    if c0==c1:return block[:12]+bytes(4)
    if c0>c1:return block
    return block[:8]+block[10:12]+block[8:10]+bytes(b^0x55 for b in block[12:])

class BC3Repair(unittest.TestCase):
    def test_reject_unpinned(self):
        with self.assertRaisesRegex(ValueError,"pinned_BC3"):
            fix.repair(b"not pinned")
    def test_exact_scope_and_no_double_patch(self):
        raw=fix.METHOD_ANCHOR+b"\n"+fix.ANCHOR+b"\nDXT1 unchanged\nDXT3 unchanged"
        with patch.object(fix,"PIN",fix.git_blob(raw)):
            out=fix.repair(raw)
            self.assertIn(b"RaftNormalizeBC3ColorBlocks(inputSpan",out)
            self.assertIn(b"case TextureFormat.DXT5Crunched:\n\t\t\t\tDxtDecoder.DecompressDXT5<TColor, TChannelValue>(inputSpan",out)
            self.assertTrue(out.endswith(b"DXT1 unchanged\nDXT3 unchanged"))
            with self.assertRaises(ValueError):fix.repair(out)
    def test_ambiguous_anchor_refused(self):
        raw=fix.METHOD_ANCHOR+fix.ANCHOR*2
        with patch.object(fix,"PIN",fix.git_blob(raw)):
            with self.assertRaisesRegex(ValueError,"ambiguous"):fix.repair(raw)
    def test_four_color_equivalence_many_endpoints(self):
        r=Random(20261127)
        for i in range(256):
            c0,c1=r.randrange(65536),r.randrange(65536)
            if i%8==0:c1=c0
            a=bytes([0,200] if i%2 else [240,16])+r.randbytes(6)
            block=a+c0.to_bytes(2,"little")+c1.to_bytes(2,"little")+bytes([0xe4,0x39,0x4e,0x93])
            changed=canonical(block)
            self.assertEqual(changed[:8],a)
            self.assertEqual(dds_bc3(block,4,4).tobytes(),dds_bc3(changed,4,4).tobytes())
    def test_explicit_equal_and_unchanged(self):
        b=bytes(8)+bytes.fromhex("e007e007ffffffff")
        self.assertEqual(canonical(b),b[:12]+bytes(4))
        b=bytes(8)+bytes.fromhex("00f81f00e4394e93")
        self.assertEqual(canonical(b),b)
