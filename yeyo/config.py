# (c) Copyright 2018 Trent Hauck
# All Rights Reserved
"""Contains the YeyoConfig object."""

import copy
import fileinput
import json
from pathlib import Path
from typing import Optional, Set

import semver


class YeyoConfig(object):
    """The base Yeyo config object."""

    def __init__(self, version: semver.VersionInfo, files: Optional[Set[Path]] = None):
        """Initialize a YeyoConfig with a version and a set of files."""
        self.version = version
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

        file_copy = copy.copy(self.files)
        file_copy.remove(file_path)
        return YeyoConfig(self.version, file_copy)

    def add_file(self, file_path: Path) -> "YeyoConfig":
        """Create a new config object with file_path added to the files."""

        file_copy = copy.copy(self.files)
        file_copy.add(file_path)
        return YeyoConfig(self.version, file_copy)

    def add_files(self, file_paths: Set[Path]) -> "YeyoConfig":
        """Add a set of paths to the config."""

        return YeyoConfig(self.version, self.files.union(file_paths))

    @classmethod
    def from_version_string(cls, version_string: str, f: Optional[Set[Path]] = None):
        """Create a YeyoConfig from a version string."""
        return cls(semver.parse_version_info(version_string), f)

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

    def update(self, old_yeyo_config: "YeyoConfig", config_path: Path, dryrun: bool = False):
        """Find the version from the prior config and replace them."""
        str_files = [str(s) for s in self.files]

        inplace = not dryrun

        with fileinput.input(files=str_files, inplace=inplace) as f:
            for line in f:

                filename = fileinput.filename()
                new_line = line.replace(old_yeyo_config.version_string, self.version_string)

                if dryrun and old_yeyo_config.version_string in line:
                    print(
                        f"Replacing line: {line} with {new_line} in file {filename}.".replace(
                            "\n", ""
                        )
                    )
                elif not dryrun:
                    print(line.replace(old_yeyo_config.version_string, self.version_string), end="")

        if dryrun:
            print(f"\nNew Config:\n{self}")
        else:
            self.to_json(config_path)

    def _new_version(self, func, *args, **kwargs):
        return func(self.version_string, *args, **kwargs)

    def bump_major(self):
        """Bump the config to the next major version."""
        return YeyoConfig.from_version_string(self._new_version(semver.bump_major), self.files)

    def bump_minor(self):
        """Bump the config to the next minor version."""
        return YeyoConfig.from_version_string(self._new_version(semver.bump_minor), self.files)

    def bump_patch(self):
        """Bump the config to the next patch version."""
        return YeyoConfig.from_version_string(self._new_version(semver.bump_patch), self.files)

    def bump_build(self):
        """Bump the config to the next build version."""
        return YeyoConfig.from_version_string(self._new_version(semver.bump_build), self.files)

    def bump_prerelease(self, prerelease_token: Optional[str] = None):
        """Bump the config to the next prerelease version."""

        if self.version.prerelease is None:
            return YeyoConfig.from_version_string(
                self._new_version(semver.bump_prerelease, token="dev"), self.files
            )

        if prerelease_token is None and self.version.prerelease:
            return YeyoConfig.from_version_string(
                self._new_version(semver.bump_prerelease, token=self.version.prerelease), self.files
            )

        finalized = self.finalize()
        return YeyoConfig.from_version_string(
            finalized._new_version(semver.bump_prerelease, token=prerelease_token), self.files
        )

    def finalize(self):
        """Finalize the current version and return the config."""
        return YeyoConfig.from_version_string(
            self._new_version(semver.finalize_version), self.files
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
            d["files"] = [str(p) for p in o.files]
            d["version"] = o.version_string

            return d
        else:
            return super().default(o)


class YeyoConfigDecoder(json.JSONDecoder):
    """Decode a YeyoConfig object."""

    def __init__(self, *args, **kwargs):
        """Init the JSONDecoder object."""
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        """Given the object passed, return a YeyoConfig object."""
        version = semver.parse_version_info(obj["version"])
        files = set([Path(p) for p in obj["files"]])

        return YeyoConfig(version, files)
