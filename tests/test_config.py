from pathlib import Path

import pytest

from spindler.core.config import (
    VARIANT_DEFINITION_FILE,
    BuildConfiguration,
    VariantDefinition,
)


class TestVariantDefinition:
    def test_stores_provided_fields(self) -> None:
        variant = VariantDefinition(
            name="ubuntu",
            directory=Path("docker/ubuntu"),
            matrix=[{"version": "22.04"}],
        )

        assert variant.name == "ubuntu"
        assert variant.directory == Path("docker/ubuntu")
        assert variant.matrix == [{"version": "22.04"}]

    def test_is_frozen(self) -> None:
        variant = VariantDefinition(name="ubuntu", directory=Path("."), matrix=[])

        with pytest.raises(AttributeError):
            variant.name = "alpine"  # type: ignore[misc]


class TestBuildConfigurationFromFile:
    def test_parses_repository_and_variants(self, variants_yaml_file: Path) -> None:
        config = BuildConfiguration.from_file(variants_yaml_file)

        assert config.repository == "my-org/my-repo"
        assert len(config.variants) == 2

    def test_parses_variant_names_and_directories(self, variants_yaml_file: Path) -> None:
        config = BuildConfiguration.from_file(variants_yaml_file)

        ubuntu = next(v for v in config.variants if v.name == "ubuntu")
        assert ubuntu.directory == Path("docker/ubuntu")

    def test_matrix_values_are_coerced_to_strings(self, variants_yaml_file: Path) -> None:
        config = BuildConfiguration.from_file(variants_yaml_file)

        ubuntu = next(v for v in config.variants if v.name == "ubuntu")
        assert ubuntu.matrix == [
            {"version": "22.04", "arch": "amd64"},
            {"version": "24.04", "arch": "arm64"},
        ]
        for entry in ubuntu.matrix:
            for value in entry.values():
                assert isinstance(value, str)

    def test_variant_with_empty_matrix_entry_is_preserved(
        self, variants_yaml_file: Path
    ) -> None:
        config = BuildConfiguration.from_file(variants_yaml_file)

        alpine = next(v for v in config.variants if v.name == "alpine")
        assert alpine.matrix == [{}]

    def test_raises_when_file_missing(self, tmp_path: Path) -> None:
        missing_path = tmp_path / "does-not-exist.yaml"

        with pytest.raises(FileNotFoundError):
            BuildConfiguration.from_file(missing_path)

    def test_raises_when_required_key_missing(self, tmp_path: Path) -> None:
        bad_file = tmp_path / "variants.yaml"
        bad_file.write_text("images: []\n")

        with pytest.raises(KeyError):
            BuildConfiguration.from_file(bad_file)


class TestBuildConfigurationAccessors:
    def test_variants_property_returns_copy(self) -> None:
        original = [VariantDefinition(name="a", directory=Path("."), matrix=[])]
        config = BuildConfiguration(repository="repo", variants=original)

        returned = config.variants
        returned.append(  # type: ignore[attr-defined]
            VariantDefinition(name="b", directory=Path("."), matrix=[])
        )

        assert len(config.variants) == 1

    def test_repository_property(self) -> None:
        config = BuildConfiguration(repository="my-repo", variants=[])

        assert config.repository == "my-repo"


def test_variant_definition_file_constant_is_expected_default() -> None:
    assert VARIANT_DEFINITION_FILE == "variants.yaml"
