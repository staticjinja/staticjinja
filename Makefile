.PHONY: docs

init:
	# Need a way to use python3 version of pip, but `python3 -m pip` doesn't
	# work on windows, and just `python -m pip` or `pip` might use 2.7 on OSX
	pip3 install poetry
	# Install dependencies, including dev deps
	poetry install -E dev

test:
	poetry run tox

coverage:
	poetry run tox -e coverage

build:
	poetry build
	poetry run twine check dist/*
	
publish:
	poetry publish

update:
	poetry update
	poetry install -E dev

docs:
	cd docs && make html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at docs/_build/html/index.html.\n\033[0m"
