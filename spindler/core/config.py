import logging
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, cast

import yaml

logger = logging.getLogger(__name__)

VARIANT_DEFINITION_FILE: Final[str] = "variants.yaml"


@dataclass(frozen=True)
class VariantDefinition:
    name: str
    directory: Path
    matrix: Sequence[dict[str, str]]


class BuildConfiguration:
    """Configuration for building Docker images.

    Args:
        variants (list[VariantDefinition]): A list of variant definitions for the images to be built.
    """

    def __init__(self, repository: str, variants: Sequence[VariantDefinition]) -> None:
        self._repository = repository
        self._variants = variants
        logger.info(f"Configuration initialized with {len(variants)} variants")

    @classmethod
    def from_file(
        cls: type["BuildConfiguration"], file_path: Path
    ) -> "BuildConfiguration":
        with file_path.open("r") as f:
            data = cast(dict[str, Any], yaml.safe_load(f))
            variants = []
            for v in data["images"]:
                new_variant = VariantDefinition(
                    name=v["name"],
                    directory=Path(v["directory"]),
                    matrix=[
                        {key: str(value) for key, value in dict(variant).items()}
                        for variant in v["matrix"]
                    ],
                )
                variants.append(new_variant)
            return cls(repository=data["repository"], variants=variants)

    @property
    def variants(self) -> Sequence[VariantDefinition]:
        return self._variants[:]

    @property
    def repository(self) -> str:
        return self._repository
