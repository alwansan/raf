"""Independent block layout and authentication controls for V10."""
import unittest
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import tempfile
from scripts import gt_imported_bc3_route_pixels as bc3
from scripts import gt_imported_png_route_pixels as png

def block(a0=240,a1=16,c0=0xf800,c1=0x001f):
    # Alpha/RGB selectors vary per row and column, including interpolants.
    alpha=sum(((x+2*y)%8)<<(3*(4*y+x)) for y in range(4) for x in range(4))
    rgb=sum(((x+y)%4)<<(2*(4*y+x)) for y in range(4) for x in range(4))
    return bytes([a0,a1])+alpha.to_bytes(6,"little")+c0.to_bytes(2,"little")+c1.to_bytes(2,"little")+rgb.to_bytes(4,"little")

def tree(w=5,h=7):
    sizes=tuple(bc3.mip_bytes(w,h,n) for n in range(2))
    raw=(block()+block(0,200,0x07e0,0xffff))*4
    return dict(m_Width=w,m_Height=h,m_TextureFormat=12,m_MipCount=2,m_ImageCount=1,
        m_TextureDimension=2,m_CompleteImageSize=sum(sizes),m_LightmapFormat=0,
        m_MipsStripped=0,m_PlatformBlob=[],**{"image data":list(raw[:sum(sizes)])},
        m_StreamData=dict(path="",offset=0,size=0))

class BC3(unittest.TestCase):
    def test_npot_and_tiny_mips(self):
        self.assertEqual(bc3.descriptor(tree())[1],(64,16))
        self.assertEqual(bc3.descriptor(tree(4,4))[1],(16,16))
        self.assertEqual(bc3.source_request(tree()).size,(5,7))
    def test_independent_orientation(self):
        im=bc3.decode_top((4,4),block())
        # Stored first pixel uses endpoint red/240; it lands on final row.
        self.assertEqual(im.getpixel((0,3)),(255,0,0,240))
        self.assertEqual(im.getpixel((1,3)),(0,0,255,16))
        self.assertNotEqual(im.getpixel((0,0)),im.getpixel((0,3)))
    def test_alpha_six_mode(self):
        im=bc3.decode_top((4,4),block(0,200))
        self.assertEqual(im.getpixel((0,3)),(255,0,0,0))
        self.assertEqual(im.getpixel((1,3)),(0,0,255,200))
        self.assertIn(255,[p[3] for p in im.getdata()])
    def test_lower_mip_not_claimed(self):
        t=tree();p=bc3.source_request(t);t["image data"][-1]^=1
        self.assertEqual(p,bc3.source_request(t))
    def test_invalid_layouts(self):
        for field,value in (("m_TextureFormat",4),("m_TextureFormat",29),("m_LightmapFormat",3),
                            ("m_PlatformBlob",[1]),("m_ImageCount",2),("m_TextureDimension",3),
                            ("m_MipsStripped",1),("m_MipCount",0),("m_CompleteImageSize",79),
                            ("m_Width",True)):
            with self.subTest(field=field,value=value):
                t=tree();t[field]=value
                with self.assertRaises(png.Unproven):bc3.source_request(t)
    def test_stream_authentication(self):
        t=tree();raw=bytes(t["image data"]);inline=bc3.source_request(t);t["image data"]=[]
        t["m_StreamData"]=dict(path="test.resS",offset=5,size=len(raw))
        req=bc3.source_request(t)
        payload=b"guard"+raw+b"end"
        pins={"Raft_Data/test.resS":("plain",len(payload),sha256(payload).hexdigest())}
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/"test.resS";p.write_bytes(payload)
            out=bc3.resolve_requests(root,pins,{"a":req,"b":replace(req,offset=100)})
            self.assertEqual(out["a"],replace(inline,from_stream=True))
            self.assertEqual(out["b"],"bc3_stream_extent_out_of_bounds")
            self.assertEqual(bc3.resolve_requests(root,{},{"a":req})["a"],"bc3_stream_provider_not_pinned")
            p.write_bytes(b"G"+payload[1:])
            self.assertEqual(bc3.resolve_requests(root,pins,{"a":req})["a"],"bc3_stream_provider_SHA_mismatch")
    def test_ambiguous_or_aliased_stream(self):
        t=tree();t["m_StreamData"]=dict(path="test.resS",offset=0,size=80)
        with self.assertRaisesRegex(png.Unproven,"ambiguous"):bc3.source_request(t)
        t["image data"]=[];t["m_StreamData"]["path"]="archive:/test.resS"
        with self.assertRaisesRegex(png.Unproven,"provider"):bc3.source_request(t)
    def test_no_v8_source_promotion(self):
        self.assertIs(type(bc3.source_request(tree())),bc3.Proof)
        self.assertIsInstance(png.safe_request(tree()),str)
