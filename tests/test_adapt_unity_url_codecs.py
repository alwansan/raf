import tempfile
import unittest
from pathlib import Path
from scripts.adapt_unity_url_codecs import repair

class UrlCodecAdaptationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.file=self.root/"Assets/Scripts/Assembly-CSharp/Raft_Network.cs"
        self.file.parent.mkdir(parents=True)
        self.file.write_text("class Network { string Encode(string v) { return HttpUtility.UrlEncode(v); } string Decode(string v) { return HttpUtility.UrlDecode(v); } }")
        self.meta=self.file.with_suffix(".cs.meta")
        self.meta.write_bytes(b"guid: 0123456789abcdef0123456789abcdef")
    def tearDown(self):
        self.tmp.cleanup()
    def test_changes_only_codecs_preserves_argument_and_meta(self):
        before=self.file.read_text()
        meta=self.meta.read_bytes()
        result=repair(self.root,apply=True)
        self.assertEqual(result["url_codec_calls_adapted"],2)
        self.assertEqual(self.file.read_text(),before.replace("HttpUtility.","System.Net.WebUtility."))
        self.assertEqual(self.meta.read_bytes(),meta)
        self.assertEqual(repair(self.root,apply=True)["url_codec_calls_adapted"],0)
    def test_dryrun_preserves_source(self):
        before=self.file.read_bytes()
        self.assertEqual(repair(self.root,apply=False)["url_codec_calls_adapted"],2)
        self.assertEqual(self.file.read_bytes(),before)
    def test_refuses_unknown_http_api_without_partial_edit(self):
        self.file.write_text(self.file.read_text()+"\nHttpUtility.HtmlDecode(value);")
        before=self.file.read_bytes()
        with self.assertRaises(ValueError):
            repair(self.root,apply=True)
        self.assertEqual(self.file.read_bytes(),before)

if __name__=="__main__": unittest.main()
