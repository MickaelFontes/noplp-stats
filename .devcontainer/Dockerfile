FROM mcr.microsoft.com/devcontainers/python:3.14@sha256:f04a1e9c29e371436d6086908eed22ac0ba087bae0f8edb826838283cf3d1726

USER vscode
RUN pipx install git+https://github.com/python-poetry/poetry.git@811a12dae0fe81f199e3f1b88b8b8be9eed543c2
USER root
RUN apt-get update && apt-get install -y --no-install-recommends chromium chromium-driver
