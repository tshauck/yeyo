# (c) Copyright 2018 Trent Hauck
# All Rights Reserved

import functools
from pathlib import Path

import py
import click
from semver import parse_version_info
from jinja2 import Template

from yeyo import __version__
from yeyo.config import YeyoConfig


STARTING_VERSION = "0.0.0-dev.1"
STARTING_FILE = Path("VERSION")
DEFAULT_CONFIG_PATH = ".yeyo.json"


def with_prerel(f):
    """A decorator to add the prerel option, which if True means to bump with a prerelease."""

    @click.option("--prerel/--no-prerel", default=True)
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def with_dryrun(f):
    """A decorator to add the option dryrun, which if True means not to overwrite the files."""

    @click.option("--dryrun/--no-dryrun", default=False)
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


@click.group()
@click.option(
    "-c",
    "--config-path",
    default=DEFAULT_CONFIG_PATH,
    help=f"Where the yeyo config is located, the default is {DEFAULT_CONFIG_PATH}.",
)
@click.pass_context
def main(ctx, config_path):
    """Hey-o for yeyo.

    yeyo is a command line interface for managing versioning in software development.

    It is a simple tool that maintains state in a json config file and has a set of commands for
    managing versions and which files are under the purview of yeyo.

    To get started run:

    \b
    $ yeyo init --help
    """
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = Path(config_path)


@main.command()
def version():
    """Print the version and exit."""
    click.echo(__version__)


@main.command()
def test():
    """Run the tests."""
    py.test.cmdline.main(["yeyo"])


@main.command()
@click.option("--starting-version", default=STARTING_VERSION, help="The version to start with.")
@click.option(
    "-f", "--files", multiple=True, help="The list of files to add to the config at the outset."
)
@click.pass_context
def init(ctx, starting_version, files):
    """Initialize a project with a yeyo config.

    For example, to initialize a repo that has a setup.py file and a mod/__init__.py to track, and
    we'd like the version to start at 0.1.0:

    \b
    $ yeyo init -f setup.py -f mod/__init__.py --starting-version 0.1.0
    $ cat .yeyo.json
    {"files": ["mod/__init__.py", "setup.py"], "version": "0.1.0"}

    There are two modes of operation after this:

    \b
    * Adding or removing files, see: $ yeyo files --help
    * Version bumping, see: $ yeyo bump --help
    """

    p = YeyoConfig(version=parse_version_info(starting_version), files=set(files))
    p.to_json(ctx.obj["config_path"])


@main.group()
@click.pass_context
def bump(ctx):
    """Entrypoint for version bumping.

    Running these commands will modify the files which are tracked by yeyo (see the command `yeyo
    files ls`) by updating the contents and replacing the version with the bumped version.

    Most commands support a `--dryrun` option which if invoked will not make any changes to the
    project, but will print out the expected changes.

    $ yeyo bump major --dryrun

    The "holy trinity" of major, minor, and patch commands also support a `--prerel` option which if
    invoked will bump version and add a prerelease tag.

    $ yeyo bump minor --prerel --dryrun
    """
    ctx.obj["yc"] = YeyoConfig.from_json(ctx.obj["config_path"])


@bump.command()
@with_prerel
@with_dryrun
@click.pass_context
def major(ctx, **kwargs):
    """Bump the major part of the version: X.0.0"""
    yc = ctx.obj["yc"]

    new_config = yc.bump_major()
    if kwargs["prerel"]:
        new_config = new_config.bump_prerelease()

    new_config.update(yc, ctx.obj["config_path"], kwargs["dryrun"])


@bump.command()
@with_prerel
@with_dryrun
@click.pass_context
def minor(ctx, **kwargs):
    """Bump the minor part of the version: 0.X.0"""
    yc = ctx.obj["yc"]

    new_config = yc.bump_minor()
    if kwargs["prerel"]:
        new_config = new_config.bump_prerelease()

    new_config.update(yc, ctx.obj["config_path"], kwargs["dryrun"])


@bump.command()
@with_prerel
@with_dryrun
@click.pass_context
def patch(ctx, **kwargs):
    """Bump the patch part of the version: 0.0.X"""
    yc = ctx.obj["yc"]

    new_config = yc.bump_patch()
    if kwargs["prerel"]:
        new_config = new_config.bump_prerelease()

    new_config.update(yc, ctx.obj["config_path"], kwargs["dryrun"])


@bump.command()
@with_prerel
@with_dryrun
@click.option("-p", "--prerelease_token", type=click.Choice(["dev", "a", "b", "rc"]), default=None)
@click.pass_context
def prerelease(ctx, prerelease_token, **kwargs):
    """Bump the prerelease part of the version."""
    yc = ctx.obj["yc"]

    new_config = yc.bump_prerelease(prerelease_token=prerelease_token)
    new_config.update(yc, ctx.obj["config_path"], kwargs["dryrun"])


@bump.command()
@with_dryrun
@click.pass_context
def finalize(ctx, **kwargs):
    """Finalize the current version by dropping any prerelease information."""
    yc = ctx.obj["yc"]

    new_config = yc.finalize()
    new_config.update(yc, ctx.obj["config_path"], kwargs["dryrun"])


@main.group()
@click.pass_context
def files(ctx):
    """Entrypoint for adding or removing files."""
    ctx.obj["yc"] = YeyoConfig.from_json(ctx.obj["config_path"])


@files.command()
@with_dryrun
@click.pass_context
def ls(ctx, **kwargs):
    """List of the files present in yeyo's config."""
    yc = ctx.obj["yc"]
    for f in yc.files:
        click.echo(str(f))


@files.command()
@click.pass_context
@click.argument("path")
def rm(ctx, path, **kwargs):
    """Remove a file from yeyo's config."""
    yc = ctx.obj["yc"]

    new_config = yc.remove_file(Path(path))
    new_config.to_json(ctx.obj["config_path"])


@files.command()
@click.pass_context
@click.argument("path", nargs=-1)
def add(ctx, path, **kwargs):
    """Add one or more files to the yeyo config."""
    yc = ctx.obj["yc"]

    new_config = yc.add_files({Path(p) for p in path})
    new_config.to_json(ctx.obj["config_path"])


_USAGE = """## Usage

How to (mis)use yeyo.

{% for cmd in commands %}
### Command: {{ cmd.name }}
```console
{{ ctx(cmd, info_name=cmd.name).get_help() }}
```
{% endfor %}

{% for group in groups -%}
### Group: {{group.name}}

```console
{{ ctx(group, info_name=group.name).get_help() }}
```

{% for k, v in group.commands.items() %}
#### Command: {{ k }}

```console
{{ ctx(v, info_name=v.name).get_help() }}
```
{% endfor -%}

{% endfor -%}
"""


@main.command()
@click.pass_context
def print_usage(ctx):
    """Echo the usage combined into a markdown format."""
    groups = [files, bump]
    commands = [init, version]

    t = Template(_USAGE)

    new_ctx = click.core.Context
    click.echo(t.render(ctx=new_ctx, groups=groups, commands=commands))
