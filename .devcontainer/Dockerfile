FROM mcr.microsoft.com/devcontainers/python:3.15@sha256:eb39f07323784af4c7558396808ceb01dacbe6dd7c63614f34d0235d0344a0ff

USER vscode
RUN pipx install git+https://github.com/python-poetry/poetry.git@811a12dae0fe81f199e3f1b88b8b8be9eed543c2
USER root
RUN apt-get update && apt-get install -y --no-install-recommends chromium chromium-driver
