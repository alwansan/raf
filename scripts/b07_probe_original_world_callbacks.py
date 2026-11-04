"""B07: private fail-closed original-world callback provenance.

Print only bounded metadata from a SHA-verified original managed DLL.
Original decompiled source, literals and assembly bytes are never published.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

PINS = {
    "Raft_Network": "080035c137e446828226ed84a23190656b6f235d274436cafb477feaf93caa03",
    "SaveAndLoad": "b150dd404da48b8012f6659680b3552c11500c4ec97a64ad9aa12c60094568bb",
}
ORIGINAL_GAME_MANAGER_SHA256 = "8eb76bcf22028ace2394afe96051ae1e3e59e44f8243c2a68d6b163d80802306"
ORIGINAL_ONWORLD_BODY_SHA256 = "f0ba21d67e1e332656fcc893f095b6a9da12eb6cd5e2be3b27001bb0cf02c835"
ORIGINAL_DLL_BYTES = 3211776
ORIGINAL_DLL_SHA256 = "0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e"
_NON_CODE = re.compile(r'''@"(?:""|[^"])*"|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|//[^\r\n]*|/\*[\s\S]*?\*/''')


def fingerprint(data):
    return hashlib.sha256(data.replace("\r\n", "\n").encode()).hexdigest()


def _executable_positions(source):
    return _NON_CODE.sub(lambda m: re.sub(r"[^\r\n]", " ", m.group()), source)


def method_body(source, name):
    declaration = re.compile(
        r"(?m)^\s*(?:public|private|protected|internal)\s+"
        r"(?:(?:static|virtual|override|sealed|new|async)\s+)*"
        r"(?P<return>[\w<>\[\],.?]+)\s+" + re.escape(name)
        + r"\s*\([^;{}]*\)\s*\{"
    )
    executable = _executable_positions(source)
    matches = list(declaration.finditer(executable))
    if len(matches) != 1:
        raise ValueError("Expected one original " + name + " declaration")
    match = matches[0]
    depth = 1
    for i in range(match.end(), len(executable)):
        if executable[i] == "{":
            depth += 1
        elif executable[i] == "}":
            depth -= 1
            if depth == 0:
                return match["return"], source[match.end():i]
    raise ValueError("Unclosed original " + name + " body")


def assert_original_dll(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size != ORIGINAL_DLL_BYTES:
        raise ValueError("Unverified original managed DLL size/type")
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != ORIGINAL_DLL_SHA256:
        raise ValueError("Original managed DLL SHA mismatch")
    return digest


def _source(root, stem, expected_digest=None):
    matches = list(root.rglob(stem + ".cs"))
    if len(matches) != 1 or not matches[0].is_file() or matches[0].is_symlink():
        raise ValueError("Ambiguous/nonregular original source: " + stem)
    data = matches[0].read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    digest = fingerprint(data)
    if expected_digest is not None and digest != expected_digest:
        raise ValueError("Original source hash changed: " + stem)
    return data, digest


def inspect(source_root, expected_game_manager_sha=None):
    # GameManager hash is derived from the authenticated DLL, then exposed
    # for subsequent pinning; do not assume any unverified source is original.
    network, network_sha = _source(source_root, "Raft_Network", PINS["Raft_Network"])
    save, save_sha = _source(source_root, "SaveAndLoad", PINS["SaveAndLoad"])
    manager, manager_sha = _source(source_root, "GameManager", expected_game_manager_sha or ORIGINAL_GAME_MANAGER_SHA256)
    if expected_game_manager_sha is None and fingerprint(method_body(manager, "OnWorldRecieved")[1]) != ORIGINAL_ONWORLD_BODY_SHA256:
        raise ValueError("Unknown original GameManager callback body")
    net_type, net_body = method_body(network, "WorldHasBeenLoaded")
    manager_type, manager_body = method_body(manager, "OnWorldRecieved")
    save_type, save_body = method_body(save, "SaveGame")
    net_code = _executable_positions(net_body)
    manager_code = _executable_positions(manager_body)
    save_code = _executable_positions(save_body)
    broadcasts = list(re.finditer(r"\bHelper\s*\.\s*BroadCastToScene\s*\(", net_code))
    completions = list(re.finditer(r"\bWorldHasBeenRecieved\s*=\s*true\s*;", net_code))
    saves = list(re.finditer(r"\bSaveGame\s*\(", manager_code))
    stats = list(re.finditer(r"\bSteamUserStats\s*\.\s*StoreStats\s*\(\s*\)\s*;", save_code))
    if net_type != "IEnumerator" or manager_type != "void" or save_type != "void":
        raise ValueError("Original world/save return contract changed")
    if len(completions) != 1 or not any(x.start() < completions[0].start() for x in broadcasts):
        raise ValueError("Original scene-ready broadcast/completion order unrecognized")
    if len(saves) != 3:
        # Redacted diagnostics to explain an actual original-source contract
        # mismatch without logging any original body, snippets or literals.
        print("B07_CALLBACK_MISMATCH " + json.dumps({
            "manager_sha256": manager_sha,
            "onworld_body_sha256": fingerprint(manager_body),
            "onworld_body_length": len(manager_body),
            "savegame_call_tokens_in_body": len(saves),
            "savegame_identifiers_in_body": len(re.findall(r"\bSaveGame\b", manager_code)),
            "savegame_identifiers_in_class": len(re.findall(r"\bSaveGame\b", _executable_positions(manager))),
            "saveandload_identifiers_in_body": len(re.findall(r"\bSaveAndLoad\b", manager_code)),
            "world_savegame_identifiers_in_body": len(re.findall(r"\bSaveWorld\b", manager_code)),
            "world_received_signatures_in_class": len(re.findall(r"\bOnWorldRecieved\s*\(", _executable_positions(manager))),
            "literal_or_comment_span_masked": sum(a != b for a, b in zip(manager_body, manager_code)),
            "diagnostic_only": True,
        }, sort_keys=True))
        raise ValueError("Original OnWorldRecieved SaveGame callsite unrecognized")
    if len(stats) != 1:
        raise ValueError("Original SaveGame stats boundary unrecognized")
    for name, code in (("WorldHasBeenLoaded", net_code), ("OnWorldRecieved", manager_code), ("SaveGame", save_code)):
        if re.search(r"(?m)^\s*#\s*(?:if|elif|else|endif)\b", code):
            raise ValueError("Conditional compilation in original " + name)
    return {
        "original_network_sha256": network_sha,
        "original_save_sha256": save_sha,
        "original_game_manager_sha256": manager_sha,
        "world_coroutine_body_sha256": fingerprint(net_body),
        "world_callback_body_sha256": fingerprint(manager_body),
        "savegame_body_sha256": fingerprint(save_body),
        "broadcast_before_completion": True,
        "on_world_received_savegame_calls": len(saves),
        "savegame_store_stats_calls": len(stats),
        "callback_exception_can_interrupt_coroutine": not bool(re.search(r"\bcatch\s*\(", net_code)),
        "observed_on_device": False,
        "original_sources_modified": False,
        "limits": "Lexical source contract, not same-event dispatch, host scheduling, IO, runtime or RGD roundtrip",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--original-managed-dll", type=Path, required=True)
    p.add_argument("--source", type=Path, required=True)
    args = p.parse_args()
    assert_original_dll(args.original_managed_dll)
    print("B07_LOCAL_WORLD_CALLBACK_PROBE " + json.dumps(inspect(args.source), sort_keys=True))


if __name__ == "__main__":
    main()
