"""Reject AssetRipper success-with-Unknown-backend before downstream Unity work."""
import argparse
import json
from pathlib import Path
import re
from collections import Counter

KNOWN_ORIGINAL_UNRESOLVED = {'Sirenix.Serialization.GlobalSerializationConfig',
    'SO_PrefabPainter', 'SO_AddressableConnectionData', 'SO_EditorSceneSwitcherInfo'}


def verify(text):
    providers = re.findall(r'During Mono initialization, found (\d+) assemblies', text)
    fallback = 'Could not initialize assembly manager' in text or "'Unknown' scripting backend" in text
    decompiled = 'ScriptExportMode: Decompiled' in text
    completed = 'General : === COMPLETED ===' in text
    unresolved = Counter(re.findall(r'Could not read MonoBehaviour structure for `([^`\r\n]+)`', text))
    mismatches = text.count('layout mismatched binary content')
    result = {'managed_provider_count': int(providers[-1]) if providers else 0,
              'unknown_backend_fallback': fallback, 'decompiled_script_export': decompiled,
              'export_completed': completed,
              'mono_structure_layout_mismatch_lines': mismatches,
              'original_unresolved_structure_types': dict(unresolved)}
    print('RAFT_SCRIPT_IMPORT_FIDELITY ' + json.dumps(result, sort_keys=True))
    if (fallback or not providers or int(providers[-1]) <= 0 or not decompiled or not completed or
            mismatches or set(unresolved) - KNOWN_ORIGINAL_UNRESOLVED):
        raise ValueError('Original managed script import/export was incomplete; refusing Unity build')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--log', type=Path, required=True)
    args = parser.parse_args()
    verify(args.log.read_text(encoding='utf-8-sig', errors='replace'))
