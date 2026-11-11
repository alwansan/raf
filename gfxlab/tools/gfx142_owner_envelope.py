"""GFX142: authenticated one-time owner delivery envelope for private APK.

Only the recipient's public X.509 certificate is stored in the repository.
The matching RSA private key MUST NOT enter the repository or GitHub Actions.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import subprocess


def digest(path: Path) -> str:
    h = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def checked(args: list[str]) -> None:
    p = subprocess.run(args, capture_output=True, text=True, check=False)
    if p.returncode:
        # No private binary content is included in subprocess arguments.
        raise RuntimeError(f"GFX142 openssl command failed: {p.stderr[-700:]}")


def encrypt_private_apk(signed: Path, certificate: Path, envelope: Path) -> dict:
    """AES-256-GCM CMS AuthEnvelopedData, RSA cert recipient; fail closed."""
    if not signed.is_file() or signed.stat().st_size < 1_000_000:
        raise ValueError("Original signed APK missing or unexpectedly small")
    if not certificate.is_file() or envelope.exists():
        raise ValueError("Missing recipient certificate or envelope output already exists")
    if signed.resolve() == envelope.resolve():
        raise ValueError("Refusing to overwrite signed original APK")
    checked(["openssl", "x509", "-in", str(certificate), "-noout", "-checkend", "0"])
    try:
        checked(["openssl", "cms", "-encrypt", "-binary", "-aes-256-gcm",
                 "-in", str(signed), "-out", str(envelope),
                 "-outform", "DER", str(certificate)])
        if envelope.stat().st_size <= signed.stat().st_size:
            raise ValueError("CMS envelope was unexpectedly shorter than signed APK")
        return {
            "private_owner_delivery_encrypted_only": True,
            "encrypted_artifact_format": "CMS DER AuthEnvelopedData",
            "encrypted_artifact_algorithm": "AES-256-GCM with RSA recipient certificate",
            "recipient_public_certificate_sha256": digest(certificate),
            "encrypted_apk_size_bytes": envelope.stat().st_size,
            "encrypted_apk_sha256": digest(envelope),
            "original_apk_in_public_artifacts": False,
        }
    except Exception:
        envelope.unlink(missing_ok=True)
        raise
