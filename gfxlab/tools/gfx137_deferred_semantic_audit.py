"""Independent, source-free semantic and pixel audit of GFX135 Deferred MRT readbacks.

All inputs are unsigned byte streams in bottom-left RGBA8 readback order.  This
checks a *controlled* source shader fixture, never Unity runtime G-buffer state.
"""

from __future__ import annotations

from hashlib import sha256

CONTROLS = ("native", "flat", "nonmetal")
TARGETS = range(4)
NAMES = tuple(f"{control}-rt{target}" for control in CONTROLS for target in TARGETS)
UNMODIFIED = {"flat": (0, 1, 3), "nonmetal": (2, 3)}


def _pixels_differ(a: bytes, b: bytes) -> int:
    return sum(a[i:i+4] != b[i:i+4] for i in range(0, len(a), 4))


def _coverage(data: bytes) -> bytes:
    return data[3::4]


def _check_controls(images: dict[str, bytes], count: int, title: str) -> dict:
    native = images["native-rt0"]
    alpha = _coverage(native)
    if set(alpha) != {0, 255} or sum(x == 255 for x in alpha) != count:
        raise ValueError(f"{title}: invalid native RT0 coverage")
    if not 0 < count < len(alpha):
        raise ValueError(f"{title}: missing background or geometry")
    if any(_coverage(images[f"{control}-rt0"]) != alpha for control in CONTROLS):
        raise ValueError(f"{title}: RT0 alpha changed across material controls")
    changed = {}
    for mode in CONTROLS[1:]:
        changed[mode] = [
            _pixels_differ(images[f"native-rt{target}"], images[f"{mode}-rt{target}"])
            for target in TARGETS
        ]
        if any(changed[mode][target] for target in UNMODIFIED[mode]):
            raise ValueError(f"{title}: {mode} changed an unrelated render target")
    minimum = max(1, count // 20)
    if (changed["flat"][2] < minimum or changed["nonmetal"][0] < 1
            or changed["nonmetal"][1] < minimum):
        raise ValueError(f"{title}: missing source material response")
    return {"flat": changed["flat"], "nonmetal": changed["nonmetal"]}


def audit_deferred_mrt(
    device: dict[str, bytes], mesa: dict[str, bytes], *,
    minimum_covered: int = 100,
) -> dict:
    """Fail closed on coverage/control errors, report rather than hide RGB drift.

    The reference is independently authenticated by the signed APK's expected
    hashes in the calling ZIP audit.  Source-only unit tests use synthetic data.
    """
    if set(device) != set(NAMES) or set(mesa) != set(NAMES):
        raise ValueError("Expected all 12 Deferred MRT readbacks and references")
    length = len(device[NAMES[0]])
    if length % 4 or length == 0 or any(
        not isinstance(images[name], bytes) or len(images[name]) != length
        for images in (device, mesa) for name in NAMES
    ):
        raise ValueError("Invalid or inconsistent RGBA8 capture length")
    ref_alpha = _coverage(mesa["native-rt0"])
    covered = ref_alpha.count(255)
    if covered < minimum_covered:
        raise ValueError("Reference geometric coverage is too small")
    reference_changes = _check_controls(mesa, covered, "Mesa reference")
    device_alpha = _coverage(device["native-rt0"])
    if device_alpha != ref_alpha:
        raise ValueError("Deferred geometry coverage differs from Mesa")
    device_changes = _check_controls(device, covered, "Adreno")
    covered_indices = [i for i, alpha in enumerate(ref_alpha) if alpha == 255]
    comparisons = {}
    for name in NAMES:
        actual, expected = device[name], mesa[name]
        abs_all = sum(abs(a - b) for a, b in zip(actual, expected, strict=True))
        abs_rgb = sum(
            abs(actual[i*4+c] - expected[i*4+c])
            for i in covered_indices for c in range(3)
        )
        comparisons[name] = {
            "rgba_sha256": sha256(actual).hexdigest(),
            "mesa_rgba_exact": actual == expected,
            "changed_pixels": _pixels_differ(actual, expected),
            "rgba_mean_absolute_error_0_to_255": round(abs_all / length, 6),
            "covered_rgb_mean_absolute_error_0_to_255": round(
                abs_rgb / (len(covered_indices) * 3), 6
            ),
            "max_channel_absolute_error_0_to_255": max(
                abs(a-b) for a, b in zip(actual, expected, strict=True)
            ),
        }
    return {
        "coverage_pixels": covered,
        "coverage_matches_reference": True,
        "rt0_coverage_sha256": sha256(device_alpha).hexdigest(),
        "reference_control_changed_pixels": reference_changes,
        "device_control_changed_pixels": device_changes,
        "targets": comparisons,
        "unity_runtime_gbuffer_layout_verified": False,
        "original_game_pixel_parity": False,
        "phase_closed": False,
    }
