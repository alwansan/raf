#!/usr/bin/env python3
"""Bounded, fail-closed chronology audit of a LogRaft session summary.

Source is an existing owner-approved CL JSON summary, never raw game log text.
The report proves the order of OBSERVED messages only. Neither Unity kernel
identity nor shader correctness follows from this timing correlation.
"""
import argparse
import hashlib
import json
import os
import re
import stat
from pathlib import Path

MAX_BYTES = 131_072
SOURCE_CL_COMMIT = "61f71ceb3b9e6f16c8fb300656f6e6baf32b33e8"
DEFAULT_SESSION = "20261108-164850-270"
DEFAULT_PACKAGE = "com.alwansan.raft.androidtest"


class DupAware(dict):
    def __init__(self, pairs):
        super().__init__()
        self.duplicate_count = 0
        for key, value in pairs:
            if key in self:
                self.duplicate_count += 1
            self[key] = value


def validate_duplicates(root):
    """Allow known non-authoritative last_sample noise, never root/evidence drift."""
    def walk(value, path):
        result = 0
        if isinstance(value, DupAware):
            if value.duplicate_count:
                if not path or path[0] != "last_sample":
                    raise ValueError("duplicate authoritative JSON key")
                result += value.duplicate_count
            for key, item in value.items():
                result += walk(item, path + (key,))
        elif isinstance(value, list):
            for item in value:
                result += walk(item, path)
        return result
    return walk(root, ())


def load_summary(path):
    """Reject symlinks, FIFOs, oversized/in-place-mutated or truncated inputs."""
    path = Path(path)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NONBLOCK", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    elif path.is_symlink():
        raise ValueError("symlink source refused")
    fd = os.open(path, flags)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or not 0 < before.st_size <= MAX_BYTES:
            raise ValueError("invalid summary file type/size")
        remaining = before.st_size
        blocks = []
        while remaining:
            chunk = os.read(fd, min(8192, remaining))
            if not chunk:
                raise ValueError("truncated summary")
            blocks.append(chunk)
            remaining -= len(chunk)
        if os.read(fd, 1):
            raise ValueError("summary grew during read")
        after = os.fstat(fd)
        if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
                after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise ValueError("summary changed during read")
        raw = b"".join(blocks)
        parsed = json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=DupAware)
        ignored = validate_duplicates(parsed)
        if not isinstance(parsed, dict):
            raise ValueError("summary root must be object")
        return parsed, ignored, hashlib.sha256(raw).hexdigest()
    finally:
        os.close(fd)


def section(parent, key):
    child = parent.get(key) if isinstance(parent, dict) else None
    if not isinstance(child, dict):
        raise ValueError("missing structured field: " + key)
    return child


def count(obj, key):
    x = obj.get(key)
    if type(x) is not int or x < 0 or x > 1_000_000_000:
        raise ValueError("invalid counter: " + key)
    return x


def stamp(obj, key):
    x = obj.get(key)
    if type(x) is not int or not 1_000_000_000_000 < x < 5_000_000_000_000:
        raise ValueError("invalid event timestamp: " + key)
    return x


def analyze(data, session=DEFAULT_SESSION, source_commit=SOURCE_CL_COMMIT,
            ignored_last_sample_duplicates=0, input_sha256=None):
    if not re.fullmatch(r"[0-9]{8}-[0-9]{6}-[0-9]{3}", session):
        raise ValueError("bad expected session")
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("bad source commit")
    if type(data.get("schema")) is not int or data.get("schema") != 1 or data.get("session") != session:
        raise ValueError("wrong summary schema/session")
    if data.get("target_package") != DEFAULT_PACKAGE:
        raise ValueError("wrong app package")
    final = section(data, "final_error_category_breakdown")
    errors = [section(final, name) for name in (
        "ultimate_water_invalid_pass", "water_fft_invalid_compute_kernel")]
    milestones = section(data, "final_game_milestones")
    early = section(milestones, "raft_android_early_startup_log_observed")
    world = section(milestones, "world_loaded_message_observed")
    fmod = section(milestones, "fmod_bootstrap_log_observed")
    render = section(data, "final_render_failure_breakdown")
    materials = section(render, "ultimate_water_invalid_pass_by_material")
    kernels = section(render, "invalid_kernel_index_root_lines")
    performance = section(data, "performance_statistics")

    water_count, kernel_count = (count(obj, "count") for obj in errors)
    water_first, kernel_first = (stamp(obj, "first_observed_unix_ms") for obj in errors)
    end = stamp(data, "end_unix_ms")
    world_first = stamp(world, "first_observed_unix_ms")
    early_first = stamp(early, "first_observed_unix_ms")
    fmod_first = stamp(fmod, "first_observed_unix_ms")
    if min(count(early, "count"), count(world, "count"), count(fmod, "count")) == 0:
        raise ValueError("missing observed startup/world milestone")
    if not (fmod_first <= early_first <= world_first <= end):
        raise ValueError("invalid milestone order")
    for obj in errors:
        first, last = stamp(obj, "first_observed_unix_ms"), stamp(obj, "last_observed_unix_ms")
        if not first <= last <= end:
            raise ValueError("event range outside session end")
    counts = {name: count(materials, name) for name in (
        "spectrum", "foam_global", "subsurface_blur", "utility_noise", "other_ultimate_water")}
    kernel_indices = {name: count(kernels, name) for name in ("index_6", "other_index")}
    if sum(counts.values()) != water_count or sum(kernel_indices.values()) != kernel_count:
        raise ValueError("final root breakdown inconsistent")
    # Real CL summaries store immutable stop-time counters and a second copy
    # of the final groups under stop_time_android_process_exit_info, not root.
    # Require the two independent published views to agree before reporting.
    stop = section(data, "stop_time_android_process_exit_info")
    stopped_groups = section(stop, "final_error_groups")
    stopped_render = section(stop, "final_render_failure_breakdown")
    for name, expected in zip(
            ("ultimate_water_invalid_pass", "water_fft_invalid_compute_kernel"), errors):
        if section(stopped_groups, name) != expected:
            raise ValueError("stop-time root groups inconsistent")
    if stopped_render != render:
        raise ValueError("stop-time render breakdown inconsistent")
    if (count(stop, "final_shader_pass_errors_total") != water_count or
            count(stop, "final_compute_kernel_errors_total") != kernel_count):
        raise ValueError("stop-time session totals inconsistent")

    sampled_water = count(performance, "shader_pass_errors_total_at_last_sample")
    sampled_kernel = count(performance, "compute_kernel_errors_total_at_last_sample")
    if sampled_water > water_count or sampled_kernel > kernel_count:
        raise ValueError("sample counts exceed final counts")
    if type(ignored_last_sample_duplicates) is not int or ignored_last_sample_duplicates < 0:
        raise ValueError("invalid duplicate count")
    if input_sha256 is not None and not re.fullmatch(r"[a-f0-9]{64}", input_sha256):
        raise ValueError("invalid input SHA")
    return {
        "schema": 1,
        "session": session,
        "cl_commit": source_commit,
        "summary_sha256": input_sha256,
        "root_counts": {"water_invalid_pass": water_count,
                        "fft_invalid_compute_kernel": kernel_count,
                        "materials": counts, "invalid_kernel_indices": kernel_indices},
        "timing_ms": {
            "first_water_before_world_loaded": world_first - water_first,
            "first_fft_before_world_loaded": world_first - kernel_first,
            "fft_first_after_water_first": kernel_first - water_first,
            "first_water_after_early_startup": water_first - early_first,
        },
        "last_sample_underreports_final_by": {
            "water_invalid_pass": water_count - sampled_water,
            "fft_invalid_compute_kernel": kernel_count - sampled_kernel,
        },
        "first_errors_observed_before_world_loaded":
            water_first < world_first and kernel_first < world_first,
        "non_authoritative_last_sample_duplicate_keys": ignored_last_sample_duplicates,
        "limits": {
            "only_observed_log_order": True,
            "full_preworld_error_count_known": False,
            "os_logcat_delivery_complete_proven": False,
            "kernel6_original_unity_identity_proven": False,
            "unity_findkernel_dispatch_proven": False,
            "device_image_shader_fixed_proven": False,
            "gpu_busy_is_unity_fps": False,
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path)
    parser.add_argument("--session", default=DEFAULT_SESSION)
    parser.add_argument("--source-commit", default=SOURCE_CL_COMMIT)
    args = parser.parse_args(argv)
    try:
        data, ignored, checksum = load_summary(args.summary)
        report = analyze(data, args.session, args.source_commit, ignored, checksum)
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        parser.exit(2, "Invalid session summary: " + type(exc).__name__ + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
