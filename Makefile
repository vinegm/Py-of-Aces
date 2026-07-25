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

.PHONY: have-vhs
have-vhs:
	@if ! command -v vhs >/dev/null 2>&1; then \
		echo "error: vhs is not installed"; \
		echo "install: https://github.com/charmbracelet/vhs"; \
		exit 1; \
	fi

.PHONY: demo
demo: have-vhs
	vhs vhs/demo.tape
