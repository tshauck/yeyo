# Changelog

## 0.3.0

### Added

- Now use yaml as the default for for the config file.

## 0.2.0

### Added

- Change config data structure to support storing a file and associated template for finding the version. This meant to help avoid version collision between two of the same versions in a file that refer to different things.

### Changed

- Rather than using `version` in the git template strings, `yeyo_version` is now used. This was done so that both the jinja template and the find and replace string both use `yeyo_version`.

## [0.0.1]

### Added

- Add general verion bump capabilities.
- Add files subcommand and its subcommands.
- Add dryrun option.
- Modularized generic input options.
- `yeyo dev test` runs the tests.
- `yeyo print-usage` that prints out the usage of yeyo in markdown format.
- `yeyo dev docker ...` for working with yeyo's docker images.

[0.0.1]: https://github.com/tshauck/yeyo/compare/v0.0.0...0.0.1
