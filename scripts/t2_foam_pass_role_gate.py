"""Fail-closed validator for privacy-safe per-pass Foam Blit role summaries.

Static IL classification only: no claim of actual textures, pixels or ShaderLab.
"""
import json
import sys

SOURCES = {"Texture", "RenderTexture", "unknown"}
DESTINATIONS = {"RenderTexture", "null", "unknown"}

def validate(report):
    if not isinstance(report, dict) or set(report) != {"sites"}:
        raise ValueError("unexpected report shape")
    sites = report["sites"]
    if not isinstance(sites, list) or len(sites) != 2:
        raise ValueError("expected exactly two Blit sites")
    seen = set()
    for site in sites:
        if not isinstance(site, dict) or set(site) != {"pass", "source", "destination"}:
            raise ValueError("unexpected site fields")
        p = site["pass"]
        if type(p) is not int or p not in (0, 1) or p in seen:
            raise ValueError("pass identity must be unique 0 or 1")
        seen.add(p)
        if type(site["source"]) is not str or site["source"] not in SOURCES:
            raise ValueError("invalid source role")
        if type(site["destination"]) is not str or site["destination"] not in DESTINATIONS:
            raise ValueError("invalid destination role")
    return {site["pass"]: (site["source"], site["destination"]) for site in sites}

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: t2_foam_pass_role_gate.py safe_report.json")
    with open(sys.argv[1], encoding="utf-8") as handle:
        roles = validate(json.load(handle))
    print(json.dumps({"pass0": list(roles[0]), "pass1": list(roles[1]),
                      "classification_only": True}, sort_keys=True))

if __name__ == "__main__":
    main()
