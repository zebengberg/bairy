test:
	pytest

build:
	rm -rf dist
	python setup.py sdist bdist_wheel clean --all

install:
	pip install -e .

run:
	bairy

upload:
	twine upload --repository testpypi dist/*