"""CLI entrypoint for imvar.

We use Click to build a single CLI tool with subcommands instead of standalone
scripts, so all build tooling for the development container images lives
under one root command.
"""

import logging
from pathlib import Path

import click

from imvar.build import VariantBuildClient

logger = logging.getLogger(__name__)

_VERBOSITY_LEVELS = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG,
}


@click.group()
@click.option(
    "--verbose",
    "-v",
    count=True,
    help="Increase logging verbosity. Use -v for INFO, -vv for DEBUG.",
)
def cli(verbose: int) -> None:
    """Command-line tooling for generating base images for development containers.

    We use Python tooling instead of Compose to make a one-stop shop for generating
    the images, instead of relying on separate multiple entries in a compose file.
    Since the pattern is pretty consistent, using a Python script allows us to centralize
    and automate the generation process efficiently.
    """
    level = _VERBOSITY_LEVELS.get(min(verbose, 2), logging.INFO)
    logging.basicConfig(
        format="[%(asctime)s][%(levelname)8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=level,
    )


@cli.command()
@click.option(
    "--context",
    "-c",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path.cwd(),
    help="The context directory for the Docker build.",
)
@click.option(
    "--file",
    "-f",
    "config_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="The directory containing the Dockerfile and variant definition file.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path, dir_okay=False),
    default=None,
    help="The output file for the build summary",
)
def build(context: Path, config_file: Path, output: Path | None) -> None:
    """Build base images for development containers."""
    build_client = VariantBuildClient(context=context, configuration_file=config_file)
    results = build_client.build_all()
    click.secho(f"Built {len(results.images)} images!", fg="green")
    for result in results.images:
        click.secho(f"- {result}", fg="green")
    if output:
        results.write_to_file(output)


if __name__ == "__main__":
    cli()
