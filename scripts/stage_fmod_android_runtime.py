"""Authenticate a sealed vendor runtime subset before staging any Unity files.

The key is a CI environment secret, never source or command-line input.
No full SDK, competing CSharp providers or original game data are imported.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import zipfile

AAD = b'Raft/FMOD/2.02.15/android-arm64/v1'
PREFIX = 'Assets/Plugins/FMOD/'
NAMES = {'platforms/android/lib/arm64-v8a/' + n for n in
         ('libfmod.so', 'libfmodstudio.so', 'libresonanceaudio.so')}
NAMES |= {'platforms/android/lib/fmod.jar', 'LICENSE.TXT'}
ALLOWED = {PREFIX + n + suffix for n in NAMES for suffix in ('', '.meta')}


def unpack(cipher, key_hex, manifest):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    if not re.fullmatch('[0-9a-fA-F]{64}', key_hex):
        raise ValueError('FMOD_ANDROID_RUNTIME_KEY must be a 32-byte hex CI secret')
    if (manifest.get('schema') != 1 or manifest.get('version') != '2.02.15'
            or set(manifest.get('files', {})) != ALLOWED):
        raise ValueError('Unexpected runtime manifest schema or file scope')
    if (len(cipher) != manifest['cipher_bytes'] or len(cipher) > 8 * 1024 * 1024
            or hashlib.sha256(cipher).hexdigest() != manifest['cipher_sha256']
            or cipher[:5] != b'RFMD1'):
        raise ValueError('Sealed runtime size/hash/header mismatch')
    plain = AESGCM(bytes.fromhex(key_hex)).decrypt(cipher[5:17], cipher[17:], AAD)
    result = {}
    with zipfile.ZipFile(io.BytesIO(plain)) as archive:
        names = archive.namelist()
        if set(names) != ALLOWED or len(names) != len(ALLOWED):
            raise ValueError('Unexpected or duplicate decrypted runtime members')
        if sum(i.file_size for i in archive.infolist()) > 16 * 1024 * 1024:
            raise ValueError('Runtime expanded size exceeds fixed scope')
        for name in sorted(ALLOWED):
            info = archive.getinfo(name)
            if info.is_dir() or (info.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError('Runtime directories/links refused')
            data = archive.read(name)
            expected = manifest['files'][name]
            if len(data) != expected['bytes'] or hashlib.sha256(data).hexdigest() != expected['sha256']:
                raise ValueError('Vendor runtime file fingerprint mismatch')
            result[name] = data
    return result


def stage(project, files, write=False):
    if set(files) != ALLOWED:
        raise ValueError('Unexpected staged runtime scope')
    # Complete preflight before mutation; never overwrite exported assets/metas.
    for name, data in files.items():
        destination = project / name
        if destination.is_symlink() or not destination.resolve().is_relative_to(project.resolve()):
            raise ValueError('Unsafe runtime destination')
        if destination.exists() and (not destination.is_file() or destination.read_bytes() != data):
            raise ValueError('Existing Unity runtime asset/meta conflict; refusing overwrite')
    created = 0
    if write:
        for name, data in sorted(files.items()):
            destination = project / name
            if not destination.exists():
                destination.parent.mkdir(parents=True, exist_ok=True)
                with destination.open('xb') as output:
                    output.write(data)
                created += 1
    return {'validated_files': len(files), 'created_files': created,
            'original_managed_providers_replaced': 0, 'original_metas_overwritten': 0,
            'version': '2.02.15', 'device_audio_verified': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cipher', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    key = os.environ.get('FMOD_ANDROID_RUNTIME_KEY', '')
    if not key:
        raise SystemExit('Missing FMOD_ANDROID_RUNTIME_KEY environment secret; no runtime staged')
    try:
        files = unpack(args.cipher.read_bytes(), key, json.loads(args.manifest.read_text()))
        print('RAFT_FMOD_ANDROID_RUNTIME ' + json.dumps(stage(args.project, files, args.apply), sort_keys=True))
    except Exception:
        # Avoid leaking secret or decrypted vendor payload via parser exceptions.
        raise SystemExit('FMOD authenticated staging failed; no fallback SDK/source substitution') from None
