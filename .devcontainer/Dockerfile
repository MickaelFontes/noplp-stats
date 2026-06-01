FROM mcr.microsoft.com/devcontainers/python:3.14@sha256:882b17d068262c7af4300180ead0ee14423d2c03393778c92435b0ca642dea07

USER vscode
RUN pipx install git+https://github.com/python-poetry/poetry.git@811a12dae0fe81f199e3f1b88b8b8be9eed543c2
USER root
RUN apt-get update && apt-get install -y --no-install-recommends chromium chromium-driver
