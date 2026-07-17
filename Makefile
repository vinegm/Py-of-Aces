.PHONY: install
install:
	uv sync

.PHONY: run
run:
	uv run pyaces

.PHONY: fmt
fmt:
	uv run ruff format .

.PHONY: fmt-check
fmt-check:
	uv run ruff format --check .

.PHONY: lint
lint:
	uv run ruff check .

.PHONY: typecheck
typecheck:
	uv run pyright

.PHONY: ci
ci: fmt-check lint typecheck
