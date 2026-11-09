#!/usr/bin/env python3
"""Regression checks for the existing read-only LogRaft OBB warning classifier."""
import unittest
from scripts.t5_classify_obb_guid_logs import PACKAGE, classify_line, classify_streams, _manifest

CODE = '101'
MAIN = f'main.{CODE}.{PACKAGE}.obb'
PATCH = f'patch.{CODE}.{PACKAGE}.obb'
PREFIX = f'/storage/emulated/0/Android/obb/{PACKAGE}/'

def warning(name):
    return "Unable to load GUID for '" + PREFIX + name + "'"

def delivery(with_patch=False):
    return {'package': PACKAGE, 'version_code': CODE,
            'files': [{'name': MAIN}] + ([{'name': PATCH}] if with_patch else [])}

class ObbGuidContract(unittest.TestCase):
    def test_optional_patch_not_a_main_failure(self):
        result = classify_streams([[warning(PATCH)]], delivery=delivery())
        self.assertEqual(result['optional_patch_lookup_not_packaged_count'], 1)
        self.assertEqual(result['main_obb_guid_warning_count'], 0)
        self.assertFalse(result['actual_device_main_obb_mount_verified'])

    def test_declared_main_is_distinct(self):
        result = classify_streams([[warning(MAIN)]], delivery=delivery())
        self.assertEqual(result['main_obb_guid_warning_count'], 1)
        self.assertEqual(result['optional_patch_lookup_not_packaged_count'], 0)

    def test_declared_patch_is_distinct(self):
        self.assertEqual(classify_line(warning(PATCH), code=CODE,
                         logical_files={MAIN, PATCH}), 'declared_patch_obb_guid_warning')

    def test_other_version_not_attributed_to_current_pair(self):
        self.assertEqual(classify_line(warning('main.102.' + PACKAGE + '.obb'),
                         code=CODE, logical_files={MAIN}),
                         'foreign_or_different_version_obb_guid_warning')

    def test_unrelated_warning_not_counted_as_main(self):
        self.assertEqual(classify_line("Unable to load GUID for '/tmp/test.bin'",
                         code=CODE, logical_files={MAIN}), 'other_guid_warning')
        self.assertIsNone(classify_line('No OBB warning', code=CODE, logical_files={MAIN}))

    def test_invalid_delivery_fails_closed(self):
        with self.assertRaises(ValueError):
            _manifest({'package': PACKAGE, 'version_code': CODE,
                       'files': [{'name': PATCH}]})
        with self.assertRaises(ValueError):
            _manifest({'package': PACKAGE, 'version_code': CODE,
                       'files': [{'name': MAIN}, {'name': MAIN}]})

if __name__ == '__main__':
    unittest.main()
