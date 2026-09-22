import subprocess
from pathlib import Path
from typing import Any

import pytest

from spindler.clients.docker import BaseImageDefinition, DockerAccessor
from spindler.core.errors import ClientError


class FakePopen:
    """Minimal stand-in for subprocess.Popen used to drive DockerAccessor._run."""

    def __init__(self, lines: list[str], exit_code: int) -> None:
        self._lines = iter([*lines, ""])
        self._exit_code = exit_code
        self.stdout = self

    def readline(self) -> str:
        try:
            return next(self._lines)
        except StopIteration:
            return ""

    def poll(self) -> int | None:
        return self._exit_code

    def wait(self) -> int:
        return self._exit_code


@pytest.fixture
def build_context(tmp_path: Path) -> Path:
    context = tmp_path / "context"
    context.mkdir()
    return context


@pytest.fixture
def accessor(build_context: Path) -> DockerAccessor:
    return DockerAccessor(context=build_context, repository="my-org/my-repo")


@pytest.fixture
def image_definition(build_context: Path) -> BaseImageDefinition:
    return BaseImageDefinition(
        dockerfile=build_context / "Dockerfile",
        name="ubuntu",
        tag="latest",
        args={"VERSION": "22.04"},
    )


class TestDockerAccessorInit:
    def test_raises_when_context_missing(self, tmp_path: Path) -> None:
        missing_context = tmp_path / "nowhere"

        with pytest.raises(FileNotFoundError):
            DockerAccessor(context=missing_context, repository="my-repo")

    def test_strips_trailing_slash_from_repository(self, build_context: Path) -> None:
        accessor = DockerAccessor(context=build_context, repository="my-repo/")

        definition = BaseImageDefinition(
            dockerfile=build_context / "Dockerfile", name="app", tag="latest"
        )
        target = f"{accessor._repository}/{definition.name}:{definition.tag}"

        assert target == "my-repo/app:latest"

    def test_accepts_empty_repository(self, build_context: Path) -> None:
        accessor = DockerAccessor(context=build_context, repository="")

        assert accessor._repository == ""


class TestDockerAccessorBuild:
    def test_build_returns_full_image_name(
        self,
        accessor: DockerAccessor,
        image_definition: BaseImageDefinition,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            subprocess,
            "Popen",
            lambda *args, **kwargs: FakePopen(lines=["Step 1/1"], exit_code=0),
        )

        result = accessor.build(image_definition)

        assert result == "my-org/my-repo/ubuntu:latest"

    def test_build_passes_build_args_to_command(
        self,
        accessor: DockerAccessor,
        image_definition: BaseImageDefinition,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        captured_command: list[str] = []

        def fake_popen(command: list[str], **kwargs: Any) -> FakePopen:
            captured_command.extend(command)
            return FakePopen(lines=[], exit_code=0)

        monkeypatch.setattr(subprocess, "Popen", fake_popen)

        accessor.build(image_definition)

        assert "--build-arg" in captured_command
        assert "VERSION=22.04" in captured_command

    def test_build_omits_build_args_when_none(
        self,
        accessor: DockerAccessor,
        build_context: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        captured_command: list[str] = []

        def fake_popen(command: list[str], **kwargs: Any) -> FakePopen:
            captured_command.extend(command)
            return FakePopen(lines=[], exit_code=0)

        monkeypatch.setattr(subprocess, "Popen", fake_popen)

        definition = BaseImageDefinition(
            dockerfile=build_context / "Dockerfile", name="ubuntu", tag="latest"
        )
        accessor.build(definition)

        assert "--build-arg" not in captured_command

    def test_build_raises_client_error_on_nonzero_exit(
        self,
        accessor: DockerAccessor,
        image_definition: BaseImageDefinition,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            subprocess,
            "Popen",
            lambda *args, **kwargs: FakePopen(lines=["error output"], exit_code=1),
        )

        with pytest.raises(ClientError):
            accessor.build(image_definition)

    def test_run_invokes_docker_prefixed_command(
        self,
        accessor: DockerAccessor,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        captured: dict[str, Any] = {}

        def fake_popen(command: list[str], **kwargs: Any) -> FakePopen:
            captured["command"] = command
            captured["cwd"] = kwargs.get("cwd")
            return FakePopen(lines=[], exit_code=0)

        monkeypatch.setattr(subprocess, "Popen", fake_popen)

        accessor._run(["ps"])

        assert captured["command"][0] == "docker"
        assert captured["command"][1] == "ps"
        assert captured["cwd"] == accessor._context
