# (c) Copyright 2019 Trent Hauck
# All Rights Reserved

import unittest
from pathlib import Path
from typing import List, NamedTuple

from click.testing import CliRunner
from yeyo import cli
from yeyo.cli import DEFAULT_CONFIG_PATH, STARTING_FILE, STARTING_VERSION
from yeyo.config import YeyoConfig


class TestCLI(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_version_bumps(self):
        class TestRow(NamedTuple):
            expected_config: YeyoConfig
            command: List[str]

        test_rows = [
            TestRow(YeyoConfig.from_version_string(STARTING_VERSION, {STARTING_FILE}), ["init"]),
            TestRow(
                YeyoConfig.from_version_string("0.0.0-dev.2", {STARTING_FILE}),
                ["bump", "prerelease"],
            ),
            TestRow(
                YeyoConfig.from_version_string("0.0.0-a.1", {STARTING_FILE}),
                ["bump", "prerelease", "-p", "a"],
            ),
            TestRow(YeyoConfig.from_version_string("0.0.0", {STARTING_FILE}), ["bump", "finalize"]),
            TestRow(
                YeyoConfig.from_version_string("0.0.1-dev.1", {STARTING_FILE}),
                ["bump", "patch", "--prerel"],
            ),
        ]

        runner = CliRunner()
        with runner.isolated_filesystem():
            for row in test_rows:

                result = runner.invoke(cli.main, row.command)
                self.assertEqual(result.exit_code, 0)

                yc = YeyoConfig.from_json(Path(DEFAULT_CONFIG_PATH))

                self.assertEqual(yc, row.expected_config)
                self.assertFilesInConfigHaveVersion(yc)

    def assertFilesInConfigHaveVersion(self, config):

        for f in config.files:
            with open(f) as fhandler:
                contents = fhandler.read()
                self.assertTrue(config.version_string in contents)
