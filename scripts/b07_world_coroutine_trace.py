"""B07: SHA-locked Android first-MoveNext trace for the original world iterator.

No iterator rewrite, yield modification, completion flag or save/network bypass.
The trace runs at the *first MoveNext*, not when the IEnumerator is constructed.
This module contains no original/decompiled game source.
"""
import re

from scripts.b07_probe_original_world_callbacks import (
    _executable_positions,
    fingerprint,
    method_body,
)

ORIGINAL_NETWORK_SHA256 = "080035c137e446828226ed84a23190656b6f235d274436cafb477feaf93caa03"
ORIGINAL_ITERATOR_BODY_SHA256 = "cbd74c24f1c6a86dd50e8d320f4f4142f5b3f3fc5bf8f64ded04710c30c3a140"
METHOD = "WorldHasBeenLoaded"
TRACE_OPERATION = "WorldHasBeenLoaded.firstMoveNext"
ENTRY = (
    "\n#if UNITY_ANDROID && !UNITY_EDITOR\n"
    'RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("world", '
    '"WorldHasBeenLoaded.firstMoveNext", "iterator entry only", false);\n'
    "#endif\n"
)


def _instrument_pinned(source, expected_source_sha, expected_body_sha):
    """Internal synthetic-test seam; production always passes the two original pins."""
    if fingerprint(source) != expected_source_sha:
        raise ValueError("B07 original Raft_Network source SHA mismatch")
    return_type, body = method_body(source, METHOD)
    if return_type != "IEnumerator" or fingerprint(body) != expected_body_sha:
        raise ValueError("B07 original WorldHasBeenLoaded iterator body SHA/type mismatch")
    executable = _executable_positions(body)
    if not re.search(r"\byield\s+(?:return|break)\b", executable):
        raise ValueError("B07 original WorldHasBeenLoaded has no iterator yield")
    if re.search(r"(?m)^\s*#\s*(?:if|elif|else|endif)\b", executable):
        raise ValueError("B07 conditional original iterator cannot be safely traced")
    if TRACE_OPERATION in source or source.count(body) != 1:
        raise ValueError("B07 duplicate/ambiguous coroutine trace source")
    updated = source.replace(body, ENTRY + body, 1)
    updated_type, updated_body = method_body(updated, METHOD)
    if updated_type != "IEnumerator" or updated_body != ENTRY + body:
        raise ValueError("B07 iterator body preservation failed")
    if updated.replace(ENTRY, "", 1) != source:
        raise ValueError("B07 trace removal did not restore original source")
    return updated


def instrument_original_coroutine(source):
    """Only accepts the authenticated, original ILSpy Raft_Network C# input."""
    return _instrument_pinned(source, ORIGINAL_NETWORK_SHA256, ORIGINAL_ITERATOR_BODY_SHA256)
