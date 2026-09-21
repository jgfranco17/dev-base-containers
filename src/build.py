import datetime as dt
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path

from src.clients.docker import BaseImageDefinition, DockerAccessor
from src.core.config import VARIANT_DEFINITION_FILE, BuildConfiguration

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BuildSummary:
    duration: float
    images: list[str]

    def write_to_file(self, output_path: Path) -> None:
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists():
            logger.warning(
                f"Output file {output_path} already exists, it will be overwritten"
            )
        if output_path.suffix != ".json":
            logger.warning(f"Output file {output_path} is not a JSON file")

        base_output = {
            "generated_at": dt.datetime.now(tz=dt.UTC).isoformat(),
            "build_duration": self.duration,
            "images": self.images,
        }
        content = json.dumps(base_output, indent=2)
        output_path.write_text(content)
        logger.info(f"Wrote build summary to file: {output_path}")


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

    def build_all(self) -> BuildSummary:
        """Build all Docker images in the specified directory.

        Returns:
            BuildSummary: A summary of the built Docker images.
        """
        images = []
        start_time = time.perf_counter()
        for variant in self._config.variants:
            logger.info(f"Building images for variant: {variant.name}")
            for entry in variant.matrix:
                tag = self._format_tag(entry) if entry else "latest"
                definition = BaseImageDefinition(
                    dockerfile=Path(variant.directory / "Dockerfile"),
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

        duration = time.perf_counter() - start_time
        return BuildSummary(images=images, duration=duration)
