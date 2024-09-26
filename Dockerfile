ARG APP_FACTORY=app:create_app
ARG APP_HOST=0.0.0.0
ARG APP_PORT=5000
ARG USERNAME=foxconnect
ARG PROJECT_DIR=/fc


FROM ndunnett/python:noble-3.12 as base
ARG APP_FACTORY
ARG APP_HOST
ARG APP_PORT
ARG USERNAME
ARG PROJECT_DIR
ENV APP_FACTORY="$APP_FACTORY" APP_HOST="$APP_HOST" APP_PORT="$APP_PORT"
ENV PROJECT_DIR="$PROJECT_DIR" VENV_DIR="$PROJECT_DIR/.venv" REPO_DIR="$PROJECT_DIR/repo"
ENV QUART_FOXDATA_ICC_DUMPS_PATH="$PROJECT_DIR/icc_dumps"
ENV QUART_FOXDATA_DATA_PICKLE_PATH="$PROJECT_DIR/data.pickle"

# create new user and project directories
RUN set -eux; \
    useradd --create-home --user-group --no-log-init "$USERNAME"; \
    mkdir -p "/home/$USERNAME" "$REPO_DIR" "$VENV_DIR"; \
    chown -R "$USERNAME:$USERNAME" "/home/$USERNAME" "$PROJECT_DIR"
WORKDIR "$REPO_DIR"


FROM base AS dev
ARG USERNAME
ARG PROJECT_DIR
ARG DEBIAN_FRONTEND=noninteractive

# update and install dev tools
RUN set -eux; \
    apt update; \
    apt install -y wget zsh git; \
    apt clean; \
    rm -rf /var/lib/apt/lists/*

# change user
USER "$USERNAME"

# install uv and set up venv
RUN set -eux; \
    wget -qO - https://astral.sh/uv/install.sh | sh; \
    . "/home/$USERNAME/.cargo/env"; \
    uv venv "$VENV_DIR"

# install rust
RUN set -eux; \
    wget -qO - https://sh.rustup.rs | sh -s -- -y

# install nvm, node, yarn
ARG NVM_GH_API=https://api.github.com/repos/nvm-sh/nvm/releases/latest
ARG NVM_DIR="/home/$USERNAME/.nvm"
ARG NODE_ENV=production
ENV NVM_DIR="$NVM_DIR" NODE_ENV="$NODE_ENV"
RUN set -ex; \
    NVM_VERSION="$(wget -qO - "$NVM_GH_API" | grep tag_name | cut -d\" -f4)"; \
    NVM_INSTALL_URL="https://raw.githubusercontent.com/nvm-sh/nvm/$NVM_VERSION/install.sh"; \
    wget -qO - "$NVM_INSTALL_URL" | bash; \
    . "$NVM_DIR/nvm.sh"; \
    nvm install 20; \
    corepack enable

# replace entrypoint
CMD sleep infinity


FROM dev AS builder
ARG USERNAME
ARG PROJECT_DIR

# build project
COPY --chown="$USERNAME:$USERNAME" . "$REPO_DIR"
RUN set -ex; \
    . "/home/$USERNAME/.cargo/env"; \
    . "$VENV_DIR/bin/activate"; \
    cd "$REPO_DIR" && \
    uv pip install --editable .


FROM base AS production
ARG USERNAME
ARG PROJECT_DIR

# copy built project and set user
USER "$USERNAME"
COPY --from=builder --chown="$USERNAME:$USERNAME" "$PROJECT_DIR" "$PROJECT_DIR"

# replace entrypoint
CMD . "$VENV_DIR/bin/activate"; \
    hypercorn "$APP_FACTORY()" --bind "$APP_HOST:$APP_PORT"
