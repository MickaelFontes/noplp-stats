SHELL=/bin/bash -o pipefail

# version settings
COMMIT?=$(shell git rev-parse HEAD)
DOCKER_IMAGE="noplp-stats"

.DEFAULT_GOAL := help

.PHONY: help
help: #Doc: display this help
	@echo "$$(grep -hE '^\S+:.*#Doc:' $(MAKEFILE_LIST) | sed -e 's/:.*#Doc:\s*/:/' -e 's/^\(.\+\):\(.*\)/\1:-\ \2/' | column -c2 -t -s :)"

##
## Formatters
##

.PHONY: format-black
format-black: #Doc: run black (code formatter)
	black .

.PHONY: format-isort
format-isort: #Doc: run isort (imports formatter)
	isort .

.PHONY: format
format: #Doc: run all formatters
	make format-isort && make format-black

##
## Linters
##

.PHONY: lint-black
lint-black: #Doc: run black in linting mode
	black . --check

.PHONY: lint-isort
lint-isort: #Doc: run isort in linting mode
	isort . --check

.PHONY: lint-pylint
lint-pylint: #Doc: run pylint (code linter)
	pylint app.py noplp pages

.PHONY: lint-flake8
lint-flake8: #Doc: run flake8 (code linter)
	flake8 --config=.flake8

##
## Test & scripts
##

.PHONY: app-debug
app-debug: #Doc: run Dash app in debug mode
	export DASH_DEBUG=True && python app.py

.PHONY: app
app: #Doc: run Dash app in production mode
	gunicorn -b :8080 -w 1 app:server

##
## Image & deployment
##

.PHONY: docker
docker: #Doc: build Docker image
	DOCKER_BUILDKIT=1 docker build . --target=runtime -f Dockerfile.dev --tag "$(DOCKER_IMAGE):$(COMMIT)"
	docker tag $(DOCKER_IMAGE):$(COMMIT) $(DOCKER_IMAGE):dev
