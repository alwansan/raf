import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
import os
import yaml
from unittest.mock import patch
import zipfile
from scripts.package_android_delivery import package,parse_badging,PACKAGE
from scripts.reassemble_android_delivery import reassemble


class DeliveryTests(unittest.TestCase):
    def test_actual_release_gate_accepts_complete_parts_and_rejects_missing_data(self):
        workflow=yaml.safe_load((Path(__file__).resolve().parents[1]/'.github/workflows/raft-unity-editor-android-import.yml').read_text())
        step=workflow['jobs']['publish-early-test']['steps'][-1]
        script=step['run'].split("<<'PY'\n",1)[1].split('\nPY',1)[0]
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);apk,obb,meta=self.inputs(root);out=root/'release-apk'
            result=package(apk,obb,meta,out,part_bytes=257,asset_limit=500)
            previous=Path.cwd()
            try:
                os.chdir(root)
                with patch.dict(os.environ,{'RUNNER_TEMP':str(root),'GITHUB_RUN_NUMBER':'77','GITHUB_SHA':'test-source'}):
                    exec(compile(script,'actual-publish-gate','exec'),{})
                    self.assertIn('\nSource: test-source\n',(root/'early-test-notes.md').read_text())
                    (out/result['files'][-1]['parts'][-1]['name']).unlink()
                    with self.assertRaises(AssertionError):exec(compile(script,'actual-publish-gate','exec'),{})
            finally:os.chdir(previous)

    def inputs(self, root):
        apk,obb=root/'test.apk',root/'test.obb'
        for p,member,raw in [(apk,'classes.dex',b'synthetic apk'*70),(obb,'assets/bin/Data/data.unity3d',b'synthetic Unity bytes'*100)]:
            with zipfile.ZipFile(p,'w',compression=zipfile.ZIP_STORED) as z:z.writestr(member,raw)
        meta=parse_badging("package: name='"+PACKAGE+"' versionCode='77' versionName='1.0'\nsdkVersion:'23'\ntargetSdkVersion:'35'",77)
        return apk,obb,meta

    def test_complete_split_xapk_and_loose_bytes_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);apk,obb,meta=self.inputs(root)
            out=root/'delivery';result=package(apk,obb,meta,out,part_bytes=257,asset_limit=500)
            for row in result['files']:
                self.assertTrue(all(p['bytes']<=257 for p in row['parts']))
                joined=reassemble(out,row['name'])
                self.assertEqual(hashlib.sha256(joined.read_bytes()).hexdigest(),row['sha256'])
            self.assertEqual((out/'Raft-Android-Test.apk').read_bytes(),apk.read_bytes())
            name='main.77.'+PACKAGE+'.obb'
            self.assertEqual((out/name).read_bytes(),obb.read_bytes())
            with zipfile.ZipFile(out/'Raft-Android-Test.xapk') as z:
                self.assertIsNone(z.testzip())
                manifest=json.loads(z.read('manifest.json'))
                self.assertEqual(manifest['total_size'],apk.stat().st_size+obb.stat().st_size)
                expansion=manifest['expansions'][0]
                self.assertEqual(expansion['file'],'Android/obb/'+PACKAGE+'/'+name)
                self.assertEqual(expansion['file'],expansion['install_path'])
                self.assertEqual(z.read(PACKAGE+'.apk'),apk.read_bytes())
                self.assertEqual(z.read(expansion['file']),obb.read_bytes())
                self.assertTrue(all(i.compress_type==zipfile.ZIP_STORED for i in z.infolist()))
            self.assertFalse(any(p.suffix=='.apks' for p in out.iterdir()))

    def test_small_standalone_is_direct_apk_and_xapk(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);apk,_,meta=self.inputs(root)
            out=root/'delivery';result=package(apk,None,meta,out)
            self.assertFalse(result['companion_required'])
            self.assertTrue((out/'Raft-Android-Test.apk').is_file())
            self.assertTrue((out/'Raft-Android-Test.xapk').is_file())
            with zipfile.ZipFile(out/'Raft-Android-Test.xapk') as z:
                self.assertEqual(json.loads(z.read('manifest.json'))['expansions'],[])
            self.assertEqual(reassemble(out,'Raft-Android-Test.apk').read_bytes(),apk.read_bytes())

    def test_part_corruption_is_refused_before_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);apk,obb,meta=self.inputs(root);out=root/'delivery'
            result=package(apk,obb,meta,out,part_bytes=257,asset_limit=500)
            row=result['files'][-1];p=out/row['parts'][0]['name'];p.write_bytes(b'x'*p.stat().st_size)
            with self.assertRaisesRegex(ValueError,'SHA256'):reassemble(out,row['name'])
            self.assertFalse((out/row['name']).exists())

    def test_wrong_version_missing_companion_and_output_overwrite_rejected(self):
        with self.assertRaises(ValueError):parse_badging("package: name='other' versionCode='77' versionName='1'",77)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);apk,obb,meta=self.inputs(root);out=root/'delivery'
            with self.assertRaises(ValueError):package(apk,root/'missing.obb',meta,out)
            self.assertFalse(out.exists())
            package(apk,obb,meta,out)
            with self.assertRaises(ValueError):package(apk,obb,meta,out)

    def test_member_crc_corruption_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);apk,obb,meta=self.inputs(root)
            data=bytearray(obb.read_bytes());offset=data.index(b'synthetic Unity bytes');data[offset]^=1;obb.write_bytes(data)
            with self.assertRaises(ValueError):package(apk,obb,meta,root/'delivery')

    def test_unsafe_reassembly_manifest_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'delivery.json').write_text(json.dumps({'files':[{'name':'safe.xapk','parts':[{'name':'../outside'}]}]}))
            with self.assertRaises(ValueError):reassemble(root,'safe.xapk')

    def test_interrupted_assembly_is_not_deleted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);apk,obb,meta=self.inputs(root);out=root/'delivery'
            package(apk,obb,meta,out,part_bytes=257,asset_limit=500)
            name='Raft-Android-Test.xapk'
            temporary=out/(name+'.assembling')
            temporary.write_bytes(b'previous partial download - do not erase')
            with self.assertRaisesRegex(ValueError,'Existing assembly temporary file'):
                reassemble(out,name)
            self.assertEqual(temporary.read_bytes(),b'previous partial download - do not erase')
            self.assertFalse((out/name).exists())

    def test_dangling_symlink_paths_are_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);apk,obb,meta=self.inputs(root);out=root/'delivery'
            package(apk,obb,meta,out,part_bytes=257,asset_limit=500)
            name='Raft-Android-Test.xapk'
            output=out/name
            output.symlink_to(out/'nonexistent')
            with self.assertRaisesRegex(ValueError,'Refusing to overwrite output'):
                reassemble(out,name)
            self.assertTrue(output.is_symlink())
            output.unlink()
            temporary=out/(name+'.assembling')
            temporary.symlink_to(out/'nonexistent')
            with self.assertRaisesRegex(ValueError,'Existing assembly temporary file'):
                reassemble(out,name)
            self.assertTrue(temporary.is_symlink())

    def test_insufficient_disk_is_rejected_before_creating_large_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);apk,obb,meta=self.inputs(root);out=root/'delivery'
            package(apk,obb,meta,out,part_bytes=257,asset_limit=500)
            name='Raft-Android-Test.xapk'
            with patch('scripts.reassemble_android_delivery.shutil.disk_usage',
                       return_value=SimpleNamespace(free=0)):
                with self.assertRaisesRegex(ValueError,'Insufficient free disk'):
                    reassemble(out,name)
            self.assertFalse((out/name).exists())
            self.assertFalse((out/(name+'.assembling')).exists())

    def test_failed_new_assembly_removes_only_own_temporary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);apk,obb,meta=self.inputs(root);out=root/'delivery'
            result=package(apk,obb,meta,out,part_bytes=257,asset_limit=500)
            row=result['files'][-1]
            row['sha256']='0'*64
            (out/'delivery.json').write_text(json.dumps(result))
            with self.assertRaisesRegex(ValueError,'Assembled file SHA256 mismatch'):
                reassemble(out,row['name'])
            self.assertFalse((out/(row['name']+'.assembling')).exists())
            self.assertFalse((out/row['name']).exists())

    def test_zip64_streaming_transport_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);apk,obb,meta=self.inputs(root);out=root/'delivery'
            with patch('zipfile.ZIP64_LIMIT',64):
                package(apk,obb,meta,out,part_bytes=257,asset_limit=500)
                path=reassemble(out,'Raft-Android-Test.xapk')
                with zipfile.ZipFile(path) as z:
                    self.assertIsNone(z.testzip())
                    self.assertEqual(z.read(PACKAGE+'.apk'),apk.read_bytes())


if __name__=='__main__':unittest.main()
