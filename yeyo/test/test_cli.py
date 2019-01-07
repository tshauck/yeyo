# (c) Copyright 2019 Trent Hauck
# All Rights Reserved

import unittest
from pathlib import Path
from typing import List
from typing import NamedTuple
from typing import Optional

import git
from click.testing import CliRunner
from semver import VersionInfo

from yeyo import cli
from yeyo.cli import STARTING_VERSION
from yeyo.config import DEFAULT_COMMIT_TEMPLATE
from yeyo.config import DEFAULT_CONFIG_PATH
from yeyo.config import DEFAULT_TAG_TEMPLATE
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
            expected_git_tag: Optional[str] = None

        test_file = Path("VERSION")

        test_rows = [
            TestRow(
                YeyoConfig.from_version_string(
                    STARTING_VERSION, DEFAULT_TAG_TEMPLATE, DEFAULT_COMMIT_TEMPLATE, {test_file}
                ),
                ["init", "-f", str(test_file)],
            ),
            TestRow(
                YeyoConfig.from_version_string(
                    "0.0.0-dev.2", DEFAULT_TAG_TEMPLATE, DEFAULT_COMMIT_TEMPLATE, {test_file}
                ),
                ["bump", "prerelease", "--git-tag-after"],
                expected_git_tag="0.0.0-dev.2",
            ),
            TestRow(
                YeyoConfig.from_version_string(
                    "0.0.0-a.1", DEFAULT_TAG_TEMPLATE, DEFAULT_COMMIT_TEMPLATE, {test_file}
                ),
                ["bump", "prerelease", "-p", "a", "--git-tag-after"],
                expected_git_tag="0.0.0-a.1",
            ),
            TestRow(
                YeyoConfig.from_version_string(
                    "0.0.0", DEFAULT_TAG_TEMPLATE, DEFAULT_COMMIT_TEMPLATE, {test_file}
                ),
                ["bump", "finalize", "--git-tag-after"],
                expected_git_tag="0.0.0",
            ),
            TestRow(
                YeyoConfig.from_version_string(
                    "0.0.1-dev.1", DEFAULT_TAG_TEMPLATE, DEFAULT_COMMIT_TEMPLATE, {test_file}
                ),
                ["bump", "patch", "--prerel", "--git-tag-before"],
                expected_git_tag="0.0.0",
            ),
        ]

        runner = CliRunner()
        with runner.isolated_filesystem():
            repo = git.Repo.init(".", "bare-repo")

            with open(test_file, "w") as f:
                f.write(STARTING_VERSION)

            for row in test_rows:
                result = runner.invoke(cli.main, row.command)
                self.assertEqual(result.exit_code, 0)

                yc = YeyoConfig.from_json(Path(DEFAULT_CONFIG_PATH))

                self.assertEqual(yc, row.expected_config)
                self.assertFilesInConfigHaveVersion(yc)

                if row.expected_git_tag:
                    self.assertTagInTags(row.expected_git_tag, repo)

    def assertFilesInConfigHaveVersion(self, config):

        for f in config.files:
            with open(f) as fhandler:
                contents = fhandler.read()
                self.assertTrue(config.version_string in contents)

    def assertTagInTags(self, version_string, repo):
        tags = [t.name for t in repo.tags]
        self.assertTrue(version_string in tags)
