# (c) Copyright 2019 Trent Hauck
# All Rights Reserved

import unittest
from pathlib import Path
from typing import List
from typing import NamedTuple
from typing import Optional

import pytest
import git
from click.testing import CliRunner
from semver import VersionInfo

from yeyo import cli
from yeyo.cli import STARTING_VERSION
from yeyo.config import DEFAULT_COMMIT_TEMPLATE
from yeyo.config import DEFAULT_CONFIG_PATH
from yeyo.config import DEFAULT_TAG_TEMPLATE
from yeyo.config import YeyoConfig
from yeyo.config import FileVersion
from yeyo.config import YEYO_VERSION_TEMPLATE

TEST_FILE = Path("VERSION")
TEST_FILE_VERSION = FileVersion(TEST_FILE, YEYO_VERSION_TEMPLATE)

test_rows = [
    (
        YeyoConfig.from_version_string(
            STARTING_VERSION, DEFAULT_TAG_TEMPLATE, DEFAULT_COMMIT_TEMPLATE, {TEST_FILE_VERSION}
        ),
        ["init", "--default"],
        None,
    ),
    (
        YeyoConfig.from_version_string(
            "0.0.0-dev.2", DEFAULT_TAG_TEMPLATE, DEFAULT_COMMIT_TEMPLATE, {TEST_FILE_VERSION}
        ),
        ["bump", "prerelease", "--git-tag-after"],
        "0.0.0-dev.2",
    ),
    (
        YeyoConfig.from_version_string(
            "0.0.0-a.1", DEFAULT_TAG_TEMPLATE, DEFAULT_COMMIT_TEMPLATE, {TEST_FILE_VERSION}
        ),
        ["bump", "prerelease", "-p", "a", "--git-tag-after"],
        "0.0.0-a.1",
    ),
    (
        YeyoConfig.from_version_string(
            "0.0.0", DEFAULT_TAG_TEMPLATE, DEFAULT_COMMIT_TEMPLATE, {TEST_FILE_VERSION}
        ),
        ["bump", "finalize", "--git-tag-after"],
        "0.0.0",
    ),
    (
        YeyoConfig.from_version_string(
            "0.0.1-dev.1", DEFAULT_TAG_TEMPLATE, DEFAULT_COMMIT_TEMPLATE, {TEST_FILE_VERSION}
        ),
        ["bump", "patch", "--prerel", "--git-tag-before"],
        "0.0.0",
    ),
][:2]


def test_version_bumps():

    runner = CliRunner()
    with runner.isolated_filesystem():
        repo = git.Repo.init(".", "bare-repo")

        with open(TEST_FILE, "w") as f:
            f.write(STARTING_VERSION)

        repo.index.add([str(TEST_FILE)])
        repo.index.commit("COMMIT")

        for config, command, expected_git_tag in test_rows:

            result = runner.invoke(cli.main, command)
            assert result.exit_code == 0

            yc = YeyoConfig.from_json(Path(DEFAULT_CONFIG_PATH))
            assert yc == config

            assert_files_in_config_have_version(yc)

            if expected_git_tag is not None:
                assert_tag_in_tags(expected_git_tag, repo)


def assert_files_in_config_have_version(config):
    for f in config.files:
        with open(f.file_path) as fhandler:
            contents = fhandler.read()
            assert config.version_string in contents


def assert_tag_in_tags(version_string, repo):
    tags = [t.name for t in repo.tags]
    assert version_string in tags
