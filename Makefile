.PHONY: docs

init:
	# Need a way to use python3 version of pip, but `python3 -m pip` doesn't
	# work on windows, and just `python -m pip` or `pip` might use 2.7 on OSX
	python -m pip install poetry
	# Install dependencies
	poetry install --sync
	# Ignore bulk refactor/reformat changes when running `git blame`
	git config blame.ignoreRevsFile .git-blame-ignore-revs

black:
	poetry run black .

black-check:
	@echo If you actually want to reformat, run make black instead
	poetry run black . --check

flake8:
	poetry run flake8

mypy:
	poetry run mypy

tox:
	# If a developer doesn't have all the python versions installed,
	# It's OK just skip them. All versions will be tested in CI.
	poetry run tox --skip-missing-interpreters=true

# Build the docs HTML
docs-html:
	poetry run sphinx-build -W \
	-b html \
	-d docs/build/doctrees \
	docs \
	docs/build/html

# Build docs and then view them
docs-view: docs-html
	open docs/build/html/index.html

# Build docs and verify all external links work
docs: docs-html
	poetry run sphinx-build -W \
	-b linkcheck \
	-d docs/build/doctrees \
	docs \
	docs/build/html

test: black-check mypy flake8 tox docs build

coverage:
	poetry run pytest --cov=staticjinja --cov-report=xml --cov-config=setup.cfg
	# Generate the html view of the coverage results, for local viewing.
	poetry run coverage html

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
	poetry build
	poetry run twine check dist/*

publish:
	poetry publish

update:
	poetry update
	poetry install --sync
