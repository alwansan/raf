"""Pinned Android local-session adapters; original source remains private."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

from scripts.adapt_original_save_paths import SUFFIX as PATH_SUFFIX
from scripts.probe_original_scene_audio import method_body, _executable_positions

LOCAL = 'RaftAndroid.Platform.LocalPlayerIdentity'
PINS = {
    'SteamManager': '8b45cf7af0e623ec11b5800f18550640334a9ff9705cdae917719d94cca5e3cf',
    'SaveAndLoad': 'b150dd404da48b8012f6659680b3552c11500c4ec97a64ad9aa12c60094568bb',
    'Cheat': '8137618061888b90d79af6dcca8c16aa5128bb5306ae07cab4e87d4a98ffe772',
    'RGD_User': '13f9afdd66f542d122e59558b3cb7b6c404b1950c903a9518aebe0599a59eef6',
    'RGD_Users': '039e902c194b10bca6b8b66f01a48b2673165cb75ffcb7c50ea65a953532903e',
    'Raft_Network': '080035c137e446828226ed84a23190656b6f235d274436cafb477feaf93caa03',
    'PlayFabManager': '474be0341d6d7403d2e9fc85ed79542284f0d5aed1071b179d29d7998f995c6d',
    'BigPictureInputField': 'dce91ddd4c8a9a02da1a4023f5dd4e734e046f11fe2bec12cea830d3781cfd09',
    'TextWriterManager': '01e82abc2c807ea5dbf54e9baf0b8787271619f79f8181e05ee8fae3a744855b',
    'CustomInputConfig': '600bf7dd0bf3d407c73b404fce56a383905f288d4d8d4053f8577eaae73c08bb',
    'Settings': '904c52b337fe951f711e2efc15bfafc4fc77f2a8d2cc9c5bee2f7d14075103ad',
    'Helper': '0858e6739f8bb10f0eea35f933390dc3740f8f1bcfa3b2d5763686691794b3ae',
    'RGD_Settings_Character': '893bf0d7a79ac40db792bff379c07fd0dee692bf46d1c75932b1d72972acd151',
}


CHEAT_METHOD_SHA256 = 'e89739ba461b65b03e78c388193dcfff44a19a41842af9b665a434c39fef1a09'

def fingerprint(text):
    return hashlib.sha256(text.replace('\r\n', '\n').encode()).hexdigest()


def replace_exact(text, old, new, count=1):
    if text.count(old) != count:
        raise ValueError('Original call-site count changed')
    return text.replace(old, new)


def enter(text, method, code):
    pattern = r'(\b' + re.escape(method) + r'\s*\([^)]*\)\s*\{)'
    matches = list(re.finditer(pattern, text))
    if len(matches) != 1:
        raise ValueError('Expected one original method: ' + method)
    pos = matches[0].end()
    return text[:pos] + '\n        if (' + LOCAL + '.Enabled) { ' + code + ' }\n' + text[pos:]


def adapt(name, text):
    original = text.replace(PATH_SUFFIX, '') if name == 'SaveAndLoad' else text
    if name not in PINS or fingerprint(original) != PINS[name]:
        raise ValueError('Unknown original source revision: ' + name)
    result = text
    if name in {'SaveAndLoad', 'RGD_User', 'RGD_Users'}:
        count = 4 if name == 'SaveAndLoad' else 1
        expr = 'SteamUser.GetSteamID().m_SteamID'
        result = replace_exact(result, expr, '(' + LOCAL + '.Enabled ? ' + LOCAL + '.Current : ' + expr + ')', count)
        if name == 'SaveAndLoad':
            attribute = '[Conditional("UNITY_STANDALONE_WIN")]'
            result = replace_exact(result, attribute,
                attribute + '\n\t[Conditional("UNITY_ANDROID")]')

    elif name == 'Cheat':
        # Authenticated ZIP2 Assembly-CSharp.dll (3211776 B), ILSpy11.2
        # exact original Cheat source/method fingerprints from B50 CI.
        # The original call returns a Steamworks.CSteamID *object*, not a
        # numeric m_SteamID property, so retain its object type on Android.
        return_type, body = method_body(result, 'AllowCheatsForLocalPlayer')
        if return_type != 'bool' or hashlib.sha256(body.replace('\r\n', '\n').encode()).hexdigest() != CHEAT_METHOD_SHA256:
            raise ValueError('Unrecognized original Cheat Steam identity method')
        executable = _executable_positions(body)
        calls = list(re.finditer(r'\bSteamUser\s*\.\s*GetSteamID\s*\(\s*\)', executable))
        if len(calls) != 1 or result.count(body) != 1:
            raise ValueError('Original Cheat Steam identity callsite drift')
        match = calls[0]
        call = body[match.start():match.end()]
        guard = '(' + LOCAL + '.Enabled ? new Steamworks.CSteamID(' + LOCAL + '.Current) : ' + call + ')'
        updated_body = body[:match.start()] + guard + body[match.end():]
        result = result.replace(body, updated_body, 1)
        if result.replace(guard, call, 1) != text:
            raise ValueError('Cheat identity guard modified unrelated original source')
    elif name == 'SteamManager':
        anchor = 'UnityEngine.Object.DontDestroyOnLoad(gameObject);'
        result = replace_exact(result, anchor, anchor + '\n        if (' + LOCAL + '.Enabled) { _ = ' + LOCAL + '.Current; m_bInitialized = false; return; }')
    elif name == 'PlayFabManager':
        result = enter(result, 'Start', 'return;')
    elif name == 'BigPictureInputField':
        result = enter(result, 'OnEnable', 'return;')
        result = enter(result, 'OnDisable', 'return;')
        result = replace_exact(result, '&& SteamUtils.IsSteamInBigPictureMode()', '&& !' + LOCAL + '.Enabled && SteamUtils.IsSteamInBigPictureMode()')
    elif name == 'TextWriterManager':
        anchor = 'cbGamepadTextDissmissed = Callback<GamepadTextInputDismissed_t>.Create(GamepadTextDismissed);'
        result = replace_exact(result, anchor, 'if (!' + LOCAL + '.Enabled) ' + anchor)
        result = replace_exact(result, '&& SteamUtils.IsSteamInBigPictureMode()', '&& !' + LOCAL + '.Enabled && SteamUtils.IsSteamInBigPictureMode()')
        result = replace_exact(result, 'cbGamepadTextDissmissed.Dispose();', 'if (!' + LOCAL + '.Enabled) cbGamepadTextDissmissed.Dispose();')
    elif name == 'Settings':
        result = replace_exact(result, 'SteamApps.GetAppBuildId()', '(' + LOCAL + '.Enabled ? 0 : SteamApps.GetAppBuildId())')
    elif name == 'RGD_Settings_Character':
        result = replace_exact(result, 'SteamFriends.GetPersonaName()', '(' + LOCAL + '.Enabled ? "Survivor" : SteamFriends.GetPersonaName())')
    elif name == 'Helper':
        for method in ('GetLargeSteamAvatarFromID', 'GetMediumSteamAvatarFromID', 'GetSmallSteamAvatarFromID'):
            result = enter(result, method, 'return null;')
    elif name == 'CustomInputConfig':
        # Keep the original disabled left-mouse emulation on Android. The
        # authored AndroidTouchPointer owns non-UI touches and emits ONLY
        # synthetic Mouse0; enabling this would duplicate left clicks
        # and could depend on MonoBehaviour OnEnable ordering across scenes.
        if result.count('Input.simulateMouseWithTouches = false;') != 1:
            raise ValueError('Original touch-to-left-mouse policy drift')
    elif name == 'Raft_Network':
        # B07: log only the first iterator MoveNext on Android. Never wrap yield
        # with catch, fake world completion, or modify the original iterator body.
        from scripts.b07_world_coroutine_trace import instrument_original_coroutine
        result = instrument_original_coroutine(result)
        result = enter(result, 'Platform_Init', 'localSteamID = ' + LOCAL + '.Current; SignedIntoPlayfab = false; return;')
        for method in ('Platform_Update', 'Platform_Shutdown'):
            result = enter(result, method, 'return;')
        result = enter(result, 'Platform_LeaveGame', 'CleanupState(); return;')
        result = enter(result, 'Platform_HostGame', 'if (startScene.name != GameSceneName) LoadScene(GameSceneName); return;')
        result = enter(result, 'SetupPlayerNetworkState', 'return;')
        # Keep the original settings initialization and local connection/scene pipeline.
        result = replace_exact(result, 'SteamUserStats.RequestCurrentStats();',
            'if (!' + LOCAL + '.Enabled) SteamUserStats.RequestCurrentStats();\n' +
            '        if (' + LOCAL + '.Enabled && startScene.name == GameSceneName) HostGame(RequestJoinAuthSetting.ALLOW_NONE, string.Empty);')
        result = replace_exact(result, 'SteamFriends.ClearRichPresence();', 'if (!' + LOCAL + '.Enabled) SteamFriends.ClearRichPresence();')
        result = enter(result, 'HostGame', 'joinAuthSetting = RequestJoinAuthSetting.ALLOW_NONE;')
        # This boundary occurs AFTER local RPC delivery; do not return before ParseLocalMessage.
        condition = 'if (PlayFabMultiplayerManager.Get().State != PlayFabMultiplayerManagerState.ConnectedToNetwork)'
        result = replace_exact(result, condition, 'if (' + LOCAL + '.Enabled || PlayFabMultiplayerManager.Get().State != PlayFabMultiplayerManagerState.ConnectedToNetwork)', 3)
        result = enter(result, 'GetPlayFabPlayerFromNetworkId', 'return null;')
    return result


def apply(project, backup, write=False):
    # Both source and backup roots must be physical paths, including parents.
    # Assets.is_symlink() alone misses a symlinked project (and its descendants);
    # resolve().is_relative_to() alone misses a linked backup outside project.
    if any(node.is_symlink() for node in (project, *project.parents)):
        raise ValueError('Unsafe redirected Unity project root')
    if any(node.is_symlink() for node in (backup, *backup.parents)):
        raise ValueError('Unsafe redirected original backup root')
    if backup.resolve().is_relative_to(project.resolve()):
        raise ValueError('Original backup must remain outside imported project')
    assets = project / 'Assets'
    if assets.is_symlink() or not assets.is_dir():
        raise ValueError('Unsafe Unity Assets root')
    plans = []
    for name in PINS:
        paths = [p for p in assets.rglob(name + '.cs') if 'Assembly-CSharp' in p.parts]
        if len(paths) != 1:
            raise ValueError('Expected unique original source: ' + name)
        path = paths[0]
        meta = path.with_suffix('.cs.meta')
        if path.is_symlink() or meta.is_symlink() or (meta.exists() and not meta.is_file()):
            raise ValueError('Regular original source and any existing meta required')
        raw = path.read_bytes()
        result = adapt(name, raw.decode('utf-8-sig')).encode()
        if raw.startswith(b'\xef\xbb\xbf'):
            result = b'\xef\xbb\xbf' + result
        for p in (path, meta) if meta.exists() else (path,):
            if (backup / p.name).exists() or (backup / p.name).is_symlink():
                raise ValueError('Original backup exists; refuse reapplication')
        plans.append((path, meta, raw, meta.read_bytes() if meta.exists() else None, result))
    if write:
        # Backups are the only safe recovery path if a later source rollback
        # fails. Never leave a half-copied backup that blocks the next import.
        if backup.is_symlink() or (backup.exists() and not backup.is_dir()):
            raise ValueError('Original backup directory must be regular')
        backup_existed = backup.exists()
        backup.mkdir(parents=True, exist_ok=True)
        targets = [backup / p.name for path, meta, raw, metadata, result in plans
                   for p in ((path, meta) if metadata is not None else (path,))]
        mutation_started = False
        try:
            for path, meta, raw, metadata, result in plans:
                shutil.copy2(path, backup / path.name)
                if metadata is not None:
                    shutil.copy2(meta, backup / meta.name)
            mutation_started = True
            for path, meta, raw, metadata, result in plans:
                path.write_bytes(result)
                if ((metadata is not None and meta.read_bytes() != metadata) or
                    (metadata is None and meta.exists()) or path.read_bytes() != result):
                    raise ValueError('Installed source/meta validation failed')
        except BaseException:
            # If restoration itself fails, retain *all* backups for recovery;
            # never delete the only known original copies.
            if mutation_started:
                for path, meta, raw, metadata, result in plans:
                    path.write_bytes(raw)
                for path, meta, raw, metadata, result in plans:
                    if path.read_bytes() != raw or (metadata is not None and meta.read_bytes() != metadata):
                        raise ValueError('Original rollback verification failed; backup retained')
            for target in targets:
                if target.is_symlink():
                    raise ValueError('Unsafe linked backup during cleanup')
                target.unlink(missing_ok=True)
            if not backup_existed:
                backup.rmdir()
            raise
    return dict(applied=write, originalSources=len(plans), originalMetasUnchanged=True,
                existingOriginalMetas=sum(p[3] is not None for p in plans), manufacturedMetas=0,
                saveIdentityCallSites=6, cloudAuthenticationFabricated=False,
                localRpcDeliveryPreserved=True, unityRuntimeVerified=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--backup', required=True, type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    print('RAFT_ANDROID_OFFLINE_SOURCE_ADAPTER ' + json.dumps(apply(args.project, args.backup, args.apply), sort_keys=True))

