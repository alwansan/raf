import json
from pathlib import Path
import tempfile
import unittest
from scripts.restore_tmp_shaders import restore
from scripts.restore_postfx_shaders import sources,verified_blob,INCLUDES

class PostFxTests(unittest.TestCase):
    def test_wrong_vendor_blob_refused(self):
        with self.assertRaises(ValueError):verified_blob({'path':'x','bytes':1,'git_blob':'0'*40},lambda _:b'x')
    def test_untrusted_repository_refused(self):
        with self.assertRaises(ValueError):sources({'repository':'other','commit':'x','files':[]},lambda _:b'')
    def test_exact_name_preserves_guid_and_bloom_pass_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);target=root/'project/Assets/Shader/bloom.shader';target.parent.mkdir(parents=True)
            target.write_text('Shader "Hidden/Post FX/Bloom" { SubShader { Pass {} } }')
            meta=Path(str(target)+'.meta');meta.write_text('guid: original-guid\n')
            vendor='Shader "Hidden/Post FX/Bloom" { SubShader { Pass {} Pass {} Pass {} Pass {} } }'
            restore(root/'project',root/'backup',{'Hidden/Post FX/Bloom':vendor},{},b'notice',shader_prefix='Hidden/Post FX/',include_root=INCLUDES,label='POSTFX_V1',vendor_version='fixture')
            self.assertEqual(target.read_text(),vendor);self.assertEqual(meta.read_text(),'guid: original-guid\n')
