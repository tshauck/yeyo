# (c) Copyright 2018 Trent Hauck
# All Rights Reserved

import functools
from pathlib import Path

import click
from semver import parse_version_info

from yeyo import __version__
from yeyo.config import YeyoConfig


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
@click.option("-c", "--config-path", default=".yeyo.json")
@click.pass_context
def main(ctx, config_path):
    """The base of the yeyo command."""
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = Path(config_path)


@main.command()
def version():
    """Print the version and exit."""
    click.echo(__version__)


@main.command()
@click.pass_context
def init(ctx):
    """Init a project with a yeyo config."""
    version_file = Path("VERSION")
    p = YeyoConfig(version=parse_version_info("0.0.0-dev.1"), files={version_file})

    with open(version_file, "w") as version_file_handler:
        version_file_handler.write(f"{p.version_string}\n")

    p.to_json(ctx.obj["config_path"])


@main.group()
@click.pass_context
def bump(ctx):
    """Entrypoint for version bumping."""
    ctx.obj["yc"] = YeyoConfig.from_json(ctx.obj["config_path"])


@bump.command()
@with_prerel
@with_dryrun
@click.pass_context
def major(ctx, **kwargs):
    """Bump the major part of the version."""
    yc = ctx.obj["yc"]

    new_config = yc.bump_major()
    if kwargs["prerel"]:
        new_config = yc.bump_prerelease()

    new_config.update(yc, ctx.obj["config_path"], kwargs["dryrun"])


@bump.command()
@with_prerel
@with_dryrun
@click.pass_context
def minor(ctx, **kwargs):
    """Bump the major part of the version."""
    yc = ctx.obj["yc"]

    new_config = yc.bump_minor()
    if kwargs["prerel"]:
        new_config = yc.bump_prerelease()

    new_config.update(yc, ctx.obj["config_path"], kwargs["dryrun"])


@bump.command()
@with_prerel
@with_dryrun
@click.pass_context
def patch(ctx, **kwargs):
    """Bump the major part of the version."""
    yc = ctx.obj["yc"]

    new_config = yc.bump_patch()
    if kwargs["prerel"]:
        new_config = yc.bump_prerelease()

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
    """Finalize the cuurent version."""
    yc = ctx.obj["yc"]

    new_config = yc.finalize()
    new_config.update(yc, ctx.obj["config_path"], kwargs["dryrun"])


@main.group()
@click.pass_context
def files(ctx):
    """Entrypoint for version bumping."""
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
    """List of the files present in yeyo's config."""
    yc = ctx.obj["yc"]

    new_config = yc.remove_file(Path(path))
    new_config.to_json(ctx.obj["config_path"])


@files.command()
@click.pass_context
@click.argument("path")
def add(ctx, path, **kwargs):
    """List of the files present in yeyo's config."""
    yc = ctx.obj["yc"]

    new_config = yc.add_file(Path(path))
    new_config.to_json(ctx.obj["config_path"])
