import io
from pathlib import Path
import struct
import tarfile
import tempfile
import unittest
import zipfile
from scripts.audit_fmod_unity_package import elf_identity, fmod_version, inspect_package


SYMBOLS = ['FMOD_System_Create', 'FMOD_System_GetVersion', 'FMOD_Studio_System_Create']


def elf(machine=183, defined=True, needed=()):
    strings = b'\0'
    indexes = {}
    for name in SYMBOLS + list(needed):
        indexes[name] = len(strings)
        strings += name.encode() + b'\0'
    symbol_offset = 64 + len(strings)
    symbols = bytes(24) + b''.join(struct.pack('<IBBHQQ', indexes[name], 0x12, 0, int(defined), 0, 0)
                                  for name in SYMBOLS)
    dynamic_offset = symbol_offset + len(symbols)
    dynamic = b''.join(struct.pack('<QQ', 1, indexes[name]) for name in needed) + bytes(16)
    section_offset = dynamic_offset + len(dynamic)
    sections = bytes(64)
    sections += struct.pack('<IIQQQQIIQQ', 0, 3, 0, 0, 64, len(strings), 0, 0, 1, 0)
    sections += struct.pack('<IIQQQQIIQQ', 0, 11, 0, 0, symbol_offset, len(symbols), 1, 0, 8, 24)
    sections += struct.pack('<IIQQQQIIQQ', 0, 6, 0, 0, dynamic_offset, len(dynamic), 1, 0, 8, 16)
    ident = b'\x7fELF\x02\x01\x01' + bytes(9)
    header = struct.pack('<HHIQQQIHHHHHH', 3, machine, 1, 0, 0, section_offset, 0, 64, 0, 0, 64, 4, 0)
    return ident + header + strings + symbols + dynamic + sections


def bridge(valid=True):
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as z:
        z.writestr('org/fmod/FMOD.class' if valid else 'other.class', b'\xca\xfe\xba\xbe' + bytes(4))
    return out.getvalue()


class FmodPackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'official.unitypackage'

    def package(self, version='0x00020215', native=None, java=True, extra_path=None):
        files = [('Assets/Plugins/FMOD/src/fmod.cs', ('public class VERSION { public const int number = ' + version + '; }').encode()),
                 ('Assets/Plugins/FMOD/platforms/android/lib/arm64-v8a/libfmodstudio.so', native or elf())]
        if java:
            files.append(('Assets/Plugins/FMOD/platforms/android/lib/fmod.jar', bridge()))
        if extra_path:
            files.append((extra_path, b'not used'))
        with tarfile.open(self.path, 'w:gz') as tar:
            for i, (name, data) in enumerate(files, 1):
                guid = f'{i:032x}'
                for part, value in [('pathname', name.encode()), ('asset', data)]:
                    member = tarfile.TarInfo(guid + '/' + part)
                    member.size = len(value)
                    tar.addfile(member, io.BytesIO(value))

    def test_bcd_version_is_not_decimal_patch_21(self):
        self.assertEqual(fmod_version(131605), '2.02.15')
        self.assertEqual(fmod_version(0x00020221), '2.02.21')

    def test_invalid_bcd_refused(self):
        with self.assertRaises(ValueError):
            fmod_version(0x000202af)

    def test_defined_exports_and_abi(self):
        result = elf_identity(elf())
        self.assertEqual(result['abi'], 'arm64-v8a')
        self.assertEqual(result['exports'], set(SYMBOLS))

    def test_arm32_or_undefined_symbols_do_not_pass(self):
        for data in (elf(machine=40), elf(defined=False), b'\x7fELF'):
            with self.assertRaises(ValueError):
                elf_identity(data)

    def test_truncated_section_table_refused(self):
        with self.assertRaises(ValueError):
            elf_identity(elf()[:-1])

    def test_native_dependency_path_refused(self):
        with self.assertRaisesRegex(ValueError, 'Unsafe native'):
            elf_identity(elf(needed=('../libfmod.so',)))

    def test_exact_package_passes_without_extracting_or_running(self):
        self.package()
        before = set(Path(self.tmp.name).iterdir())
        result = inspect_package(self.path)
        self.assertEqual(result['header_version'], '2.02.15')
        self.assertFalse(result['runtime_getVersion_executed'])
        self.assertEqual(set(result['libraries']), {'libfmodstudio.so'})
        self.assertEqual(set(Path(self.tmp.name).iterdir()), before)

    def test_wrong_version_refused(self):
        self.package(version='0x00020221')
        with self.assertRaisesRegex(ValueError, 'exactly 2.02.15'):
            inspect_package(self.path)

    def test_java_bridge_required(self):
        self.package(java=False)
        with self.assertRaisesRegex(ValueError, 'Java bridge'):
            inspect_package(self.path)

    def test_native_dependency_closure_is_checked(self):
        self.package(native=elf(needed=('libfmod.so', 'liblog.so')))
        with self.assertRaisesRegex(ValueError, 'dependency'):
            inspect_package(self.path)

    def test_archive_symlink_refused(self):
        with tarfile.open(self.path, 'w:gz') as tar:
            member = tarfile.TarInfo('link')
            member.type = tarfile.SYMTYPE
            member.linkname = '/tmp/outside'
            tar.addfile(member)
        with self.assertRaisesRegex(ValueError, 'links'):
            inspect_package(self.path)

    def test_unsafe_unity_path_refused(self):
        self.package(extra_path='Assets/../outside.so')
        with self.assertRaisesRegex(ValueError, 'Unsafe Unity'):
            inspect_package(self.path)
