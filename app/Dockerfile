FROM ubuntu:22.04

# set noninteractive environment variable to prevent user prompts during build
ENV DEBIAN_FRONTEND="noninteractive"

# prevent buffering of stdout and stderr
ENV PYTHONUNBUFFERED=1

# configure apt to never install additional recommended or suggested packages
RUN apt-config dump | grep -we Recommends -e Suggests | sed s/1/0/ | tee /etc/apt/apt.conf.d/999-no-install-recommends

# replace mirror URLs with Australian servers to prevent horrifically slow builds
RUN sed --in-place --regexp-extended "s#(//)(archive\.ubuntu)#\1au.\2#" /etc/apt/sources.list

# update and install packages
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install software-properties-common gnupg wget git zsh -y

# install node using nvm
RUN mkdir /usr/local/nvm
ENV NVM_DIR /usr/local/nvm
ENV NODE_VERSION 20.9.0
RUN wget -q -O - https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash && \
    . $NVM_DIR/nvm.sh && \
    nvm install $NODE_VERSION && \
    nvm alias default $NODE_VERSION && \
    nvm use default
ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH $NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH
RUN npm install -g npm

# add deadsnakes repository for newer releases of Python
RUN add-apt-repository ppa:deadsnakes/ppa -y && apt-get update

# install Python 3.12 and latest version of pip
RUN apt-get purge .*python.* -y && \
    apt-get install python3.12 -y && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1 && \
    wget -q -O - https://bootstrap.pypa.io/get-pip.py | python

# remove unneeded packages and clean apt cache
RUN apt-get purge software-properties-common -y && \
    apt-get clean -y && \
    apt-get autoclean -y && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# create new user and home directory
RUN useradd --create-home dev && mkdir /home/dev/src && chown -R dev:dev /home/dev

# install Python packages
WORKDIR /home/dev/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# replace default entrypoint
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh
ENTRYPOINT ["/home/dev/src/app/entrypoint.sh"]

USER dev
WORKDIR /home/dev/src
CMD ["sleep", "infinity"]
