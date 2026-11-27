"""Independent analytic V11 source regressions."""
import unittest
import math
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import tempfile
from scripts import gt_imported_dxt5nm_route_pixels as nm
from scripts import gt_imported_bc3_route_pixels as bc3
from scripts import gt_imported_png_route_pixels as png
from test_gt_imported_bc3_route_pixels import block,tree

def normal_tree():
    return dict(tree(),m_LightmapFormat=3,m_ColorSpace=0)

class NormalMap(unittest.TestCase):
    def test_channel_order_and_clamp(self):
        packed,normal=nm.decode_top((4,4),block())
        self.assertEqual(packed.getpixel((0,3)),(255,0,0,240))
        self.assertEqual(normal.getpixel((0,3)),(240,0,127,255))
        self.assertEqual(normal.getpixel((1,3)),(16,0,127,0))
        self.assertNotEqual(normal.getpixel((0,0)),normal.getpixel((0,3)))
    def test_independent_integer_oracle(self):
        packed,normal=nm.decode_top((4,4),block(100,150,0x07e0,0x8410))
        expected=[(a,g,(math.isqrt(max(0,255**2-(2*a-255)**2-(2*g-255)**2))+255)//2,r) for r,g,b,a in packed.getdata()]
        self.assertEqual(list(normal.getdata()),expected)
        self.assertTrue(any(p[2]>127 for p in expected))
    def test_scope_and_invalid_usage(self):
        t=normal_tree()
        self.assertIs(type(nm.source_request(t)),nm.Proof)
        self.assertIsInstance(bc3.safe_request(t),str)
        self.assertIsInstance(png.safe_request(t),str)
        for k,v in (("m_LightmapFormat",0),("m_LightmapFormat",True),("m_ColorSpace",1),("m_ColorSpace",False),("m_TextureFormat",4)):
            with self.subTest(k=k,v=v):self.assertIsInstance(nm.safe_request(dict(t,**{k:v})),str)
        self.assertIsInstance(nm.safe_request({k:v for k,v in t.items() if k!="m_ColorSpace"}),str)
    def test_stream_pin_and_lower_scope(self):
        t=normal_tree();inline=nm.source_request(t);raw=bytes(t["image data"]);t["image data"]=[]
        t["m_StreamData"]=dict(path="test.resS",offset=2,size=len(raw))
        req=nm.source_request(t)
        self.assertIs(type(req),nm.Request)
        payload=b"xx"+raw+b"yy"
        pins={"Raft_Data/test.resS":("plain",len(payload),sha256(payload).hexdigest())}
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"test.resS";p.write_bytes(payload)
            self.assertEqual(nm.resolve_requests(Path(tmp),pins,{"a":req})["a"],replace(inline,from_stream=True))
            p.write_bytes(b"XY"+payload[2:])
            self.assertEqual(nm.resolve_requests(Path(tmp),pins,{"a":req})["a"],"bc3_stream_provider_SHA_mismatch")
        t=normal_tree();t["image data"][-1]^=1
        self.assertEqual(nm.source_request(t),inline)
