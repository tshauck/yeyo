# (c) Copyright 2018 Trent Hauck
# All Rights Reserved

import tempfile
import unittest
from pathlib import Path

from yeyo.config import YeyoConfig


class TestYeyoConfig(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_to_json_roundtrip(self):

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_path = tmp_path / "test.json"

            yc = YeyoConfig.from_version_string("0.1.1")
            yc.to_json(config_path)

            yc2 = YeyoConfig.from_json(config_path)
            self.assertEqual(yc, yc2)

    def test_replace_version(self):

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            version = tmp_path / "VERSION"

            yc = YeyoConfig.from_version_string("0.1.1", {version})
            new_yc = YeyoConfig.from_version_string("0.2.1", {version})

            with open(version, "w") as f:
                f.write(yc.version_string)

            new_yc.update_prior_config(yc)

            with open(version) as f:
                lines = f.readlines()[0]

            self.assertEqual(new_yc.version_string, lines.strip("\n"))
