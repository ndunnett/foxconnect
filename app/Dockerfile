FROM ndunnett/python:latest

# update and install dev tools
RUN set -eux; \
    DEBIAN_FRONTEND="noninteractive"; \
    apt-get update; \
    apt-get install -y wget zsh git

# install node using nvm
ARG NODE_VERSION=20.11.1
ENV NODE_VERSION="$NODE_VERSION"
ENV NVM_DIR=/usr/local/nvm
ENV NODE_PATH="$NVM_DIR/v$NODE_VERSION/lib/node_modules"
ENV PATH="$NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH"
RUN set -ex; \
    NVM_GH_API="https://api.github.com/repos/nvm-sh/nvm/releases/latest"; \
    NVM_VERSION="$(wget -qO - "$NVM_GH_API" | grep tag_name | cut -d\" -f4)"; \
    NVM_INSTALL_URL="https://raw.githubusercontent.com/nvm-sh/nvm/$NVM_VERSION/install.sh"; \
    mkdir "$NVM_DIR"; \
    wget -qO - "$NVM_INSTALL_URL" | bash; \
    . "$NVM_DIR/nvm.sh"; \
    nvm install "$NODE_VERSION"; \
    nvm alias default "$NODE_VERSION"; \
    nvm use default; \
    npm install -g npm

# create new user and home directory
RUN set -eux; \
    useradd --create-home dev; \
    mkdir /home/dev/src; \
    chown -R dev:dev /home/dev
USER dev

# install Python packages
COPY --chown=dev:dev requirements.txt /opt/requirements.txt
RUN pip install --no-cache-dir -r /opt/requirements.txt

# replace default entrypoint
COPY --chown=dev:dev --chmod=755 entrypoint.sh /opt/entrypoint.sh
ENTRYPOINT ["/opt/entrypoint.sh"]
WORKDIR /home/dev/src
CMD ["sleep", "infinity"]
