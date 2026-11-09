"""Source-free tests for T3 PNG capture audit."""
import importlib.util
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

SCRIPT=Path(__file__).resolve().parents[1]/"scripts"/"t3_cl_png_pixel_audit.py"
spec=importlib.util.spec_from_file_location("t3_png_audit",SCRIPT)
audit_module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_module)

def chunk(kind,data):
    return struct.pack(">I",len(data))+kind+data+struct.pack(">I",zlib.crc32(kind+data)&0xffffffff)

def png(width,height,fn,filter_type=0):
    previous=bytearray(width*3)
    scan=bytearray()
    for y in range(height):
        actual=bytearray(v for x in range(width) for v in fn(x,y))
        row=bytearray(actual)
        if filter_type==1:
            for i in range(len(row)): row[i]=(actual[i]-(actual[i-3] if i>=3 else 0))&255
        elif filter_type==2:
            for i in range(len(row)): row[i]=(actual[i]-previous[i])&255
        scan.append(filter_type)
        scan.extend(row)
        previous=actual
    ihdr=struct.pack(">IIBBBBB",width,height,8,2,0,0,0)
    return audit_module.SIGNATURE+chunk(b"IHDR",ihdr)+chunk(b"IDAT",zlib.compress(scan))+chunk(b"IEND",b"")

class PngAuditTests(unittest.TestCase):
    def check(self,content):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"capture.png"
            path.write_bytes(content)
            return audit_module.audit(path)
    def test_black_capture(self):
        result=self.check(png(8,8,lambda x,y:(0,0,0)))
        self.assertEqual(result["regions"]["full"]["black_fraction"],1)
        self.assertEqual(result["regions"]["center"]["unique_rgb"],1)
    def test_color_diversity(self):
        result=self.check(png(8,8,lambda x,y:(255,0,0) if x<4 else (0,0,255)))
        self.assertEqual(result["regions"]["full"]["unique_rgb"],2)
        self.assertEqual(result["regions"]["full"]["black_fraction"],0)
    def test_sub_and_up_filters(self):
        for filt in (1,2):
            with self.subTest(filt=filt):
                result=self.check(png(8,8,lambda x,y:(x*10,y*10,80),filt))
                self.assertEqual(result["regions"]["full"]["unique_rgb"],64)
    def test_inflate_overrun_rejected(self):
        # Valid CRC, valid IEND, but inflated data exceeds IHDR dimensions.
        ihdr=struct.pack(">IIBBBBB",2,2,8,2,0,0,0)
        oversized=b"\x00"*10000
        payload=(audit_module.SIGNATURE+chunk(b"IHDR",ihdr)
                 +chunk(b"IDAT",zlib.compress(oversized))+chunk(b"IEND",b""))
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"oversized.png"
            path.write_bytes(payload)
            with self.assertRaisesRegex(ValueError,"invalid_scanline_size"):
                audit_module.audit(path)
    def test_trailing_zlib_stream_rejected(self):
        ihdr=struct.pack(">IIBBBBB",2,2,8,2,0,0,0)
        scan=b"\x00"+b"\x00"*6
        scan*=2
        payload=(audit_module.SIGNATURE+chunk(b"IHDR",ihdr)
                 +chunk(b"IDAT",zlib.compress(scan)+b"extra")
                 +chunk(b"IEND",b""))
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"trailing.png"
            path.write_bytes(payload)
            with self.assertRaisesRegex(ValueError,"invalid_scanline_size"):
                audit_module.audit(path)
    def test_crc_failure(self):
        bad=bytearray(png(8,8,lambda x,y:(0,0,0)))
        bad[-5]^=1
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"bad.png"
            path.write_bytes(bad)
            with self.assertRaisesRegex(ValueError,"bad_crc"):
                audit_module.audit(path)
    def test_truncated(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"bad.png"
            path.write_bytes(png(8,8,lambda x,y:(0,0,0))[:-6])
            with self.assertRaises(ValueError):
                audit_module.audit(path)

if __name__=="__main__":
    unittest.main()
