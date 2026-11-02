"""Package authenticated native outputs as APK + OBB + XAPK, with lossless transport parts.

Does not rebuild, resign, downsample, repartition Unity data or invent an APKS.
XAPK installation/OBB mounting still requires a compatible device installer.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

PACKAGE = 'com.alwansan.raft.androidtest'
RELEASE_LIMIT = 2_147_483_648
DEFAULT_PART = 1024 * 1024 * 1024
BUFFER = 1024 * 1024


class PartsWriter:
    # An unseekable ZIP sink avoids materializing an extra multi-GB XAPK on disk.
    def __init__(self, root, name, limit):
        self.root, self.name, self.limit = root, name, limit
        self.position = 0
        self.parts = []
        self.stream = None
        self.count = 0
        self.total_hash = hashlib.sha256()
    def tell(self): return self.position
    def flush(self):
        if self.stream: self.stream.flush()
    def _finish(self):
        if self.stream:
            self.stream.close()
            self.parts[-1].update(bytes=self.count, sha256=self.part_hash.hexdigest())
            self.stream = None
    def write(self, data):
        size = len(data)
        self.total_hash.update(data)
        view = memoryview(data)
        while view:
            if self.stream is None:
                name = self.name + '.part' + str(len(self.parts)+1).zfill(3)
                self.stream = (self.root/name).open('xb')
                self.parts.append({'name':name})
                self.count = 0
                self.part_hash = hashlib.sha256()
            chunk = view[:self.limit-self.count]
            self.stream.write(chunk)
            self.part_hash.update(chunk)
            self.count += len(chunk)
            self.position += len(chunk)
            view = view[len(chunk):]
            if self.count == self.limit: self._finish()
        return size
    def finish(self):
        self._finish()
        if len(self.parts) == 1:
            previous = self.parts[0]['name']
            (self.root/previous).rename(self.root/self.name)
            self.parts[0]['name'] = self.name
        return {'name':self.name, 'bytes':self.position,
                'sha256':self.total_hash.hexdigest(), 'parts':self.parts}


def parse_badging(text, expected_version):
    match = re.search(r"^package: name='([^']+)' versionCode='([0-9]+)' versionName='([^']*)'", text, re.M)
    if not match or match[1] != PACKAGE or int(match[2]) != expected_version or expected_version < 1:
        raise ValueError('APK package/version does not match this native build')
    def sdk(key):
        row = re.search(r'^'+key+r":'([0-9]+)'",text,re.M)
        if not row: raise ValueError('APK SDK metadata unavailable')
        return row[1]
    return {'package_name':PACKAGE,'version_code':str(expected_version),'version_name':match[3],
            'min_sdk_version':sdk('sdkVersion'),'target_sdk_version':sdk('targetSdkVersion'),
            'permissions':re.findall(r"^uses-permission: name='([^']+)'",text,re.M)}


def copy_transport(source, output, name, limit):
    sink = PartsWriter(output,name,limit)
    try:
        with source.open('rb') as stream:
            for block in iter(lambda:stream.read(BUFFER),b''): sink.write(block)
        return sink.finish()
    finally: sink._finish()


def package(apk, obb, metadata, output, *, part_bytes=DEFAULT_PART, asset_limit=RELEASE_LIMIT):
    if metadata.get('package_name') != PACKAGE or not re.fullmatch(r'[1-9][0-9]*',metadata.get('version_code','')):
        raise ValueError('Invalid package identity')
    if not 1 <= part_bytes < asset_limit <= RELEASE_LIMIT:
        raise ValueError('Transport part must fit the GitHub release asset limit')
    if output.exists(): raise ValueError('Refusing to overwrite delivery directory')
    inputs = [apk] + ([obb] if obb is not None else [])
    if not all(p.is_file() and not p.is_symlink() and p.stat().st_size for p in inputs):
        raise ValueError('Required native output missing or empty')
    for p in inputs:
        try:
            with zipfile.ZipFile(p) as archive:
                if archive.testzip() is not None: raise ValueError('Native ZIP CRC mismatch')
        except (zipfile.BadZipFile, RuntimeError, OSError, EOFError):
            raise ValueError('Native ZIP integrity failure') from None
    # Loose outputs plus XAPK are alternatives; both retain original bytes.
    total = sum(p.stat().st_size for p in inputs)
    if shutil.disk_usage(output.parent).free < 2*total+64*1024*1024:
        raise ValueError('Insufficient free disk for complete loose outputs and XAPK')
    output.mkdir()
    def transport(path, name):
        # Retain directly downloadable complete files whenever GitHub permits.
        limit = asset_limit-1 if path.stat().st_size < asset_limit else part_bytes
        return copy_transport(path,output,name,limit)
    records = [transport(apk,'Raft-Android-Test.apk')]
    members = [(apk,PACKAGE+'.apk')]
    expansions = []
    if obb is not None:
        name = 'main.'+metadata['version_code']+'.'+PACKAGE+'.obb'
        records.append(transport(obb,name))
        member = 'Android/obb/'+PACKAGE+'/'+name
        members.append((obb,member))
        expansions.append({'file':member,'install_location':'EXTERNAL_STORAGE','install_path':member})
    manifest = dict(metadata,xapk_version=1,name='Raft Android Test',total_size=total,expansions=expansions)
    sink = PartsWriter(output,'Raft-Android-Test.xapk',
                       asset_limit-1 if total+64*1024 < asset_limit else part_bytes)
    try:
        with zipfile.ZipFile(sink,'w',compression=zipfile.ZIP_STORED,allowZip64=True) as archive:
            archive.writestr('manifest.json',json.dumps(manifest,ensure_ascii=False))
            for path,name in members:
                archive.write(path,name,compress_type=zipfile.ZIP_STORED)
        records.append(sink.finish())
    finally: sink._finish()
    result = {'schema':1,'package':PACKAGE,'version_code':metadata['version_code'],
              'companion_required':obb is not None,'files':records,
              'transport_only_parts':True,'device_install_verified':False}
    (output/'delivery.json').write_text(json.dumps(result,indent=2)+'\n')
    lines = [p['sha256']+'  '+p['name'] for r in records for p in r['parts']]
    (output/'SHA256SUMS').write_text('\n'.join(lines)+'\n')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--apk',type=Path,required=True);p.add_argument('--obb',type=Path)
    p.add_argument('--badging',type=Path,required=True);p.add_argument('--version-code',type=int,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    metadata=parse_badging(args.badging.read_text(),args.version_code)
    result=package(args.apk,args.obb,metadata,args.output)
    shutil.copy2(Path(__file__).with_name('reassemble_android_delivery.py'),args.output/'reassemble.py')
    print('RAFT_ANDROID_DELIVERY '+json.dumps({'logical_files':len(result['files']),
          'companion_required':result['companion_required'],'transport_parts':sum(len(r['parts']) for r in result['files']),
          'lossless_transport':True,'device_install_verified':False},sort_keys=True))


if __name__=='__main__':main()
