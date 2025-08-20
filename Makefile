.PHONY: docs

init:
	uv sync --all-groups
	# Ignore bulk refactor/reformat changes when running `git blame`
	git config blame.ignoreRevsFile .git-blame-ignore-revs

fix:
	uv run --python 3.13 ruff format .
	uv run --python 3.13 ruff check . --fix

lint:
	uv run --python 3.13 ruff format . --check
	uv run --python 3.13 ruff check .

mypy:
	uv run --python 3.13 mypy

# Build the docs HTML
docs-html:
	uv run --python 3.13 sphinx-build -W \
	-b html \
	-d docs/build/doctrees \
	docs \
	docs/build/html

# Build docs and then view them
docs-view: docs-html
	open docs/build/html/index.html

# Build docs and verify all external links work
docs: docs-html
	uv run --python 3.13 sphinx-build -W \
	-b linkcheck \
	-d docs/build/doctrees \
	docs \
	docs/build/html

# If you want a specific python version: `uv run --python 3.13 pytest`
test:
	uv run pytest

coverage:
	uv run --python 3.13 pytest --cov=staticjinja --cov-report=xml --cov-config=pyproject.toml
	# Generate the html view of the coverage results, for local viewing.
	uv run coverage html

# Make a coverage report and then view them
coverage-view: coverage
	open .htmlcov/index.html

# Use bash to evaluate this, since Make by default uses sh
coverage-upload: SHELL:=/bin/bash
coverage-upload: coverage
	# Use -Z to fail if the upload fails.
	# Use -f to specify the report file explicitly.
	# If not on CI you will need to run `export CODECOV_TOKEN="token"` before.
	bash <(curl -s https://codecov.io/bash) -Z -f coverage.xml

build:
	uv build
	uv run twine check dist/*

publish:
	uv publish

update:
	uv lock --upgrade
