# yeyo

> yeyo is a command line tool for managing versions across file types within a repo.

[![](https://img.shields.io/pypi/v/yeyo.svg)](https://pypi.python.org/pypi/yeyo)
[![](https://img.shields.io/travis/tshauck/yeyo.svg)](https://travis-ci.org/tshauck/yeyo)
[![](https://img.shields.io/docker/pulls/thauck/yeyo.svg)](https://hub.docker.com/r/thauck/yeyo)

<!-- vim-markdown-toc GFM -->

* [Installation](#installation)
  * [Python Package](#python-package)
  * [Use with Docker](#use-with-docker)
* [Usage](#usage)
  * [Command: init](#command-init)
  * [Command: version](#command-version)
  * [Group: files](#group-files)
    * [Command: ls](#command-ls)
    * [Command: rm](#command-rm)
    * [Command: add](#command-add)
  * [Group: bump](#group-bump)
    * [Command: major](#command-major)
    * [Command: minor](#command-minor)
    * [Command: patch](#command-patch)
    * [Command: prerelease](#command-prerelease)
    * [Command: finalize](#command-finalize)
  * [Group: git](#group-git)
    * [Command: render-tag-string](#command-render-tag-string)
    * [Command: render-commit-string](#command-render-commit-string)
    * [Command: tag](#command-tag)

<!-- vim-markdown-toc -->

## Installation

### Python Package

```console
$ pip install yeyo
```

### Use with Docker

If you'd like to use yeyo through docker, you can do so by first pulling the image:

```console
# In practice, you should pin to a particular version.
$ docker pull thauck/yeyo:latest
```

Then, run a container and mount the project directory to `/project`. For example,

```console
$ docker run -it -v $(pwd):/project thauck/yeyo:latest init
```

will initialize the host directory from the docker container.

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
  --starting-version TEXT     The version to start with.
  -f, --files TEXT            The list of files to add to the config at the
                              outset.
  -t, --tag-template TEXT     A jinja2 templated string that will be used for
                              git tags.
  -c, --commit-template TEXT  A jinja2 templated string that will be used for
                              git commits.
  --help                      Show this message and exit.
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
  --dryrun / --no-dryrun  If True, do not actually write files, just log the
                          output. Defaults to False.
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
  major       Bump the major part of the version: X.0.0.
  minor       Bump the minor part of the version: 0.X.0.
  patch       Bump the patch part of the version: 0.0.X.
  prerelease  Bump the prerelease part of the version.
```

#### Command: major

```console
Usage: major [OPTIONS]

  Bump the major part of the version: X.0.0.

Options:
  --prerel / --no-prerel          If True, also make the version a prerelease
                                  version.
  --dryrun / --no-dryrun          If True, do not actually write files, just
                                  log the output. Defaults to False.
  --git-tag-before / --no-git-tag-before
                                  If True, tag the repo, then version bump.
  --git-tag-after / --no-git-tag-after
                                  If True, bump, then commit the changed files
                                  and tag the repo.
  --help                          Show this message and exit.
```

#### Command: minor

```console
Usage: minor [OPTIONS]

  Bump the minor part of the version: 0.X.0.

Options:
  --prerel / --no-prerel          If True, also make the version a prerelease
                                  version.
  --dryrun / --no-dryrun          If True, do not actually write files, just
                                  log the output. Defaults to False.
  --git-tag-before / --no-git-tag-before
                                  If True, tag the repo, then version bump.
  --git-tag-after / --no-git-tag-after
                                  If True, bump, then commit the changed files
                                  and tag the repo.
  --help                          Show this message and exit.
```

#### Command: patch

```console
Usage: patch [OPTIONS]

  Bump the patch part of the version: 0.0.X.

Options:
  --prerel / --no-prerel          If True, also make the version a prerelease
                                  version.
  --dryrun / --no-dryrun          If True, do not actually write files, just
                                  log the output. Defaults to False.
  --git-tag-before / --no-git-tag-before
                                  If True, tag the repo, then version bump.
  --git-tag-after / --no-git-tag-after
                                  If True, bump, then commit the changed files
                                  and tag the repo.
  --help                          Show this message and exit.
```

#### Command: prerelease

```console
Usage: prerelease [OPTIONS]

  Bump the prerelease part of the version.

Options:
  -p, --prerelease_token [dev|a|b|rc]
  --prerel / --no-prerel          If True, also make the version a prerelease
                                  version.
  --dryrun / --no-dryrun          If True, do not actually write files, just
                                  log the output. Defaults to False.
  --git-tag-before / --no-git-tag-before
                                  If True, tag the repo, then version bump.
  --git-tag-after / --no-git-tag-after
                                  If True, bump, then commit the changed files
                                  and tag the repo.
  --help                          Show this message and exit.
```

#### Command: finalize

```console
Usage: finalize [OPTIONS]

  Finalize the current version by dropping any prerelease information.

Options:
  --dryrun / --no-dryrun          If True, do not actually write files, just
                                  log the output. Defaults to False.
  --git-tag-before / --no-git-tag-before
                                  If True, tag the repo, then version bump.
  --git-tag-after / --no-git-tag-after
                                  If True, bump, then commit the changed files
                                  and tag the repo.
  --help                          Show this message and exit.
```

### Group: git

```console
Usage: git [OPTIONS] COMMAND [ARGS]...

  Entrypoint for git commands.

Options:
  --help  Show this message and exit.

Commands:
  render-commit-string  Display what the commit string would be.
  render-tag-string     Display what the tag string would be.
  tag                   Tags the repo with the templated tag string.
```

#### Command: render-tag-string

```console
Usage: render-tag-string [OPTIONS]

  Display what the tag string would be.

Options:
  --help  Show this message and exit.
```

#### Command: render-commit-string

```console
Usage: render-commit-string [OPTIONS]

  Display what the commit string would be.

Options:
  --help  Show this message and exit.
```

#### Command: tag

```console
Usage: tag [OPTIONS]

  Tags the repo with the templated tag string.

Options:
  --dryrun / --no-dryrun  If True, do not actually write files, just log the
                          output. Defaults to False.
  --help                  Show this message and exit.
```
