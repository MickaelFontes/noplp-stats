FROM mcr.microsoft.com/devcontainers/python:3.14@sha256:97152d71a6e42cc2f4f39d68fe72a94fc10baeb203700296dd3b2db4cfaaa686

USER vscode
RUN pipx install git+https://github.com/python-poetry/poetry.git@811a12dae0fe81f199e3f1b88b8b8be9eed543c2
USER root
RUN apt-get update && apt-get install -y --no-install-recommends chromium chromium-driver
