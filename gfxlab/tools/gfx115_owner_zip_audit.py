"""Audit the GFX115 phone depth images and vertex results against the signed APK."""
import argparse
import json

from gfxlab.tools.gfx114_owner_zip_audit import audit


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("owner_zip")
    parser.add_argument("signed_apk")
    args = parser.parse_args()
    print(json.dumps(audit(args.owner_zip,args.signed_apk,experiment="GFX115"),indent=2))
