"""Authored source payloads and actual UnityPy 1.23.0/Pillow decoder controls.

Serialized object parser is injected with authored metadata, but verified
owner/stream bytes, decoder and PNG comparison run for real.
"""
from hashlib import sha1,sha256
from pathlib import Path
import tempfile
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

from PIL import Image
from UnityPy.enums import TextureFormat, BuildTarget
from scripts import gt_particle108_source_pixel_parity as parity


def pin(raw):
    return len(raw),sha256(raw).hexdigest()


class PixelParityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.data=self.root/"Raft_Data"
        self.data.mkdir()
        self.owner="authored.assets"
        self.key=(self.owner,28)
        self.owner_bytes=b"authored serialized owner fixture only"
        self.owner_file=self.data/self.owner
        self.owner_file.write_bytes(self.owner_bytes)
        # Unity texture storage bottom row first. Fixed flip to top-left.
        self.bottom=bytes([0,0,0,0, 80,70,60,128])
        self.top=bytes([1,2,3,255, 90,100,110,64])
        self.payload=self.bottom+self.top
        self.provider=b"guard"+self.payload+b"trailer"
        self.provider_file=self.data/"authored.assets.resS"
        self.provider_file.write_bytes(self.provider)
        self.manifest=self.root/"manifest.tsv"
        self.manifest_bytes=("kind\tbytes\tsha256\tmode\trelative_path_under_Raft\n"
            f"plain\t{len(self.provider)}\t{sha256(self.provider).hexdigest()}\t660\tRaft_Data/authored.assets.resS\n").encode()
        self.manifest.write_bytes(self.manifest_bytes)
        self.blob=sha1(b"blob "+str(len(self.manifest_bytes)).encode()+b"\0"+self.manifest_bytes).hexdigest()
        self.texture=NS(m_Width=2,m_Height=2,m_TextureDimension=2,m_ImageCount=1,m_MipsStripped=0,
                        m_MipCount=1,m_TextureFormat=TextureFormat.RGBA32,m_PlatformBlob=None,
                        object_reader=NS(version=(2021,3,45,2),platform=BuildTarget.StandaloneWindows64),
                        image_data=b"",m_StreamData=NS(path="archive:/CAB-authored/authored.assets.resS",offset=5,size=16))
        self.object=NS(path_id=28,type=NS(name="Texture2D"),read=lambda:self.texture)
        self.expected=Image.frombytes("RGBA",(2,2),self.top+self.bottom)

    def load(self,raw):
        self.assertIs(type(raw),bytes)
        self.assertEqual(raw,self.owner_bytes)
        return NS(file=NS(objects={28:self.object}))

    def decode(self):
        with patch.object(parity,"SHADER_OWNERS",{self.owner:pin(self.owner_bytes)}), \
             patch.object(parity,"MANIFEST_BLOB",self.blob):
            return parity.decode_original_texture(self.root,self.manifest,self.key,loader=self.load)

    def test_actual_stream_decoder_uses_exact_range_and_fixed_orientation(self):
        image,kind=self.decode()
        self.assertEqual(kind,"stream")
        self.assertEqual(image.tobytes(),self.expected.tobytes())
        self.assertEqual(self.texture.image_data,b"")
        self.assertEqual(self.texture.m_StreamData.offset,5)
        self.assertEqual(self.provider_file.read_bytes(),self.provider)

    def test_actual_inline_decoder(self):
        self.texture.image_data=self.payload
        self.texture.m_StreamData=NS(path="",offset=0,size=0)
        image,kind=self.decode()
        self.assertEqual(kind,"inline")
        self.assertEqual(image.tobytes(),self.expected.tobytes())

    def test_provider_same_size_mutation_rejected_before_decode(self):
        data=bytearray(self.provider);data[-1]^=1
        self.provider_file.write_bytes(data)
        with patch.object(parity,"decode_payload") as decoder:
            with self.assertRaisesRegex(ValueError,"SHA_mismatch"):
                self.decode()
            decoder.assert_not_called()

    def test_missing_stream_never_calls_decoder(self):
        self.provider_file.unlink()
        with patch.object(parity,"decode_payload") as decoder:
            with self.assertRaises(FileNotFoundError):
                self.decode()
            decoder.assert_not_called()

    def test_manifest_substitution_even_valid_provider_hash_rejected(self):
        self.manifest.write_bytes(self.manifest_bytes.replace(b"660",b"661"))
        with self.assertRaisesRegex(ValueError,"manifest_git_blob_mismatch"):
            self.decode()

    def test_owner_same_size_drift_rejected_before_load(self):
        self.owner_file.write_bytes(b"x"+self.owner_bytes[1:])
        with self.assertRaisesRegex(ValueError,"SHA_mismatch"):
            self.decode()

    def test_range_out_of_bounds(self):
        self.texture.m_StreamData.offset=len(self.provider)-1
        with self.assertRaisesRegex(ValueError,"invalid_pinned_pixel_byte_range"):
            self.decode()

    def test_range_crosses_hash_chunk_boundaries(self):
        with patch.object(parity,"CHUNK",7):
            self.assertEqual(parity.verified_range(self.provider_file,pin(self.provider),5,16),self.payload)

    def test_inline_stream_conflict(self):
        self.texture.image_data=self.payload
        with self.assertRaisesRegex(ValueError,"ambiguous_inline_stream"):
            self.decode()

    def test_path_traversal_rejected(self):
        self.texture.m_StreamData.path="archive:/../authored.assets.resS"
        with self.assertRaisesRegex(ValueError,"unsupported_texture_stream_path"):
            self.decode()

    def test_stripped_top_mip_cannot_be_called_source_parity(self):
        self.texture.m_MipsStripped=1
        with self.assertRaisesRegex(ValueError,"unproven_original_texture_top_mip"):
            self.decode()

    def test_actual_png_exact_pixel_parity(self):
        image,kind=self.decode()
        p=self.root/"authored.png"
        self.expected.save(p)
        result=parity.compare_pixels(image,parity.read_export_png(p))
        self.assertEqual(result["pixel_coordinates_compared"],4)
        self.assertTrue(result["rgba8_samples_equal"])

    def test_identical_histogram_vertical_flip_is_not_equivalent(self):
        image,_=self.decode()
        flipped=self.expected.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        self.assertEqual(image.getchannel("A").histogram(),flipped.getchannel("A").histogram())
        result=parity.compare_pixels(image,flipped)
        self.assertFalse(result["alpha_samples_equal"])
        self.assertTrue(result["alpha_vertical_flip_only_match"])
        self.assertEqual(result["alpha_mismatch_pixels"],4)
        self.assertGreater(result["nonopaque_to_opaque_coordinates"],0)
        self.assertEqual(result["alpha_loss_pixels"],0)
        self.assertFalse(result["net_nonopaque_population_decreased"])
        self.assertFalse(result["all_source_transparency_lost"])

    def test_rgb_mutation_does_not_claim_RGBA_equivalence(self):
        image,_=self.decode()
        wrong=self.expected.copy()
        wrong.putpixel((0,0),(4,5,6,255))
        result=parity.compare_pixels(image,wrong)
        self.assertTrue(result["alpha_samples_equal"])
        self.assertFalse(result["rgba8_samples_equal"])
        self.assertEqual(result["rgb_mismatch_pixels"],1)

    def test_opaque_export_detects_loss_at_exact_coordinates(self):
        image,_=self.decode()
        opaque=self.expected.convert("RGB")
        result=parity.compare_pixels(image,opaque)
        self.assertEqual(result["alpha_loss_pixels"],3)
        self.assertTrue(result["all_source_transparency_lost"])
        self.assertEqual(result["nonopaque_to_opaque_coordinates"],3)
        self.assertEqual(result["alpha_increased_pixels"],3)
        self.assertTrue(result["rgb_samples_equal"])

    def test_dimension_change_unproven(self):
        image,_=self.decode()
        result=parity.compare_pixels(image,self.expected.resize((4,4)))
        self.assertFalse(result["dimensions_match"])
        self.assertEqual(result["pixel_coordinates_compared"],0)

    def test_non_png_or_high_bit_depth_not_proof(self):
        p=self.root/"wrong.png"
        Image.new("I;16",(2,2),1).save(p)
        with self.assertRaisesRegex(ValueError,"requires_8bit_PNG"):
            parity.read_export_png(p)

    def test_only_independently_traced_external_targets_compared(self):
        p=self.root/"authored.png";self.expected.save(p)
        other=(self.owner,29);local=(self.owner,30)
        external=(2800000,"a"*32,3)
        routes={self.key:{"pointer":external},other:{"pointer":(2800000,"b"*32,3)},
                local:{"pointer":(123,"0"*32,0)}}
        selected={self.key:external,local:routes[local]["pointer"]}
        with patch.object(parity,"decode_original_texture",return_value=(self.expected,"stream")) as decode:
            r=parity.external_parity(self.root,self.manifest,selected,routes,{"a"*32:(p,{},True)})
            decode.assert_called_once_with(self.root,self.manifest,self.key)
        self.assertEqual(r["independently_traced_external_targets"],1)
        self.assertEqual(r["exact_rgba8_targets"],1)
        self.assertFalse(r["Unity_import_or_GPU_parity_proven"])

    def test_two_independent_external_pngs_actual_decoder_and_net_loss(self):
        other=(self.owner,29)
        second=NS(**vars(self.texture))
        second.image_data=self.payload
        second.m_StreamData=NS(path="",offset=0,size=0)
        obj2=NS(path_id=29,type=NS(name="Texture2D"),read=lambda:second)
        def load(raw):
            env=self.load(raw)
            env.file.objects[29]=obj2
            return env
        first_path=self.root/"exact.png";self.expected.save(first_path)
        second_path=self.root/"reordered.png"
        self.expected.transpose(Image.Transpose.FLIP_TOP_BOTTOM).save(second_path)
        a,b=(2800000,"a"*32,3),(2800000,"b"*32,3)
        selected={self.key:a,other:b}
        routes={self.key:{"pointer":a},other:{"pointer":b}}
        real_decode=parity.decode_original_texture
        with patch.object(parity,"SHADER_OWNERS",{self.owner:pin(self.owner_bytes)}), \
             patch.object(parity,"MANIFEST_BLOB",self.blob), \
             patch.object(parity,"decode_original_texture",
                side_effect=lambda root,manifest,key:real_decode(root,manifest,key,loader=load)):
            result=parity.external_parity(self.root,self.manifest,selected,routes,
                                          {"a"*32:(first_path,{},True),"b"*32:(second_path,{},True)})
        self.assertEqual(result["targets_decoded"],2)
        self.assertEqual(result["source_stream_targets"],1)
        self.assertEqual(result["source_inline_targets"],1)
        self.assertEqual(result["exact_rgba8_targets"],1)
        self.assertEqual(result["targets_with_alpha_flip_only"],1)
        self.assertEqual(result["targets_with_alpha_loss"],0)
        self.assertFalse(result["all_independently_traced_external_alpha_samples_equal"])

    def test_missing_source_not_equivalence(self):
        p=self.root/"authored.png";self.expected.save(p)
        external=(2800000,"a"*32,3)
        with patch.object(parity,"decode_original_texture",side_effect=FileNotFoundError):
            r=parity.external_parity(self.root,self.manifest,{self.key:external},
                {self.key:{"pointer":external}},{"a"*32:(p,{},True)})
        self.assertEqual(r["targets_unavailable"],1)
        self.assertFalse(r["all_independently_traced_external_alpha_samples_equal"])


if __name__=="__main__":
    unittest.main()
