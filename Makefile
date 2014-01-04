.PHONY: docs

init:
	pip install -r requirements.txt

test:
	py.test test_staticjinja.py

coverage:
	py.test --verbose --cov-report term-missing --cov=staticjinja test_staticjinja.py

publish:
	python setup.py sdist upload
	python setup.py bdist_wheel upload

docs:
	cd docs && make html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at docs/_build/html/index.html.\n\033[0m"
