from pathlib import Path

import pytest


@pytest.fixture
def tmp_dir(tmp_path: Path) -> Path:
    """A temporary directory usable as a build context or output root."""
    return tmp_path


@pytest.fixture
def variants_yaml_content() -> str:
    return """
repository: my-org/my-repo
images:
  - name: ubuntu
    directory: docker/ubuntu
    matrix:
      - version: "22.04"
        arch: amd64
      - version: "24.04"
        arch: arm64
  - name: alpine
    directory: docker/alpine
    matrix:
      - {}
"""


@pytest.fixture
def variants_yaml_file(tmp_path: Path, variants_yaml_content: str) -> Path:
    file_path = tmp_path / "variants.yaml"
    file_path.write_text(variants_yaml_content)
    return file_path
