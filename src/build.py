import datetime as dt
import logging
from pathlib import Path

import click
from docker.models.images import Image

import docker
from src.variants import VARIANT_DEFINITION_FILE, VariantDefinition

logger = logging.getLogger(__name__)


class VariantBuildClient:
    """Client for building Docker images.

    Args:
        directory (Path): The directory containing the Dockerfile.
    """

    def __init__(self, directory: Path) -> None:
        self._client = docker.from_env()

        self._directory = directory.absolute()
        variant_definition_file = self._directory / VARIANT_DEFINITION_FILE
        if not variant_definition_file.exists():
            raise FileNotFoundError(
                f"Variant definition file not found: {variant_definition_file}"
            )
        self._variant_definition = VariantDefinition.from_file(variant_definition_file)

        self._dockerfile_path = self._directory / "Dockerfile"
        if not self._dockerfile_path.exists():
            raise FileNotFoundError(f"Dockerfile not found: {self._dockerfile_path}")

        logger.info(f"Initialized client for building images from {directory}")

    def _build_single_image(
        self, dockerfile: str, name: str, args: dict[str, str] | None = None
    ) -> Image:
        """Build the Docker image using the specified Dockerfile and build arguments.

        Args:
            dockerfile (str): The name of the Dockerfile to use for building the image.
            name (str): The name to assign to the built Docker image.
            args (dict[str, str], optional): Build arguments to pass to the Docker build process.

        Returns:
            Image: The built Docker image.
        """
        logger.info(
            f"Building Docker image (dockerfile={dockerfile}, args={args}, name={name})"
        )
        image, build_logs = self._client.images.build(
            path=str(self._directory),
            dockerfile=dockerfile,
            tag=name,
            buildargs=args,
        )
        for log in build_logs:
            match log:
                case "stream":
                    click.secho(log, fg="cyan")
                case "error":
                    click.secho(log, fg="red")

        logger.info("Finished building Docker images")
        return image

    def _format_tag(self, args: dict[str, str]) -> str:
        date = dt.datetime.now(tz=dt.UTC).strftime("%Y%m%d")
        base_details = ".".join(f"{key}-{value}" for key, value in args.items())
        return f"{base_details}-{date}"

    def build_all(self) -> list[str]:
        """Build all Docker images in the specified directory.

        Returns:
            list[str]: A list of the tags of the built Docker images.
        """
        images = []
        for variant in self._variant_definition.variants:
            tag = self._format_tag(variant) if variant else "latest"
            full_image_name = f"{self._variant_definition.name}:{tag}"
            self._build_single_image(
                dockerfile=str(self._dockerfile_path),
                name=full_image_name,
                args=variant,
            )
            images.append(full_image_name)

        logger.info(f"Built {len(images)} Docker images")
        return images
