from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, cast

import yaml

VARIANT_DEFINITION_FILE: Final[str] = "variants.yaml"


@dataclass(frozen=True)
class VariantDefinition:
    name: str
    variants: list[dict[str, str]]

    @classmethod
    def from_file(cls: type["VariantDefinition"], file_path: Path) -> "VariantDefinition":
        with file_path.open("r") as f:
            data = cast(dict[str, Any], yaml.safe_load(f))
            return cls(
                name=data["name"],
                variants=[
                    {key: str(value) for key, value in variant.items()}
                    for variant in data["variants"]
                ],
            )
