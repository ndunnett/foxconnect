FROM ndunnett/python:latest
ARG DEBIAN_FRONTEND=noninteractive

# update and install dev tools
RUN set -eux; \
    apt update; \
    apt install -y --no-install-recommends wget zsh git; \
    apt clean; \
    rm -rf /var/lib/apt/lists/*

# create new user and home directory
ARG USERNAME=dev
RUN set -eux; \
    useradd --create-home --user-group --no-log-init "$USERNAME"; \
    mkdir -p "/home/$USERNAME/src"; \
    chown -R "$USERNAME:$USERNAME" "/home/$USERNAME"
WORKDIR "/home/$USERNAME/src"
USER "$USERNAME"

# install node and yarn
ARG NVM_GH_API=https://api.github.com/repos/nvm-sh/nvm/releases/latest
RUN set -ex; \
    NVM_VERSION="$(wget -qO - "$NVM_GH_API" | grep tag_name | cut -d\" -f4)"; \
    NVM_INSTALL_URL="https://raw.githubusercontent.com/nvm-sh/nvm/$NVM_VERSION/install.sh"; \
    wget -qO - "$NVM_INSTALL_URL" | bash; \
    export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"; \
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"; \
    nvm install 20 && corepack enable

# install Python packages
COPY --chown="$USERNAME:$USERNAME" requirements.txt /opt/requirements.txt
RUN pip install --no-cache-dir -r /opt/requirements.txt

# replace default entrypoint
COPY --chown="$USERNAME:$USERNAME" --chmod=755 entrypoint.sh /opt/entrypoint.sh
ENTRYPOINT ["/opt/entrypoint.sh"]
CMD ["sleep", "infinity"]
