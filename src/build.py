import datetime as dt
import logging
from pathlib import Path

from src.clients.docker import BaseImageDefinition, DockerAccessor
from src.core.config import VARIANT_DEFINITION_FILE, BuildConfiguration

logger = logging.getLogger(__name__)


class VariantBuildClient:
    """Client for building Docker images.

    Args:
        configuration_file (Path): The path to the variant definitions.
    """

    def __init__(
        self,
        context: Path | None = None,
        configuration_file: Path = Path(VARIANT_DEFINITION_FILE),
    ) -> None:
        self._config_path = configuration_file.absolute()
        if not self._config_path.exists():
            raise FileNotFoundError(
                f"Variant definition file not found: {self._config_path}"
            )
        self._config = BuildConfiguration.from_file(self._config_path)
        self._client = DockerAccessor(
            context=context.absolute() if context else Path.cwd().absolute(),
            repository=self._config.repository,
        )

        logger.info(f"Initialized client for building images from {configuration_file}")

    def _format_tag(self, args: dict[str, str]) -> str:
        date = dt.datetime.now(tz=dt.UTC).strftime("%Y%m%d")
        base_details = ".".join(f"{key}-{value}" for key, value in args.items())
        return f"{base_details}-{date}"

    def build_all(self) -> list[str]:
        """Build all Docker images in the specified directory.

        Returns:
            list[str]: A list of the full names of the built Docker images (name:tag).
        """
        images = []
        for variant in self._config.variants:
            logger.info(f"Building images for variant: {variant.name}")
            for entry in variant.matrix:
                tag = self._format_tag(entry) if entry else "latest"
                definition = BaseImageDefinition(
                    dockerfile=self._config_path.parent
                    / variant.directory
                    / "Dockerfile",
                    name=variant.name,
                    tag=tag,
                    args=entry if entry else None,
                )
                image_name = self._client.build(definition)
                images.append(image_name)
                logger.debug(f"Built image: {image_name}")

        logger.info(
            f"Built {len(images)} Docker images across {len(self._config.variants)} variants"
        )
        return images
