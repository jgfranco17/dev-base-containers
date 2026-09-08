ARG UBUNTU_VERSION=22.04
FROM ubuntu:${UBUNTU_VERSION} AS base

LABEL org.opencontainers.image.owner="jgfranco17"
LABEL org.opencontainers.image.description="An Ubuntu-based sandbox environment with basic developers tools and utilities."
LABEL org.opencontainers.image.source="https://github.com/jgfranco17/dev-base-containers"

SHELL ["/bin/bash", "-c"]

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    wget \
    git \
    unzip \
    zip \
    vim \
    net-tools \
    iputils-ping \
    dnsutils \
    software-properties-common \
    ca-certificates \
    sudo \
    tree \
    jq \
    shellcheck \
    zsh \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ARG USERNAME="devuser"
RUN useradd -ms /bin/zsh ${USERNAME} \
    && usermod -aG sudo ${USERNAME} \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

ENV HOME="/home/${USERNAME}"
ENV ZDOTDIR="${HOME}"
ENV ZSH_CUSTOM="${HOME}/.oh-my-zsh/custom"
RUN bash -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" --unattended
RUN --mount=type=bind,source=scripts,target=/tmp/scripts \
    bash -c "/tmp/scripts/shell-setup.sh"

USER ${USERNAME}

FROM base AS setup

WORKDIR "${HOME}"

COPY configs/.vimrc "${HOME}/.vimrc"
COPY configs/development.zsh-theme "${HOME}/.oh-my-zsh/themes/development.zsh-theme"
COPY configs/.zshrc "${HOME}/.zshrc"

FROM setup AS sandbox

ENTRYPOINT ["/bin/zsh"]
