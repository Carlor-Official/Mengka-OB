import hashlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_release", ROOT / "scripts/build_release.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class DistributionTests(unittest.TestCase):
    def test_archive_matches_source_and_checksum(self):
        data = (ROOT.parent / "releases" / build.NAME).read_bytes()
        self.assertEqual(data, build.archive_bytes())
        checksum = (ROOT.parent / "releases" / (build.NAME + ".sha256")).read_text()
        self.assertEqual(checksum, f"{hashlib.sha256(data).hexdigest()}  {build.NAME}\n")

    def test_only_public_sdk_and_example_are_packaged(self):
        expected = {f"obp/{name}" for name in (
            "__init__.py", "assets.py", "console_login.py", "helpers.py", "message.py",
            "module.py", "registry.py", "runtime.py", "state.py", "web.py",
        )} | {"main.py", "echo_plugin.py", "mengka.plugin.json", "requirements.txt", "README.md", "contract-source.json"}
        with zipfile.ZipFile(io.BytesIO(build.archive_bytes())) as archive:
            self.assertEqual(set(archive.namelist()), expected)
            self.assertEqual(len(archive.namelist()), len(expected))
            manifest = json.loads(archive.read("mengka.plugin.json"))
            self.assertEqual(manifest["permissions"]["actions"], ["send_message"])
            self.assertEqual(manifest["entrypoints"]["any"]["path"], "main.py")
            self.assertEqual(manifest["protocol"], "obp/1")
            self.assertNotIn("app_id", manifest)
            self.assertNotIn("token", manifest)

    def test_runtime_matches_reviewed_framework_snapshot(self):
        source = json.loads((ROOT / "contract-source.json").read_text())
        self.assertEqual(source["frameworkVersion"], "1.0.4")
        self.assertEqual(len(source["moduleSHA256"]), 10)
        for name, digest in source["moduleSHA256"].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest, name)


if __name__ == "__main__":
    unittest.main()
