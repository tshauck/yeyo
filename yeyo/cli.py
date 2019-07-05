# (c) Copyright 2018 Trent Hauck
# All Rights Reserved
"""Defines the command line interface."""

import functools
import json
from pathlib import Path

import click
import py
from jinja2 import Template
from semver import parse_version_info

from yeyo import BANNER
from yeyo import __version__
from yeyo.config import DEFAULT_COMMIT_TEMPLATE
from yeyo.config import DEFAULT_CONFIG_PATH
from yeyo.config import DEFAULT_TAG_TEMPLATE
from yeyo.config import YEYO_VERSION_TEMPLATE
from yeyo.config import YeyoConfig

STARTING_VERSION = "0.0.0-dev.1"
STARTING_FILE = Path("VERSION")


def with_git(f):
    """Wrap a command to add options for creating a git tag before or after the version bump."""

    @click.option(
        "--git-tag-before/--no-git-tag-before",
        default=False,
        help="If True, tag the repo, then version bump.",
    )
    @click.option(
        "--git-tag-after/--no-git-tag-after",
        default=False,
        help="If True, bump, then commit the changed files and tag the repo.",
    )
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def with_prerel(f):
    """Wrap a command to add the prerel option, which if True means to bump with a prerelease."""

    @click.option(
        "--prerel/--no-prerel",
        default=True,
        help="If True, also make the version a prerelease version.",
    )
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def with_dryrun(f):
    """Wrap a command to add the option dryrun, which if True means not to overwrite the files."""

    @click.option(
        "--dryrun/--no-dryrun",
        default=False,
        help="If True, do not actually write files, just log the output. Defaults to False.",
    )
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


@click.group()
@click.pass_context
def main(ctx):
    """
    Hey-o for yeyo.

    yeyo is a command line interface for managing versioning in software development.

    It is a simple tool that maintains state in a json config file and has a set of commands for
    managing versions and which files are under the purview of yeyo.

    To get started run:

    \b
    $ yeyo init --help
    """
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = Path(DEFAULT_CONFIG_PATH)


@main.command()
def banner():
    """Print the banner."""
    click.echo(click.style(BANNER, blink=True, bold=True))


@main.group()
@click.pass_context
def git(ctx):
    """Entrypoint for git commands."""
    ctx.obj["yc"] = YeyoConfig.from_yaml(ctx.obj["config_path"])


@git.command()
@click.pass_context
def render_tag_string(ctx):
    """Display what the tag string would be."""
    click.echo(ctx.obj["yc"].get_templated_tag())


@git.command()
@click.pass_context
def render_commit_string(ctx):
    """Display what the commit string would be."""
    click.echo(ctx.obj["yc"].get_templated_commit())


@git.command()
@click.pass_context
@with_dryrun
def tag(ctx, **kwargs):
    """Tags the repo with the templated tag string."""
    if kwargs["dryrun"]:
        click.echo(ctx.obj["yc"].get_templated_tag())
    else:
        ctx.obj["yc"].tag_repo()


@main.command()
def version():
    """Print yeyo's version and exit."""
    click.echo(__version__)


@main.group()
def dev():
    """Entrypoint for yeyo related development commands, e.g. building its docker image."""


@dev.command()
def test():
    """Run yeyo's tests through pytest."""
    py.test.cmdline.main(["yeyo"])


@main.command()
@click.option("--starting-version", default=STARTING_VERSION, help="The version to start with.")
@click.option(
    "-t",
    "--tag-template",
    default=DEFAULT_TAG_TEMPLATE,
    help="A jinja2 templated string that will be used for git tags.",
)
@click.option(
    "-c",
    "--commit-template",
    default=DEFAULT_COMMIT_TEMPLATE,
    help="A jinja2 templated string that will be used for git commits.",
)
@click.option(
    "--default/--no-default",
    default=False,
    help="If True, add a VERSION file as a default file, default value is False.",
)
@click.pass_context
def init(ctx, starting_version, tag_template, commit_template, default):
    """
    Initialize a project with a yeyo config.

    \b
    $ yeyo init
    $ cat .yeyo.json | jq
    {
      "files": [],
      "version": "0.0.0-dev.1",
      "tag_template": "{{ yeyo_version }}",
      "commit_template": "{{ yeyo_version }}"
    }

    There are two modes of operation after this:

    \b
    * Adding or removing files, see: $ yeyo files --help
    * Version bumping, see: $ yeyo bump --help
    """
    p = YeyoConfig(
        version=parse_version_info(starting_version),
        tag_template=tag_template,
        commit_template=commit_template,
    )

    if default:
        p = p.add_file(STARTING_FILE, YEYO_VERSION_TEMPLATE)

    p.to_json(ctx.obj["config_path"])


@main.group()
@click.pass_context
def bump(ctx):
    """
    Entrypoint for version bumping.

    Running these commands will modify the files which are tracked by yeyo (see the command `yeyo
    files ls`) by updating the contents and replacing the version with the bumped version.

    Most commands support a `--dryrun` option which if invoked will not make any changes to the
    project, but will print out the expected changes.

    $ yeyo bump major --dryrun

    The "holy trinity" of major, minor, and patch commands also support a `--prerel` option which if
    invoked will bump version and add a prerelease tag.

    $ yeyo bump minor --prerel --dryrun
    """
    ctx.obj["yc"] = YeyoConfig.from_yaml(ctx.obj["config_path"])


@bump.command()
@click.pass_context
@with_prerel
@with_dryrun
@with_git
def major(ctx, **kwargs):
    """Bump the major part of the version: X.0.0."""
    yc = ctx.obj["yc"]

    new_config = yc.bump_major()
    if kwargs["prerel"]:
        new_config = new_config.bump_prerelease()

    new_config.update(
        yc,
        ctx.obj["config_path"],
        kwargs["dryrun"],
        kwargs["git_tag_before"],
        kwargs["git_tag_after"],
    )


@bump.command()
@click.pass_context
@with_prerel
@with_dryrun
@with_git
def minor(ctx, **kwargs):
    """Bump the minor part of the version: 0.X.0."""
    yc = ctx.obj["yc"]

    new_config = yc.bump_minor()
    if kwargs["prerel"]:
        new_config = new_config.bump_prerelease()

    new_config.update(
        yc,
        ctx.obj["config_path"],
        kwargs["dryrun"],
        kwargs["git_tag_before"],
        kwargs["git_tag_after"],
    )


@bump.command()
@click.pass_context
@with_prerel
@with_dryrun
@with_git
def patch(ctx, **kwargs):
    """Bump the patch part of the version: 0.0.X."""
    yc = ctx.obj["yc"]

    new_config = yc.bump_patch()
    if kwargs["prerel"]:
        new_config = new_config.bump_prerelease()

    new_config.update(
        yc,
        ctx.obj["config_path"],
        kwargs["dryrun"],
        kwargs["git_tag_before"],
        kwargs["git_tag_after"],
    )


@bump.command()
@click.option("-p", "--prerelease_token", type=click.Choice(["dev", "a", "b", "rc"]), default=None)
@click.pass_context
@with_prerel
@with_dryrun
@with_git
def prerelease(ctx, prerelease_token, **kwargs):
    """Bump the prerelease part of the version."""
    yc = ctx.obj["yc"]

    new_config = yc.bump_prerelease(prerelease_token=prerelease_token)
    new_config.update(
        yc,
        ctx.obj["config_path"],
        kwargs["dryrun"],
        kwargs["git_tag_before"],
        kwargs["git_tag_after"],
    )


@bump.command()
@click.pass_context
@with_dryrun
@with_git
def finalize(ctx, **kwargs):
    """Finalize the current version by dropping any prerelease information."""
    yc = ctx.obj["yc"]

    new_config = yc.finalize()
    new_config.update(
        yc,
        ctx.obj["config_path"],
        kwargs["dryrun"],
        kwargs["git_tag_before"],
        kwargs["git_tag_after"],
    )


@main.group()
@click.pass_context
def files(ctx):
    """Entrypoint for adding or removing files."""
    ctx.obj["yc"] = YeyoConfig.from_yaml(ctx.obj["config_path"])


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
@click.argument("path")
@click.option(
    "-t",
    "--template_string",
    default=YEYO_VERSION_TEMPLATE,
    type=str,
    help="The template string to find and replace with.",
)
def add(ctx, path, template_string):
    """Add a file path and, optionally, an associated search string.

    Imagine we were starting with the same .yeyo.json as the init example -- so we've just run
    `yeyo init`. Now we want to add a python module to yeyo's tracking, and only replace cases where
    __version__ = "0.0.1":

    $ yeyo files add __init__.py -t "__version__ = \\"yeyo_version\\""

    `yeyo_version` will be replace with the current version and updated when bumping version.

    \b
    $ cat .yeyo.json | jq
    {
      "files": [
        {
          "file_path": "__init__.py",
          "match_template": "__version__ = \\"yeyo_version\\""
        }
      ],
      "version": "0.0.0-dev.1",
      "tag_template": "{{ yeyo_version }}",
      "commit_template": "{{ yeyo_version }}"
    }

    You might run a version bump in dryrun mode now to see which files would change and how.

    \b
    $ yeyo bump minor --dryrun
    Replacing line: __version__ = "0.0.0-dev.1" with __version__ = "0.1.0" in file __init__.py.
    ...
    """
    yc = ctx.obj["yc"]

    new_config = yc.add_file(Path(path), template_string)
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
    groups = [files, bump, git]
    commands = [init, version]

    t = Template(_USAGE)

    new_ctx = click.core.Context
    click.echo(t.render(ctx=new_ctx, groups=groups, commands=commands))
