SHELL := /bin/bash

.PHONY: bootstrap bootstrap-ci up down validate-cold-start

bootstrap:
	bash scripts/bootstrap.sh

bootstrap-ci:
	bash scripts/bootstrap_ci.sh

up:
	docker compose up -d

down:
	docker compose down

validate-cold-start:
	bash scripts/cold_start_validate.sh
