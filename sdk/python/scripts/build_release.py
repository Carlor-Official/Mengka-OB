"""Build the reviewed public SDK and echo example, without runtime files."""
from pathlib import Path
import argparse
import hashlib
import io
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RELEASES = ROOT.parent / "releases"
NAME = "mengka-ob-python-sdk.zip"
MODULES = (
    "__init__.py", "assets.py", "console_login.py", "helpers.py", "message.py",
    "module.py", "registry.py", "runtime.py", "state.py", "web.py",
)


def release_files():
    files = {f"obp/{name}": ROOT / "obp" / name for name in MODULES}
    files.update({name: ROOT / "examples" / "echo" / name for name in (
        "main.py", "echo_plugin.py", "mengka.plugin.json",
    )})
    files.update({name: ROOT / name for name in (
        "README.md", "requirements.txt", "contract-source.json",
    )})
    return files


def archive_bytes():
    buffer = io.BytesIO()
    # ZIP_STORED keeps output identical across Python/zlib versions. This SDK is small.
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, path in sorted(release_files().items()):
            info = zipfile.ZipInfo(name, (2026, 11, 27, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    return buffer.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify committed ZIP and SHA256 without writing")
    args = parser.parse_args()
    data = archive_bytes()
    digest = hashlib.sha256(data).hexdigest()
    checksum = f"{digest}  {NAME}\n".encode("ascii")
    archive = RELEASES / NAME
    sha = RELEASES / (NAME + ".sha256")
    if args.check:
        if not archive.exists() or archive.read_bytes() != data or not sha.exists() or sha.read_bytes() != checksum:
            raise SystemExit("SDK distribution is missing or stale; run build_release.py")
        print("SDK source, archive and SHA256 match")
    else:
        RELEASES.mkdir(parents=True, exist_ok=True)
        archive.write_bytes(data)
        sha.write_bytes(checksum)
        print(f"Built {NAME}: {len(data)} bytes; SHA256 {digest}")


if __name__ == "__main__":
    main()
