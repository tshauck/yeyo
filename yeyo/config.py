# (c) Copyright 2018 Trent Hauck
# All Rights Reserved
"""Contains the YeyoConfig object."""

import copy
import fileinput
import json
from pathlib import Path
from typing import NamedTuple
from typing import Optional
from typing import Set

import git
import semver
from jinja2 import Template

YEYO_VERSION_TEMPLATE = "yeyo_version"
DEFAULT_TAG_TEMPLATE = f"{{{{ {YEYO_VERSION_TEMPLATE} }}}}"
DEFAULT_COMMIT_TEMPLATE = f"{{{{ {YEYO_VERSION_TEMPLATE} }}}}"
DEFAULT_CONFIG_PATH = ".yeyo.json"


class YeyoDirtyRepoException(Exception):
    """Raised when more files than just the tracked changes are raised."""


class FileVersion(NamedTuple):
    """Contains a file_path and a template to use for search and replace."""

    file_path: Path
    match_template: str

    def replace(self, s: str, v1: semver.VersionInfo, v2: semver.VersionInfo) -> str:
        """Given the input string, s, use the template to find v1 and replace it with v2."""

        search_string = self.match_template.replace(YEYO_VERSION_TEMPLATE, str(v1))
        replace_string = self.match_template.replace(YEYO_VERSION_TEMPLATE, str(v2))
        return s.replace(search_string, replace_string)


class YeyoConfig(object):
    """The base Yeyo config object."""

    def __init__(
        self,
        version: semver.VersionInfo,
        tag_template: str = DEFAULT_TAG_TEMPLATE,
        commit_template: str = DEFAULT_COMMIT_TEMPLATE,
        files: Optional[Set[FileVersion]] = None,
    ):
        """Initialize a YeyoConfig with a version and a set of files."""
        self.version = version
        self.tag_template = tag_template
        self.commit_template = commit_template
        self.files = files or set()

    def __repr__(self):
        """Return the string representation."""
        return json.dumps(self, cls=YeyoConfigEncoder, indent=4)

    def __eq__(self, other):
        """Check the equality against another YeyoConfig object."""
        ok_version = self.version == other.version
        ok_files = self.files == other.files
        return ok_files and ok_version

    def remove_file(self, file_path: Path) -> "YeyoConfig":
        """Create a new config object with file_path removed from the files."""
        file_versions = {fv for fv in self.files if fv.file_path != file_path}
        return YeyoConfig(self.version, self.tag_template, self.commit_template, file_versions)

    def add_file(self, file_path: Path, match_template: str) -> "YeyoConfig":
        """Create a new config object with file_path added to the files."""
        file_copy = copy.copy(self.files)
        file_copy.add(FileVersion(file_path, match_template))

        return YeyoConfig(self.version, self.tag_template, self.commit_template, file_copy)

    def get_templated_tag(self, **kwargs):
        """Render the tag template, kwargs are passed to the jinja template."""
        t = Template(self.tag_template)
        return t.render(yeyo_version=self.version_string, files=self.files, **kwargs)

    def get_templated_commit(self, **kwargs):
        """Render the commit template, kwargs are passed to the jinja template."""
        t = Template(self.commit_template)
        return t.render(yeyo_version=self.version_string, files=self.files, **kwargs)

    @classmethod
    def from_version_string(
        cls,
        version_string: str,
        tag_template: str,
        commit_template: str,
        file_versions: Optional[Set[FileVersion]] = None,
    ):
        """Create a YeyoConfig from a version string."""

        if file_versions is None:
            file_versions = set()

        config = cls(semver.parse_version_info(version_string), tag_template, commit_template)
        for f in file_versions:
            config = config.add_file(f.file_path, f.match_template)
        return config

    @classmethod
    def from_json(cls, p: Path):
        """Create a YeyoConfig from a json file."""
        with open(p) as out_handler:
            return json.load(out_handler, cls=YeyoConfigDecoder)

    def to_json(self, p: Path):
        """Write the YeyoConfig to a json file."""
        with open(p, "w") as out_handler:
            json.dump(self, out_handler, cls=YeyoConfigEncoder)
            out_handler.write("\n")

    def _update_files(self, old_yeyo_config: "YeyoConfig", dryrun: bool):
        inplace = not dryrun

        for fv in self.files:
            with fileinput.input(files=[str(fv.file_path)], inplace=inplace) as f:
                for line in f:

                    filename = fileinput.filename()
                    new_line = fv.replace(line, old_yeyo_config.version, self.version)

                    if dryrun and old_yeyo_config.version_string in line:
                        print(
                            f"Replacing line: {line} with {new_line} in file {filename}.".replace(
                                "\n", ""
                            )
                        )
                    elif not dryrun:
                        print(new_line, end="")

    def update(
        self,
        old_yeyo_config: "YeyoConfig",
        config_path: Path,
        dryrun: bool = False,
        git_tag_before: bool = False,
        git_tag_after: bool = False,
    ):
        """Find the version from the prior config and replace them."""
        if git_tag_before and not dryrun:
            self._tag_repo()

        if self.files:
            self._update_files(old_yeyo_config, dryrun)

        if dryrun:
            print(f"\nNew Config:\n{self}")
            print(f"Tag Template: {self.get_templated_tag()}.")
            print(f"Commit Template: {self.get_templated_commit()}.")
        else:
            self.to_json(config_path)

            if git_tag_after:
                self._tag_after()

    @property
    def string_files(self):
        """Convert the set of Paths at self.files to a set of strings."""
        return {str(p.file_path) for p in self.files}

    def _tag_after(self: "YeyoConfig"):
        repo = git.Repo(".")

        file_paths = {p.file_path for p in self.files}.union({Path(DEFAULT_CONFIG_PATH)})
        extra_files = {Path(p) for p in repo.untracked_files} - file_paths
        if extra_files:
            raise YeyoDirtyRepoException(
                f"Repo is dirty, these extra files have changes: {extra_files}."
            )

        if self.files:
            repo.index.add(self.string_files)

        repo.index.add([str(DEFAULT_CONFIG_PATH)])

        commit_string = self.get_templated_commit()
        repo.index.commit(commit_string)

        self._tag_repo()

    def _tag_repo(self: "YeyoConfig"):
        tag_string = self.get_templated_tag()

        repo = git.Repo(".")
        repo.create_tag(tag_string)

    def tag_repo(self: "YeyoConfig"):
        """Tag the current repo with the templated string."""
        self._tag_repo()

    def _new_version(self, func, *args, **kwargs):
        return func(self.version_string, *args, **kwargs)

    def bump_major(self):
        """Bump the config to the next major version."""
        return YeyoConfig.from_version_string(
            self._new_version(semver.bump_major),
            self.tag_template,
            self.commit_template,
            self.files,
        )

    def bump_minor(self):
        """Bump the config to the next minor version."""
        return YeyoConfig.from_version_string(
            self._new_version(semver.bump_minor),
            self.tag_template,
            self.commit_template,
            self.files,
        )

    def bump_patch(self):
        """Bump the config to the next patch version."""
        return YeyoConfig.from_version_string(
            self._new_version(semver.bump_patch),
            self.tag_template,
            self.commit_template,
            self.files,
        )

    def bump_build(self):
        """Bump the config to the next build version."""
        return YeyoConfig.from_version_string(
            self._new_version(semver.bump_build),
            self.tag_template,
            self.commit_template,
            self.files,
        )

    def bump_prerelease(self, prerelease_token: Optional[str] = None):
        """Bump the config to the next prerelease version."""
        if self.version.prerelease is None:
            return YeyoConfig.from_version_string(
                self._new_version(semver.bump_prerelease, token="dev"),
                self.tag_template,
                self.commit_template,
                self.files,
            )

        if prerelease_token is None and self.version.prerelease:
            return YeyoConfig.from_version_string(
                self._new_version(semver.bump_prerelease, token=self.version.prerelease),
                self.tag_template,
                self.commit_template,
                self.files,
            )

        finalized = self.finalize()
        return YeyoConfig.from_version_string(
            finalized._new_version(semver.bump_prerelease, token=prerelease_token),
            self.tag_template,
            self.commit_template,
            self.files,
        )

    def finalize(self):
        """Finalize the current version and return the config."""
        return YeyoConfig.from_version_string(
            self._new_version(semver.finalize_version),
            self.tag_template,
            self.commit_template,
            self.files,
        )

    @property
    def version_string(self):
        """Pretty format the underlying version."""
        return semver.format_version(
            self.version.major,
            self.version.minor,
            self.version.patch,
            self.version.prerelease,
            self.version.build,
        )


class YeyoConfigEncoder(json.JSONEncoder):
    """Encode a YeyoConfig object."""

    def default(self, o):
        """Handle the deserialization of the object."""
        if isinstance(o, YeyoConfig):
            d = {}
            d["files"] = [
                {"file_path": str(p.file_path), "match_template": p.match_template} for p in o.files
            ]
            d["version"] = o.version_string
            d["tag_template"] = o.tag_template
            d["commit_template"] = o.commit_template

            return d
        elif isinstance(o, set):
            return list(o)
        else:
            return super().default(o)


class YeyoConfigDecoder(json.JSONDecoder):
    """Decode a YeyoConfig object."""

    def __init__(self, *args, **kwargs):
        """Init the JSONDecoder object."""
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        """Given the object passed, return a YeyoConfig object."""

        if set(obj.keys()) == {"file_path", "match_template"}:
            return FileVersion(Path(obj["file_path"]), obj["match_template"])

        version = semver.parse_version_info(obj["version"])

        files = []
        for fv in obj["files"]:
            files.append(fv)
        files = set(files)

        tag_template = obj.get("tag_template", DEFAULT_TAG_TEMPLATE)
        commit_template = obj.get("commit_template", DEFAULT_COMMIT_TEMPLATE)

        return YeyoConfig(version, tag_template, commit_template, files)
