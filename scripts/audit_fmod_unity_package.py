"""Read-only validation of a user-supplied official FMOD Unity package.

Never imports competing managed sources or executes any native library.
Only metadata, hashes, ABI and defined dynamic symbols are reported.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import struct
import tarfile
import zipfile

EXPECTED_VERSION = 0x00020215
NATIVE_NAMES = {'libfmodstudio.so', 'libfmod.so', 'libresonanceaudio.so', 'libc++_shared.so'}


def fmod_version(value):
    if not isinstance(value, int) or not 0 <= value <= 0xffffffff:
        raise ValueError('Invalid FMOD version number')
    bcd = f'{value:08x}'
    if not bcd.isdigit():
        raise ValueError('FMOD version is not valid BCD')
    return f'{int(bcd[:4])}.{bcd[4:6]}.{bcd[6:8]}'


def bounded_slice(data, offset, size):
    if offset < 0 or size < 0 or offset + size > len(data):
        raise ValueError('ELF range outside file')
    return data[offset:offset + size]


def elf_identity(data):
    if len(data) < 64 or data[:7] != b'\x7fELF\x02\x01\x01':
        raise ValueError('Not a complete little-endian ELF64 library')
    header = struct.unpack_from('<HHIQQQIHHHHHH', data, 16)
    if header[0] != 3 or header[1] != 183 or header[7] != 64:
        raise ValueError('Expected AArch64 shared library')
    shoff, shsize, shcount = header[5], header[10], header[11]
    if shsize != 64 or shcount < 1 or shcount > 4096:
        raise ValueError('Unsupported ELF section table')
    bounded_slice(data, shoff, shsize * shcount)
    sections = [struct.unpack_from('<IIQQQQIIQQ', data, shoff + i * shsize) for i in range(shcount)]
    exports, needed = set(), set()
    def string_at(strings, index):
        if index >= len(strings):
            raise ValueError('ELF string index outside table')
        end = strings.find(b'\0', index)
        if end < 0:
            raise ValueError('ELF string is not terminated')
        return strings[index:end].decode('ascii', errors='strict')
    for section in sections:
        kind, offset, size, link, entry_size = section[1], section[4], section[5], section[6], section[9]
        if kind not in (6, 11):
            continue
        if link >= len(sections):
            raise ValueError('ELF string-table link is invalid')
        string_section = sections[link]
        if string_section[1] != 3:
            raise ValueError('ELF link does not reference a string table')
        strings = bounded_slice(data, string_section[4], string_section[5])
        entries = bounded_slice(data, offset, size)
        expected = 24 if kind == 11 else 16
        if entry_size != expected or size % expected:
            raise ValueError('ELF dynamic entry layout is invalid')
        for at in range(0, size, expected):
            if kind == 11:
                name, info, visibility, defined, _, _ = struct.unpack_from('<IBBHQQ', entries, at)
                if defined and info >> 4 in (1, 2) and info & 15 in (2, 10) and visibility & 3 in (0, 3):
                    exports.add(string_at(strings, name))
            else:
                tag, value = struct.unpack_from('<QQ', entries, at)
                if tag == 0:
                    break
                if tag == 1:
                    dependency = string_at(strings, value)
                    if '/' in dependency or '\\' in dependency:
                        raise ValueError('Unsafe native dependency path')
                    needed.add(dependency)
    if not exports:
        raise ValueError('No defined public dynamic function exports found')
    return {'abi': 'arm64-v8a', 'exports': exports, 'needed': needed}


def inspect_package(path):
    path = Path(path)
    if not 0 < path.stat().st_size <= 1024 * 1024 * 1024:
        raise ValueError('Unexpected package size')
    entries, total = {}, 0
    with tarfile.open(path, mode='r:gz') as archive:
        for index, member in enumerate(archive):
            if index > 20000 or member.issym() or member.islnk():
                raise ValueError('Unsafe package links or excessive member count')
            name = member.name
            if name.startswith('./'):
                name = name[2:]
            parts = PurePosixPath(name).parts
            if name.startswith('/') or '..' in parts or '\\' in name:
                raise ValueError('Unsafe archive member path')
            if member.isdir():
                continue
            total += member.size
            if member.size > 256 * 1024 * 1024 or total > 4 * 1024 * 1024 * 1024:
                raise ValueError('Package expanded-size safety bound exceeded')
            if len(parts) != 2 or not re.fullmatch('[0-9a-fA-F]{32}', parts[0]):
                continue
            if parts[1] not in ('pathname', 'asset', 'asset.meta'):
                continue
            row = entries.setdefault(parts[0].lower(), {})
            if parts[1] in row:
                raise ValueError('Duplicate Unity package entry')
            row[parts[1]] = member
        libraries, bridges, versions = {}, {}, set()
        for row in entries.values():
            if 'pathname' not in row or 'asset' not in row:
                continue
            if row['pathname'].size > 2048:
                raise ValueError('Unexpected pathname size')
            asset_path = archive.extractfile(row['pathname']).read().decode('utf-8').rstrip('\0\r\n')
            parts = PurePosixPath(asset_path).parts
            if not parts or parts[0] != 'Assets' or '..' in parts or '\\' in asset_path:
                raise ValueError('Unsafe Unity asset path')
            lower = asset_path.lower()
            name = parts[-1]
            if name.lower() == 'fmod.cs':
                if row['asset'].size > 2 * 1024 * 1024:
                    raise ValueError('Unexpected FMOD header size')
                text = archive.extractfile(row['asset']).read().decode('utf-8-sig')
                found = re.findall(r'\bconst\s+int\s+number\s*=\s*(0[xX][0-9a-fA-F]+|\d+)\s*;', text)
                versions.update(int(n, 16 if n.lower().startswith('0x') else 10) for n in found)
            android = any(part.lower() == 'android' for part in parts)
            arm64 = any(part.lower() in ('arm64-v8a', 'arm64', 'aarch64') for part in parts)
            if not android or not ((arm64 and name in NATIVE_NAMES) or name.lower() == 'fmod.jar'):
                continue
            if row['asset'].size > 64 * 1024 * 1024:
                raise ValueError('Unexpected runtime payload size')
            data = archive.extractfile(row['asset']).read()
            metadata = {'path': asset_path, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
            if name in NATIVE_NAMES:
                if name in libraries:
                    raise ValueError('Duplicate Android native library candidates')
                identity = elf_identity(data)
                metadata.update(abi=identity['abi'], needed=sorted(identity['needed']))
                libraries[name] = (metadata, identity['exports'])
            else:
                with zipfile.ZipFile(io.BytesIO(data)) as jar:
                    if len(jar.infolist()) > 4096 or len(jar.namelist()) != len(set(jar.namelist())):
                        raise ValueError('Unexpected or duplicate Java bridge members')
                    if 'org/fmod/FMOD.class' not in jar.namelist():
                        raise ValueError('FMOD Android Java bridge class missing')
                    if jar.getinfo('org/fmod/FMOD.class').file_size > 1024 * 1024:
                        raise ValueError('Java bridge size bound exceeded')
                    if not jar.read('org/fmod/FMOD.class').startswith(b'\xca\xfe\xba\xbe'):
                        raise ValueError('Invalid Android Java class signature')
                if bridges:
                    raise ValueError('Duplicate Android Java bridge candidates')
                bridges[name] = metadata
        if versions != {EXPECTED_VERSION}:
            raise ValueError('FMOD managed header must be exactly 2.02.15; mixed/wrong versions refused')
        if 'libfmodstudio.so' not in libraries or not bridges:
            raise ValueError('Required release Android ARM64 Studio library or Java bridge absent')
        reachable, pending = set(), ['libfmodstudio.so']
        while pending:
            name = pending.pop()
            if name in reachable:
                continue
            reachable.add(name)
            pending.extend(dep for dep in libraries[name][0]['needed'] if dep in libraries)
        all_exports = set().union(*(libraries[name][1] for name in reachable))
        required = {'FMOD_System_Create', 'FMOD_System_GetVersion', 'FMOD_Studio_System_Create'}
        if not required <= all_exports:
            raise ValueError('Required defined native FMOD API exports are missing')
        for metadata, _ in libraries.values():
            for dependency in metadata['needed']:
                if (dependency.startswith('libfmod') or dependency == 'libc++_shared.so') and dependency not in libraries:
                    raise ValueError('Packaged native FMOD dependency is missing')
    with path.open('rb') as source:
        package_hash = hashlib.file_digest(source, 'sha256').hexdigest()
    return {'package_sha256': package_hash, 'header_version': fmod_version(EXPECTED_VERSION),
            'header_version_verified': True, 'runtime_getVersion_executed': False,
            'libraries': {name: data for name, (data, _) in libraries.items()}, 'java_bridge': bridges,
            'required_defined_api_exports': sorted(required),
            'limitations': 'Read-only official-package metadata audit; no native execution, Unity import, sound banks or device audio verification.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('package', type=Path)
    args = parser.parse_args()
    print('RAFT_FMOD_ANDROID_PACKAGE_AUDIT ' + json.dumps(inspect_package(args.package), sort_keys=True))
