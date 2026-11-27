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

    def test_actual_historical_erratum_raw_metadata(self):
        h=v16.read(v16.V15);raw=v16.V15.with_name("authored-rgba32-pathid1-historical-before.meta.txt").read_bytes()
        rows=v16.historical_expected_rows(h,raw)
        original={(r["mode"],tuple(r["source_key"])):r for r in h["independent"]["six_pair_rows"]}
        for key,r in rows.items():
            if key==("rgba",("sharedassets3.assets",1)):
                self.assertEqual(r["normalized_before_sha256"],"886a66512cc4ffd828e2a2b5c6c03da0e91f54394f7cdce847aa42161dee8ea7")
                self.assertEqual(r["normalized_after_sha256"],v16.digest(v16.historical_meta_stable(raw)))
                self.assertEqual(original[key]["normalized_before_sha256"],"886a66512cc4ffd828e2a5b5c6c03da0e91f54394f7cdce847aa42161dee8ea7")
                for field in r:
                    if not field.startswith("normalized_"):self.assertEqual(r[field],original[key][field])
            else:self.assertEqual(r,original[key])

    def test_historical_erratum_rejects_wrong_archive_or_old_hash(self):
        for key in ("archive","row"):
            h=v16.read(v16.V15)
            if key=="archive":h["archive"]["sha256"]="0"*64
            else:next(r for r in h["independent"]["six_pair_rows"] if r["mode"]=="rgba" and r["source_key"][1]==1)["normalized_after_sha256"]="0"*64
            with self.assertRaises(ValueError):v16.historical_expected_rows(h)

    def test_historical_erratum_rejects_changed_raw_bytes(self):
        h=v16.read(v16.V15);raw=v16.V15.with_name("authored-rgba32-pathid1-historical-before.meta.txt").read_bytes()
        with self.assertRaises(ValueError):v16.historical_expected_rows(h,raw.replace(b"alphaIsTransparency: 1",b"alphaIsTransparency: 0"))

    def test_probe_never_writes_texture_metadata(self):
        s=(v16.V16_TOOLS/"SyntheticNormalExporterReimport.cs").read_text()
        self.assertNotIn("File.WriteAllBytes",s)
        self.assertNotIn("PolicyManifest",s)
        self.assertIn('ObservePhase("exporter_candidate",m,shader,false)',s)
        self.assertIn("Reimport(t.path)",s)

if __name__=="__main__":unittest.main()
