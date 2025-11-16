# Devcontainer with Python 3.13 and Node.js 24
FROM mcr.microsoft.com/devcontainers/base:noble

# Install dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    curl ca-certificates gnupg lsb-release software-properties-common \
    build-essential pkg-config git && \
    rm -rf /var/lib/apt/lists/*

# Install Python 3.13 via deadsnakes
RUN add-apt-repository ppa:deadsnakes/ppa -y && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3.13 python3.13-venv && \
    rm -rf /var/lib/apt/lists/* && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.13 1

# Install pip and setuptools for Python 3.13
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.13 && \
    python3.13 -m pip install --upgrade pip setuptools

# Install Node.js 24 via NodeSource
RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install PowerShell (pwsh) to allow running start.ps1/stop.ps1 inside devcontainer
USER root
RUN wget -q https://packages.microsoft.com/config/ubuntu/24.04/packages-microsoft-prod.deb -O /tmp/packages-microsoft-prod.deb \
    && dpkg -i /tmp/packages-microsoft-prod.deb \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends powershell \
    && rm -rf /var/lib/apt/lists/* /tmp/packages-microsoft-prod.deb
USER ${USERNAME}

# Create workspace folder and set user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=1000
RUN if ! getent group ${USERNAME}; then groupadd --gid ${USER_GID} ${USERNAME}; fi \
    && if ! id -u ${USERNAME} >/dev/null 2>&1; then useradd -s /bin/bash --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME}; fi
USER ${USERNAME}

WORKDIR /workspaces/web-reader

# Show versions
RUN node -v && npm -v && python3 --version && pip --version
