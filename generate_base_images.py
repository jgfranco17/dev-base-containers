"""Generate base images for development containers.

We use Python scripting instead of compose to make a one-stop shop for generating
the images, instead of relying on separate multiple entries in a compose file.
Since the pattern is pretty consistent, using a Python script allows us to centralize
and automate the generation process efficiently.
"""

import argparse
import logging
from pathlib import Path

import click

from src.build import VariantBuildClient

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="[%(asctime)s][%(levelname)8s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate base images for development containers."
    )
    parser.add_argument(
        "--context",
        "-c",
        type=Path,
        default=Path.cwd(),
        help="The context directory for the Docker build.",
    )
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        help="The directory containing the Dockerfile and variant definition file.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="The output file for the build summary",
    )
    args = parser.parse_args()

    build_client = VariantBuildClient(
        context=args.context, configuration_file=Path(args.file)
    )
    results = build_client.build_all()
    click.secho(f"Built {len(results.images)} images!", fg="green")
    for result in results.images:
        click.secho(f"- {result}", fg="green")
    if output_file := args.output:
        results.write_to_file(Path(output_file))


if __name__ == "__main__":
    main()
