"""Recover the authenticated PostFX histogram kernel and its Resources identity."""
import argparse
import hashlib
from pathlib import Path
import re
import shutil
from scripts.restore_postfx_shaders import download, PREFIX, INCLUDES
from scripts.restore_tmp_shaders import rewrite_includes

PIN = '6ae7e4dde5a2c01ea982d6b780dd4951c9cd22b6'
GUID = re.compile(r'^guid: ([a-f0-9]{32})$', re.M)


def verified_source(raw):
    if len(raw) != 2516 or hashlib.sha1(b'blob 2516\0' + raw).hexdigest() != PIN:
        raise ValueError('EyeHistogram vendor blob fingerprint mismatch')
    text = raw.decode('utf-8-sig')
    if re.findall(r'^#pragma kernel (\w+)', text, re.M) != ['KEyeHistogram', 'KEyeHistogramClear']:
        raise ValueError('Histogram kernel contract changed')
    return text


def restore(project, backup, raw):
    project, backup = project.resolve(), backup.resolve()
    if backup == project or project in backup.parents:
        raise ValueError('Backup must be outside imported project')
    source = verified_source(raw)
    targets = list((project/'Assets').rglob('EyeHistogram.asset'))
    if len(targets) != 1:
        raise ValueError('Expected exactly one original EyeHistogram compute asset')
    old = targets[0]
    text = old.read_text()
    if not re.search(r'^--- !u!72 &7200000\s*$', text, re.M) or not re.search(r'^  m_Name: EyeHistogram\s*$', text, re.M):
        raise ValueError('Unexpected original ComputeShader identity/fileID')
    meta = Path(str(old)+'.meta')
    if old.is_symlink() or meta.is_symlink() or not meta.is_file():
        raise ValueError('Original compute asset and meta must be regular files')
    match = GUID.search(meta.read_text())
    if not match:
        raise ValueError('Missing original compute GUID')
    includes = {}
    for name in ('Common.cginc', 'EyeAdaptation.cginc'):
        p = project/INCLUDES/name
        if not p.is_file():
            raise ValueError('Restore authenticated PostFX includes first')
        includes[name] = p.read_text()
    if not all(re.search(r'^#define\s+'+key+r'\s+'+value+r'\s*$', includes['EyeAdaptation.cginc'], re.M)
               for key, value in [('HISTOGRAM_BINS','64'), ('HISTOGRAM_THREAD_X','16'), ('HISTOGRAM_THREAD_Y','16')]):
        raise ValueError('Original CSharp histogram dimensions do not match vendor include')
    output = project/'Assets/RaftAndroid/Resources/Shaders/EyeHistogram.compute'
    resource_conflicts = [p for p in (project/'Assets').rglob('EyeHistogram.*')
                          if p.suffix != '.meta' and '/Resources/Shaders/' in p.as_posix() and p != old]
    if output.exists() or Path(str(output)+'.meta').exists() or resource_conflicts:
        raise ValueError('Conflicting histogram Resources identity')
    destination = backup/old.relative_to(project)
    if destination.exists() or Path(str(destination)+'.meta').exists():
        raise ValueError('Refusing to overwrite original backup')
    # Keep original serialized object and NativeFormatImporter metadata privately.
    # A .compute source needs ComputeShaderImporter; preserve its GUID/main fileID.
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(old, destination)
    shutil.copy2(meta, Path(str(destination)+'.meta'))
    output_meta = Path(str(output)+'.meta')
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rewrite_includes(source, includes, INCLUDES))
    output_meta.write_text('fileFormatVersion: 2\nguid: '+match[1]+'\nComputeShaderImporter:\n  externalObjects: {}\n  currentAPIMask: 4\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n')
        old.unlink()
        meta.unlink()
    except Exception:
        # Preserve original GUID references if any filesystem operation fails.
        # Backups contain the exact original asset and original importer meta.
        if not old.exists():
            shutil.copy2(destination, old)
        if not meta.exists():
            shutil.copy2(Path(str(destination)+'.meta'), meta)
        output.unlink(missing_ok=True)
        output_meta.unlink(missing_ok=True)
        raise
    print('RAFT_POSTFX_COMPUTE_RESTORED kernels=2 originalGUIDPreserved=true mainFileID=7200000 resource=Shaders/EyeHistogram deviceVerified=false')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path)
    parser.add_argument('--backup', type=Path)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    raw = download(PREFIX+'EyeHistogram.compute')
    verified_source(raw)
    if args.verify_only:
        print('RAFT_OFFICIAL_HISTOGRAM_SOURCE gitBlobHashVerified=true kernels=2')
        return
    if not args.project or not args.backup:
        raise ValueError('Project and external backup required')
    restore(args.project, args.backup, raw)


if __name__ == '__main__':
    main()
