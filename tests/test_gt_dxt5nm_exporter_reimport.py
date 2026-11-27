import unittest
from copy import deepcopy
from scripts import gt_dxt5nm_exporter_reimport as v16
from scripts import gt_dxt5nm_texel_policy as v14
from scripts import gt_authored_dxt5nm_alpha_exporter_witness as v15

class DirectCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h=v16.read(v15.V14)
        cls.s=v16.read(v16.V12)["v11_replay"]["textures"]

    def args(self,i):
        h=self.h["verified"]["rows"][i];raw=self.h["independent"]["phase_mip_RGBA_hex"][i]
        gpu=[bytes.fromhex(x) for x in raw["alpha_off"]]
        return gpu,gpu[0] if i==0 else b"",bytes.fromhex(self.s[i]["actual_rgba_hex"]),h,raw,i==0

    def test_exact_historical_mips(self):
        for i in range(2):
            a=self.args(i)
            self.assertEqual(v16.compare_mips(*a),a[3]["alpha_off_mip_sha256"])

    def test_lower_mip_byte_falsifier(self):
        a=self.args(0);a[0][1]=b"\x00"+a[0][1][1:]
        with self.assertRaises(ValueError):v16.compare_mips(*a)

    def test_wrong_orientation(self):
        a=list(self.args(0));a[1]=v14.flip(a[1],5,7)
        with self.assertRaises(ValueError):v16.compare_mips(*a)

    def test_nonreadable_CPU_falsifier(self):
        a=list(self.args(1));a[1]=a[0][0]
        with self.assertRaises(ValueError):v16.compare_mips(*a)

    def test_mismatched_source(self):
        a=list(self.args(0));a[2]=bytes(140)
        with self.assertRaises(ValueError):v16.compare_mips(*a)

    def test_missing_level(self):
        a=list(self.args(1));a[0]=a[0][:-1]
        with self.assertRaises(ValueError):v16.compare_mips(*a)

    def test_historical_raw_bytes_must_agree(self):
        a=list(self.args(0));a[4]=deepcopy(a[4]);a[4]["alpha_off"][2]="00000000"
        with self.assertRaises(ValueError):v16.compare_mips(*a)

    def test_published_V15_normalization_is_labelled(self):
        raw=b"fileFormatVersion: 2\nguid: "+b"a"*32+b"\ntimeCreated: 123\nTextureImporter:\n  alphaIsTransparency: 0\n"
        canonical=b"fileFormatVersion: 2\nguid: VOLATILE\ntimeCreated: VOLATILE\nTextureImporter:\n  alphaIsTransparency: 0\n"
        self.assertEqual(v16.historical_meta_stable(raw),canonical)
        self.assertNotEqual(v15.meta_stable(raw),canonical)
        self.assertEqual(v16.historical_meta_stable(raw.replace(b"a"*32,b"b"*32).replace(b"123",b"456")),canonical)

    def test_normalization_rejects_duplicate_header(self):
        raw=b"guid: "+b"a"*32+b"\ntimeCreated: 123\ntimeCreated: 456\n"
        with self.assertRaises(ValueError):v16.historical_meta_stable(raw)

    def test_probe_never_writes_texture_metadata(self):
        s=(v16.V16_TOOLS/"SyntheticNormalExporterReimport.cs").read_text()
        self.assertNotIn("File.WriteAllBytes",s)
        self.assertNotIn("PolicyManifest",s)
        self.assertIn('ObservePhase("exporter_candidate",m,shader,false)',s)
        self.assertIn("Reimport(t.path)",s)

if __name__=="__main__":unittest.main()
