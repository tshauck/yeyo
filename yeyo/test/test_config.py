# (c) Copyright 2018 Trent Hauck
# All Rights Reserved

import tempfile
import unittest
from pathlib import Path

import semver
import pytest

from yeyo.config import DEFAULT_COMMIT_TEMPLATE
from yeyo.config import DEFAULT_TAG_TEMPLATE
from yeyo.config import YeyoConfig
from yeyo.config import FileVersion
from yeyo.config import YEYO_VERSION_TEMPLATE


version_replace_test = [
    (
        Path("."),
        YEYO_VERSION_TEMPLATE,
        "0.0.1",
        semver.VersionInfo(0, 0, 1),
        "0.0.2",
        semver.VersionInfo(0, 0, 2),
    ),
    (
        Path("."),
        f"prefix_{YEYO_VERSION_TEMPLATE}",
        "prefix_0.0.1",
        semver.VersionInfo(0, 0, 1),
        "prefix_0.0.2",
        semver.VersionInfo(0, 0, 2),
    ),
    (
        Path("."),
        f"prefix_{YEYO_VERSION_TEMPLATE}",
        "no version",
        semver.VersionInfo(0, 0, 1),
        "no version",
        semver.VersionInfo(0, 0, 2),
    ),
]


@pytest.mark.parametrize("path,template,actual,v1,expected,v2", version_replace_test)
def test_file_version_replace(path, template, actual, v1, expected, v2):
    """Test the string replace"""

    fv = FileVersion(file_path=path, match_template=template)
    test_str = fv.replace(actual, v1, v2)
    assert test_str == expected


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
                "0.1.1", DEFAULT_COMMIT_TEMPLATE, DEFAULT_TAG_TEMPLATE
            ).add_file(version, YEYO_VERSION_TEMPLATE)

            new_yc = YeyoConfig.from_version_string(
                "0.2.1", DEFAULT_COMMIT_TEMPLATE, DEFAULT_COMMIT_TEMPLATE
            ).add_file(version, YEYO_VERSION_TEMPLATE)

            with open(version, "w") as f:
                f.write(yc.version_string)

            new_yc.update(yc, config_path)

            with open(version) as f:
                lines = f.readlines()[0]

            self.assertEqual(new_yc.version_string, lines.strip("\n"))

    def test_remove_file(self):

        a = Path("a")
        b = Path("b")

        yc = YeyoConfig.from_version_string("0.1.1", DEFAULT_COMMIT_TEMPLATE, DEFAULT_TAG_TEMPLATE)
        yc = yc.add_file(a, YEYO_VERSION_TEMPLATE)
        yc = yc.add_file(b, YEYO_VERSION_TEMPLATE)
        new_yc = yc.remove_file(a)

        file_version = list(new_yc.files)[0]
        self.assertEqual(file_version.file_path, Path("b"))

    def test_add_file(self):

        paths = {FileVersion(Path("a"), YEYO_VERSION_TEMPLATE)}
        new_path = Path("b")

        yc = YeyoConfig.from_version_string(
            "0.1.1", DEFAULT_COMMIT_TEMPLATE, DEFAULT_TAG_TEMPLATE, paths
        )
        new_yc = yc.add_file(new_path, YEYO_VERSION_TEMPLATE)

        self.assertEqual(yc.files, paths)

        # `add` is in-place so do after the first assert.
        paths.add(FileVersion(new_path, YEYO_VERSION_TEMPLATE))
        self.assertEqual(new_yc.files, paths)
