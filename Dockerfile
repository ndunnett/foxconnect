ARG APP_FACTORY=app:create_app
ARG APP_HOST=0.0.0.0
ARG APP_PORT=5000
ARG USERNAME=foxconnect


FROM ndunnett/python:noble-3.13 as base
ARG APP_FACTORY
ARG APP_HOST
ARG APP_PORT
ARG USERNAME
ENV FC_APP_FACTORY="$APP_FACTORY" FC_APP_HOST="$APP_HOST" FC_APP_PORT="$APP_PORT"
ENV FC_USERNAME="$USERNAME" FC_HOME="/home/$USERNAME"
ENV FC_REPO_PATH="$FC_HOME/repo"
ENV QUART_FOXDATA_ICC_DUMPS_PATH="$FC_HOME/icc_dumps"
ENV QUART_FOXDATA_DATA_PICKLE_PATH="$FC_HOME/data.pickle"

# create new user and project directories
RUN set -eux; \
    useradd --create-home --user-group --no-log-init "$FC_USERNAME"; \
    mkdir -p "$FC_HOME" "$FC_REPO_PATH"; \
    chown -R "$FC_USERNAME:$FC_USERNAME" "$FC_HOME"
WORKDIR "$FC_REPO_PATH"


FROM base AS dev
ARG DEBIAN_FRONTEND=noninteractive

# update and install dev tools
RUN set -eux; \
    apt update; \
    apt install -y wget zsh git; \
    apt clean; \
    rm -rf /var/lib/apt/lists/*

# change user
USER "$FC_USERNAME"

# install uv
RUN set -eux; \
    wget -qO - https://astral.sh/uv/install.sh | sh

# install rust
RUN set -eux; \
    wget -qO - https://sh.rustup.rs | sh -s -- -y

# install nvm, node, yarn
ARG NVM_GH_API=https://api.github.com/repos/nvm-sh/nvm/releases/latest
ARG NVM_DIR="$FC_HOME/.nvm"
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

# build project
COPY --chown="$FC_USERNAME:$FC_USERNAME" . "$FC_REPO_PATH"
RUN set -ex; \
    . "$FC_HOME/.cargo/env"; \
    uv sync


FROM base AS production

# copy built project and set user
USER "$FC_USERNAME"
COPY --from=builder --chown="$FC_USERNAME:$FC_USERNAME" "$FC_REPO_PATH" "$FC_REPO_PATH"

# replace entrypoint
CMD . "$FC_REPO_PATH/.venv/bin/activate"; \
    hypercorn "$FC_APP_FACTORY()" --bind "$FC_APP_HOST:$FC_APP_PORT"
