import json
from pathlib import Path
from typing import Any

import pytest

from multibuilder.build import BuildSummary, VariantBuildClient
from multibuilder.clients.docker import BaseImageDefinition


class TestBuildSummaryWriteToFile:
    def test_writes_expected_json_structure(self, tmp_path: Path) -> None:
        summary = BuildSummary(duration=1.23, images=["repo/app:latest"])
        output_path = tmp_path / "summary.json"

        summary.write_to_file(output_path)

        data = json.loads(output_path.read_text())
        assert data["build_duration"] == 1.23
        assert data["images"] == ["repo/app:latest"]
        assert "generated_at" in data

    def test_creates_missing_parent_directories(self, tmp_path: Path) -> None:
        summary = BuildSummary(duration=0.5, images=[])
        output_path = tmp_path / "nested" / "dir" / "summary.json"

        summary.write_to_file(output_path)

        assert output_path.exists()

    def test_overwrites_existing_file(self, tmp_path: Path) -> None:
        output_path = tmp_path / "summary.json"
        output_path.write_text("stale content")
        summary = BuildSummary(duration=2.0, images=["repo/app:v2"])

        summary.write_to_file(output_path)

        data = json.loads(output_path.read_text())
        assert data["images"] == ["repo/app:v2"]

    def test_accepts_non_json_suffix_without_raising(self, tmp_path: Path) -> None:
        summary = BuildSummary(duration=0.1, images=[])
        output_path = tmp_path / "summary.txt"

        summary.write_to_file(output_path)

        assert output_path.exists()


class TestVariantBuildClientInit:
    def test_raises_when_configuration_file_missing(self, tmp_path: Path) -> None:
        missing_file = tmp_path / "does-not-exist.yaml"

        with pytest.raises(FileNotFoundError):
            VariantBuildClient(context=tmp_path, configuration_file=missing_file)

    def test_initializes_with_valid_configuration(
        self, tmp_path: Path, variants_yaml_file: Path
    ) -> None:
        client = VariantBuildClient(
            context=tmp_path, configuration_file=variants_yaml_file
        )

        assert client._config.repository == "my-org/my-repo"

    def test_defaults_context_to_absolute_configuration_file_path(
        self, variants_yaml_file: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(variants_yaml_file.parent)

        client = VariantBuildClient(configuration_file=variants_yaml_file)

        assert client._client._context == variants_yaml_file.parent.absolute()


class TestVariantBuildClientFormatTag:
    def test_formats_tag_with_sorted_insertion_order_and_date(
        self, tmp_path: Path, variants_yaml_file: Path
    ) -> None:
        client = VariantBuildClient(
            context=tmp_path, configuration_file=variants_yaml_file
        )

        tag = client._format_tag({"version": "22.04", "arch": "amd64"})

        assert tag.startswith("version-22.04.arch-amd64-")
        date_suffix = tag.rsplit("-", maxsplit=1)[-1]
        assert len(date_suffix) == 8
        assert date_suffix.isdigit()


class TestVariantBuildClientBuildAll:
    def test_build_all_builds_every_matrix_entry(
        self,
        tmp_path: Path,
        variants_yaml_file: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        built_definitions: list[BaseImageDefinition] = []

        def fake_build(self: Any, definition: BaseImageDefinition) -> str:
            built_definitions.append(definition)
            return f"{definition.name}:{definition.tag}"

        monkeypatch.setattr(
            "src.clients.docker.DockerAccessor.build", fake_build, raising=True
        )

        client = VariantBuildClient(
            context=tmp_path, configuration_file=variants_yaml_file
        )
        summary = client.build_all()

        assert len(built_definitions) == 3
        assert len(summary.images) == 3

    def test_build_all_uses_latest_tag_for_empty_matrix_entry(
        self,
        tmp_path: Path,
        variants_yaml_file: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        built_definitions: list[BaseImageDefinition] = []

        def fake_build(self: Any, definition: BaseImageDefinition) -> str:
            built_definitions.append(definition)
            return f"{definition.name}:{definition.tag}"

        monkeypatch.setattr(
            "src.clients.docker.DockerAccessor.build", fake_build, raising=True
        )

        client = VariantBuildClient(
            context=tmp_path, configuration_file=variants_yaml_file
        )
        client.build_all()

        alpine_definition = next(d for d in built_definitions if d.name == "alpine")
        assert alpine_definition.tag == "latest"
        assert alpine_definition.args is None

    def test_build_all_reports_duration(
        self,
        tmp_path: Path,
        variants_yaml_file: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            "src.clients.docker.DockerAccessor.build",
            lambda self, definition: f"{definition.name}:{definition.tag}",
            raising=True,
        )

        client = VariantBuildClient(
            context=tmp_path, configuration_file=variants_yaml_file
        )
        summary = client.build_all()

        assert summary.duration >= 0
