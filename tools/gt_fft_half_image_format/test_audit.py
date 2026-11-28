import unittest
import struct
from tools.gt_fft_half_image_format import audit as a
class ImageFormatTests(unittest.TestCase):
    @staticmethod
    def module(fmt,extended=False):
        w=[0x07230203,0x10000,14<<16,16,0,(2<<16)|17,1]
        if extended:w += [(2<<16)|17,49]
        # Minimal syntactic OpTypeImage contract, not a valid executable.
        w += [(9<<16)|25,3,2,1,2,0,0,2,fmt]
        return struct.pack("<"+"I"*len(w),*w)
    def test_one_word_only(self):
        for fmt,old,new,ext in (("RGHalf",6,7,True),("ARGBHalf",1,2,False)):
            raw=self.module(old,ext);out,index=a.patch_image_format(raw,fmt)
            self.assertEqual(len(raw),len(out))
            before=struct.unpack("<"+"I"*(len(raw)//4),raw)
            after=struct.unpack("<"+"I"*(len(out)//4),out)
            self.assertEqual([i for i,(x,y) in enumerate(zip(before,after)) if x!=y],[index])
            self.assertEqual((before[index],after[index]),(old,new))
    def test_reject_wrong_or_missing_cap(self):
        with self.assertRaises(ValueError):a.patch_image_format(self.module(1),"RGHalf")
        with self.assertRaises(ValueError):a.patch_image_format(self.module(6),"RGHalf")
        with self.assertRaises(ValueError):a.patch_image_format(self.module(1)[:-4],"ARGBHalf")
    def test_pins(self):
        for fmt in a.FORMATS:
            self.assertEqual(set(a.PINS[fmt]),set(a.live.LABELS)-{"control"})
            self.assertEqual(len(set(a.PINS[fmt].values())),8)
if __name__=="__main__":unittest.main()
