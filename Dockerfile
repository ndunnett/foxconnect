ARG APP_FACTORY=app:create_app
ARG APP_HOST=0.0.0.0
ARG APP_PORT=5000
ARG USERNAME=foxconnect


# ---------------------
# BASE IMAGE
# updates the ubuntu image, sets new non-root user,
# cleans up files, and sets all common environment variables
# ---------------------
FROM ubuntu:noble AS base
ARG USERNAME
ENV FC_USERNAME="$USERNAME" FC_HOME="/home/$USERNAME"
ENV FC_REPO_PATH="$FC_HOME/repo"

ARG DEBIAN_FRONTEND=noninteractive
RUN <<EOT
    set -eux
    # delete default user on new ubuntu images
    grep ubuntu /etc/passwd && \
    touch /var/mail/ubuntu && \
    chown ubuntu /var/mail/ubuntu && \
    userdel -r ubuntu
    # create new user and project directories
    useradd --create-home --user-group --no-log-init "$FC_USERNAME"
    mkdir -p "$FC_HOME" "$FC_REPO_PATH"
    chown -R "$FC_USERNAME:$FC_USERNAME" "$FC_HOME"
    # update base image
    apt update
    apt full-upgrade -y
    # find and remove redundant files (reduces final image size)
    apt install -y --no-install-recommends rdfind
    rdfind -makehardlinks true -makeresultsfile false /etc /usr /var
    apt remove -y rdfind
    # clean up
    apt autoremove -y
    apt clean
    rm -rf /root /var/cache/* /var/log/* /var/lib/apt/lists/* /var/lib/dpkg/status-old
EOT

# set locale for python
ENV LANG="C.UTF-8"

# prevent python from buffering stdout and stderr streams
ENV PYTHONUNBUFFERED="1"

# prevent uv from setting symlinks from cache
ENV UV_LINK_MODE="copy"

# set project environment variables
ARG APP_FACTORY
ARG APP_HOST
ARG APP_PORT
ENV FC_APP_FACTORY="$APP_FACTORY" FC_APP_HOST="$APP_HOST" FC_APP_PORT="$APP_PORT"
ENV UV_PROJECT_ENVIRONMENT="$FC_REPO_PATH/.venv"
ENV UV_PYTHON_INSTALL_DIR="$FC_HOME/python"
ENV PYO3_PYTHON="$FC_REPO_PATH/.venv/bin/python"
ENV QUART_FOXDATA_ICC_DUMPS_PATH="$FC_HOME/icc_dumps"
ENV QUART_FOXDATA_DATA_PICKLE_PATH="$FC_HOME/data.pickle"

USER "$FC_USERNAME"
WORKDIR "$FC_REPO_PATH"


# ---------------------
# DEV IMAGE
# installs build tools onto the base image and runs infinite loop
# ---------------------
FROM base AS dev

USER root
ARG DEBIAN_FRONTEND=noninteractive
RUN <<EOT
    set -eux
    apt update
    # install general dev tools
    apt install -y wget zsh git
    # install rust dependencies
    apt install -y ca-certificates libc6-dev pkg-config libssl-dev clang
    # cleanup
    apt clean
    rm -rf /var/lib/apt/lists/*
EOT
USER "$FC_USERNAME"

# install rust
RUN set -eux; wget -qO - https://sh.rustup.rs | sh -s -- -y
ENV PATH="$FC_HOME/.cargo/bin:$PATH"

# install nvm, node, and yarn
ARG NVM_GH_API="https://api.github.com/repos/nvm-sh/nvm/releases/latest"
ARG NVM_DIR="$FC_HOME/.nvm"
ENV NVM_DIR="$NVM_DIR" NODE_ENV="production"
RUN <<EOT
    set -ex
    NVM_VERSION="$(wget -qO - "$NVM_GH_API" | grep tag_name | cut -d\" -f4)"
    NVM_INSTALL_URL="https://raw.githubusercontent.com/nvm-sh/nvm/$NVM_VERSION/install.sh"
    wget -qO - "$NVM_INSTALL_URL" | bash
    . "$NVM_DIR/nvm.sh"
    nvm install 20
    corepack enable
EOT

# install uv
COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /uvx /bin/

# replace entrypoint
CMD sleep infinity


# ---------------------
# BUILDER IMAGE
# uses dev image to pull managed python install and build the project into a virtual environment using uv
# ---------------------
FROM dev AS builder

# configure uv to compile bytecode
ENV UV_COMPILE_BYTECODE="1"

# install project dependencies and python
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    set -eux; uv sync --frozen --no-dev --no-install-workspace --managed-python

# build project
COPY --chown="$FC_USERNAME:$FC_USERNAME" . "$FC_REPO_PATH"
RUN --mount=type=cache,target=/root/.cache/uv \
    set -eux; uv sync --frozen --no-dev --no-editable


# ---------------------
# PRODUCTION IMAGE
# copies the project runtime from the builder image into a clean base image and runs hypercorn server
# ---------------------
FROM base AS production
COPY --from=builder --chown="$FC_USERNAME:$FC_USERNAME" "$UV_PYTHON_INSTALL_DIR" "$UV_PYTHON_INSTALL_DIR"
COPY --from=builder --chown="$FC_USERNAME:$FC_USERNAME" "$UV_PROJECT_ENVIRONMENT" "$UV_PROJECT_ENVIRONMENT"
COPY --from=builder --chown="$FC_USERNAME:$FC_USERNAME" "$FC_REPO_PATH/.env*" "$FC_REPO_PATH/"

CMD . "$UV_PROJECT_ENVIRONMENT/bin/activate"; \
    hypercorn "$FC_APP_FACTORY()" --bind "$FC_APP_HOST:$FC_APP_PORT"
