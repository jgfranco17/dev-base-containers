import logging
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from spindler.core.errors import ClientError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BaseImageDefinition:
    """Data wrapper for a Docker image."""

    dockerfile: Path
    name: str
    tag: str
    args: dict[str, str] | None = None


@dataclass(frozen=True)
class CommandResult:
    """Result of a Docker build operation."""

    stdout: str
    stderr: str
    exit_code: int


class DockerAccessor:
    """Accessor for Docker commands using subprocess."""

    def __init__(self, context: Path, repository: str) -> None:
        self._context = context.absolute()
        if not self._context.exists():
            raise FileNotFoundError(f"Docker context not found: {self._context}")

        if repository.endswith("/"):
            repository = repository.rstrip("/")
        self._repository = repository
        if not self._repository:
            logger.warning(
                "Repository is not specified, user will have to rely on local tagging"
            )
        else:
            logger.info(f"Using repository: {self._repository}")

        logger.info(f"Initialized Docker accessor with context='{self._context}'")

    def _log_event(self, event: str, message: str) -> None:
        print(f"docker.{event.lower()} > {message}", file=sys.stderr)

    def _run(self, command: Sequence[str]) -> None:
        """Run a Docker command in the specified context."""
        full_command = ["docker", *command]
        logger.info(f"Running Docker command: {full_command} (context='{self._context}')")
        process = subprocess.Popen(
            full_command,
            cwd=self._context,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1,
        )
        stdout = ""
        while True and process.stdout:
            out = process.stdout.readline()
            if not out and process.poll() is not None:
                break
            if out:
                stdout += out
                self._log_event(command[0], out.strip())
        exit_code = process.wait()
        if exit_code != 0:
            raise ClientError(
                f"Docker command failed with exit code {exit_code}: {full_command}"
            )

    def build(self, image: BaseImageDefinition) -> str:
        """Build a Docker image and return its full name (name:tag).

        Returns:
            str: The full name of the built Docker image.
        """
        target = f"{self._repository}/{image.name}:{image.tag}"
        command = [
            "build",
            "-t",
            target,
            "-f",
            str(self._context / "Dockerfile"),
            str(self._context),
        ]
        if image.args:
            for key, value in image.args.items():
                command.extend(["--build-arg", f"{key}={value}"])

        self._run(command)
        return target
