"""Verify the handset report for the 15 M02 poses against the delivered APK."""
import argparse
import json

from gfxlab.tools.gfx109_owner_zip_audit import audit
from gfxlab.tools.gfx112_animated_payload import EXPECTED


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("owner_zip")
    parser.add_argument("signed_apk")
    args = parser.parse_args()
    print(json.dumps(audit(args.owner_zip, args.signed_apk, experiment="GFX112",
                           expected={name: (1666, 8) for name in EXPECTED}), indent=2))
