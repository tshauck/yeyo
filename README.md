# yeyo

> yeyo is a package for automatically managing versions in software repos.

[![](https://img.shields.io/pypi/v/yeyo.svg)](https://pypi.python.org/pypi/yeyo)
[![](https://img.shields.io/travis/tshauck/yeyo.svg)](https://travis-ci.org/tshauck/yeyo)

## Installation

```console
$ pip install yeyo
```

## Usage

How to (mis)use yeyo.

### Command: init

```console
Usage: init [OPTIONS]

  Initialize a project with a yeyo config.

  For example, to initialize a repo that has a setup.py file and a
  mod/__init__.py to track, and we'd like the version to start at 0.1.0:

  $ yeyo init -f setup.py -f mod/__init__.py --starting-version 0.1.0
  $ cat .yeyo.json
  {"files": ["mod/__init__.py", "setup.py"], "version": "0.1.0"}

  There are two modes of operation after this:

  * Adding or removing files, see: $ yeyo files --help
  * Version bumping, see: $ yeyo bump --help

Options:
  --starting-version TEXT  The version to start with.
  -f, --files TEXT         The list of files to add to the config at the
                           outset.
  --help                   Show this message and exit.
```

### Command: version

```console
Usage: version [OPTIONS]

  Print the version and exit.

Options:
  --help  Show this message and exit.
```

### Group: files

```console
Usage: files [OPTIONS] COMMAND [ARGS]...

  Entrypoint for adding or removing files.

Options:
  --help  Show this message and exit.

Commands:
  add  Add one or more files to the yeyo config.
  ls   List of the files present in yeyo's config.
  rm   Remove a file from yeyo's config.
```

#### Command: ls

```console
Usage: ls [OPTIONS]

  List of the files present in yeyo's config.

Options:
  --dryrun / --no-dryrun
  --help                  Show this message and exit.
```

#### Command: rm

```console
Usage: rm [OPTIONS] PATH

  Remove a file from yeyo's config.

Options:
  --help  Show this message and exit.
```

#### Command: add

```console
Usage: add [OPTIONS] [PATH]...

  Add one or more files to the yeyo config.

Options:
  --help  Show this message and exit.
```

### Group: bump

```console
Usage: bump [OPTIONS] COMMAND [ARGS]...

  Entrypoint for version bumping.

  Running these commands will modify the files which are tracked by yeyo
  (see the command `yeyo files ls`) by updating the contents and replacing
  the version with the bumped version.

  Most commands support a `--dryrun` option which if invoked will not make
  any changes to the project, but will print out the expected changes.

  $ yeyo bump major --dryrun

  The "holy trinity" of major, minor, and patch commands also support a
  `--prerel` option which if invoked will bump version and add a prerelease
  tag.

  $ yeyo bump minor --prerel --dryrun

Options:
  --help  Show this message and exit.

Commands:
  finalize    Finalize the current version by dropping any prerelease...
  major       Bump the major part of the version: X.0.0
  minor       Bump the minor part of the version: 0.X.0
  patch       Bump the patch part of the version: 0.0.X
  prerelease  Bump the prerelease part of the version.
```

#### Command: major

```console
Usage: major [OPTIONS]

  Bump the major part of the version: X.0.0

Options:
  --prerel / --no-prerel
  --dryrun / --no-dryrun
  --help                  Show this message and exit.
```

#### Command: minor

```console
Usage: minor [OPTIONS]

  Bump the minor part of the version: 0.X.0

Options:
  --prerel / --no-prerel
  --dryrun / --no-dryrun
  --help                  Show this message and exit.
```

#### Command: patch

```console
Usage: patch [OPTIONS]

  Bump the patch part of the version: 0.0.X

Options:
  --prerel / --no-prerel
  --dryrun / --no-dryrun
  --help                  Show this message and exit.
```

#### Command: prerelease

```console
Usage: prerelease [OPTIONS]

  Bump the prerelease part of the version.

Options:
  --prerel / --no-prerel
  --dryrun / --no-dryrun
  -p, --prerelease_token [dev|a|b|rc]
  --help                          Show this message and exit.
```

#### Command: finalize

```console
Usage: finalize [OPTIONS]

  Finalize the current version by dropping any prerelease information.

Options:
  --dryrun / --no-dryrun
  --help                  Show this message and exit.
```
