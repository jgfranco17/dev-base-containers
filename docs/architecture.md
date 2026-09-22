# Spindler — Product & Design Overview

## Problem

Building base images for development containers traditionally means either:

- maintaining a growing Compose file with one service per image variant, or
- writing one-off shell scripts per Dockerfile/version combination.

Both approaches scale poorly. Adding a new OS version, or a new variant
entirely, means copy-pasting build stanzas and manually keeping tags,
arguments, and registry paths in sync. There's no single source of truth for
"what images do we build" and no consistent way to know what was actually
produced by a given run.

## What Spindler is

Spindler is a small, focused CLI tool that turns "what images do we build" into
a single declarative file, and turns "build them" into a single command.

Instead of N scripts or N Compose services, a project maintains one
`variants.yaml` describing:

- which base images exist (e.g. `ubuntu`),
- where each one's Dockerfile lives,
- and the matrix of build arguments to produce (e.g. every supported OS
  version).

Spindler reads that file and produces every image in the matrix as a tagged
Docker build, in one invocation.

## Goals

- **Single source of truth** for which base images exist and how they're
  parameterized.
- **Low ceremony to add a variant**: adding a new OS version or a new image
  family is a YAML edit, not a new script.
- **Predictable, auditable builds**: every run can emit a machine-readable
  summary (what was built, how long it took) for CI to consume or archive.
- **Good operator experience**: adjustable log verbosity, clear pass/fail
  signal, one console command to remember (`spindler-cli`).

## Non-goals

- Spindler does not push images to a registry or manage registry credentials
  — that's a CI concern, layered on top of Spindler's output.
- Spindler does not template or generate Dockerfiles — it builds existing
  ones with different arguments.
- Spindler is not a general-purpose build system (no dependency graph,
  caching strategy, or parallel scheduling beyond what Docker itself does).

## Intended users

- **Maintainers of this repo**, adding/updating base image definitions.
- **CI pipelines**, invoking Spindler non-interactively and consuming its
  JSON summary as a build artifact.

## High-level design

At the highest level, Spindler is three concerns layered on top of each other:

1. **Definition** — a `variants.yaml` file is the declarative contract for
   what gets built. This is the artifact a maintainer edits; they never need
   to touch Python code to add a new image or version.
2. **Orchestration** — given a definition, Spindler figures out the full set
   of (image × build-arg combination) pairs to build, and drives each one
   through to completion, tagging and tracking the result.
3. **Reporting** — the outcome of a run (images produced, time taken) is
   surfaced both to a human (console output) and to a machine (optional JSON
   summary file), so CI can key off a successful/failed run without scraping
   logs.

This separation means each concern can evolve independently: the definition
format can gain new fields, the orchestration can swap in a different build
backend, and the reporting format can add fields — without the others needing
to change.

## Key design decisions

- **Declarative over imperative**: the build matrix lives in data as a configuration
  file, not as code. This is the main lever for the "low ceremony to add a variant" goal.
- **One CLI, one binary**: `spindler-cli` is the single entry point,
  distributed as an installable package rather than a script users copy
  around. This makes versioning, dependency management, and "how do I run
  this" unambiguous.
- **CI-first output**: the JSON summary exists specifically so pipelines can
  treat a Spindler run as a build step with real outputs (image list,
  duration), rather than a shell script whose only signal is exit code.
- **Fail-fast builds**: a broken variant stops the run rather than silently
  producing a partial/inconsistent set of images. This trades off "always
  get whatever succeeded" for "never publish half a matrix without knowing."

## Success criteria

- Adding a new base image or version requires only a `variants.yaml` change.
- A single command builds every defined image variant, with clear
  success/failure signal.
- CI can consume a build run's output programmatically (not just via log
  scraping) to decide what to publish.

## Open questions / future considerations

- Should partial failures produce a partial summary (best-effort) instead of
  aborting the whole run?
- Should Spindler take on pushing/publishing, or stay strictly build-only and
  leave registry interaction to CI?
- Should the definition format support per-variant Dockerfile names, or
  multi-stage/build-backend selection (e.g. `buildx`) as the image set grows?
- Should there be a "dry run" / "list" mode to preview what a given
  `variants.yaml` would build, without invoking Docker?
