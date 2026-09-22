# Spindler

Spindler is a CLI tool for building base images for development containers. Instead of
maintaining a sprawling set of Compose entries or one-off shell scripts, Spindler reads
a single `variants.yaml` definition and spins out every image variant in the matrix as a
tagged Docker build.

## Installation

Spindler is packaged with [uv](https://docs.astral.sh/uv/).

```bash
just install
```

This creates a virtual environment, syncs dependencies, and installs the `spindler-cli`
console script.

## Usage

```bash
uv run spindler-cli build --context docker/ubuntu --file docker/variants.yaml --output summary.json
```

- `--context` / `-c`: the Docker build context directory.
- `--file` / `-f`: the variant definition file describing the images and build matrix.
- `--output` / `-o`: optional path to write a JSON build summary.

Increase logging verbosity with `-v` (INFO) or `-vv` (DEBUG):

```bash
uv run spindler-cli -vv build -c docker/ubuntu -f docker/variants.yaml
```

## Variant definitions

Each entry in `variants.yaml` describes an image name, its build directory, and a matrix
of build arguments. Spindler builds one image per matrix entry, tagging it with the
argument values and the current date.

```yaml
repository: ghcr.io/jgfranco17/dev-base-containers
images:
  - name: ubuntu
    directory: ubuntu
    matrix:
      - UBUNTU_VERSION: "22.04"
      - UBUNTU_VERSION: "24.04"
```

## Development

```bash
just pytest
```
