#!/usr/bin/env python3
"""INPUT-005: conservative stage correlation for opt-in, sanitized mouse traces.

Accepted line format:
 T4_MOUSE_STAGE frame=42 stage=android button=left
Stages: android, unity, raft. Buttons: left, right, middle, wheel.
The trace format is an instrumentation contract, not proof that the game emits it.
No raw device/game data is included. Absence never proves a missing callback.
"""
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

STAGES = ("android", "unity", "raft")
BUTTONS = ("left", "right", "middle", "wheel")
TOKEN = re.compile(r"(?<!\w)(frame|stage|button)=([A-Za-z0-9_-]+)\b")


def analyze(lines):
    frames = defaultdict(lambda: defaultdict(set))
    malformed = 0
    for line in lines:
        if "T4_MOUSE_STAGE" not in line:
            continue
        fields = dict(TOKEN.findall(line))
        frame = fields.get("frame", "")
        stage = fields.get("stage")
        button = fields.get("button")
        if not frame.isdecimal() or stage not in STAGES or button not in BUTTONS:
            malformed += 1
            continue
        frames[int(frame)][button].add(stage)

    result = {}
    for button in BUTTONS:
        observed = [stages[button] for stages in frames.values() if button in stages]
        counts = {stage: sum(stage in entry for entry in observed) for stage in STAGES}
        gaps = {
            "android_without_unity_same_frame": sum("android" in x and "unity" not in x for x in observed),
            "unity_without_raft_same_frame": sum("unity" in x and "raft" not in x for x in observed),
        }
        result[button] = {"observed_frames": len(observed), "stage_frames": counts,
                          "uncorrelated_same_frame": gaps,
                          "device_success_proven": False}
    return {"buttons": result, "malformed_markers": malformed,
            "frames_with_markers": len(frames), "device_success_proven": False,
            "limitations": "Same-frame absence is not failure: callbacks may cross frame boundaries, be sampled, or not be instrumented. Signed Android gameplay and keyboard preservation require independent phone evidence."}


def self_test():
    sample = ["T4_MOUSE_STAGE frame=10 stage=android button=left",
              "T4_MOUSE_STAGE frame=10 stage=unity button=left",
              "T4_MOUSE_STAGE frame=11 stage=android button=right",
              "T4_MOUSE_STAGE frame=12 stage=raft button=wheel",
              "T4_MOUSE_STAGE frame=x stage=android button=middle"]
    result = analyze(sample)
    assert result["buttons"]["left"]["stage_frames"]["unity"] == 1
    assert result["buttons"]["right"]["uncorrelated_same_frame"]["android_without_unity_same_frame"] == 1
    assert result["buttons"]["wheel"]["stage_frames"]["raft"] == 1
    assert result["malformed_markers"] == 1
    assert not result["device_success_proven"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("PASS: mouse boundary trace self-test")
    elif args.log:
        with args.log.open(encoding="utf-8", errors="replace") as handle:
            print(json.dumps(analyze(handle), indent=2))
    else:
        parser.error("provide a sanitized log or --self-test")


if __name__ == "__main__":
    main()
