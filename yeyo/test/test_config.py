# (c) Copyright 2018 Trent Hauck
# All Rights Reserved

import tempfile
import unittest
from pathlib import Path

from yeyo.config import DEFAULT_COMMIT_TEMPLATE
from yeyo.config import DEFAULT_TAG_TEMPLATE
from yeyo.config import YeyoConfig


class TestYeyoConfig(unittest.TestCase):
    def test_to_json_roundtrip(self):

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_path = tmp_path / "test.json"

            yc = YeyoConfig.from_version_string(
                "0.1.1", DEFAULT_COMMIT_TEMPLATE, DEFAULT_TAG_TEMPLATE
            )
            yc.to_json(config_path)

            yc2 = YeyoConfig.from_json(config_path)
            self.assertEqual(yc, yc2)

    def test_replace_version(self):

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            version = tmp_path / "VERSION"
            config_path = tmp_path / "test.json"

            yc = YeyoConfig.from_version_string(
                "0.1.1", DEFAULT_COMMIT_TEMPLATE, DEFAULT_TAG_TEMPLATE, {version}
            )
            new_yc = YeyoConfig.from_version_string(
                "0.2.1", DEFAULT_COMMIT_TEMPLATE, DEFAULT_COMMIT_TEMPLATE, {version}
            )

            with open(version, "w") as f:
                f.write(yc.version_string)

            new_yc.update(yc, config_path)

            with open(version) as f:
                lines = f.readlines()[0]

            self.assertEqual(new_yc.version_string, lines.strip("\n"))

    def test_remove_file(self):

        paths = {Path("a"), Path("b")}

        yc = YeyoConfig.from_version_string(
            "0.1.1", DEFAULT_COMMIT_TEMPLATE, DEFAULT_TAG_TEMPLATE, paths
        )
        new_yc = yc.remove_file(Path("a"))

        self.assertEqual(new_yc.files, {Path("b")})
        self.assertEqual(yc.files, paths)

    def test_add_file(self):

        paths = {Path("a")}
        new_path = Path("b")

        yc = YeyoConfig.from_version_string(
            "0.1.1", DEFAULT_COMMIT_TEMPLATE, DEFAULT_TAG_TEMPLATE, paths
        )
        new_yc = yc.add_file(new_path)

        self.assertEqual(yc.files, paths)

        # `add` is in-place so do after the first assert.
        paths.add(new_path)
        self.assertEqual(new_yc.files, paths)
