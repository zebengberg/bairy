test:
	pytest

build:
	rm -rf dist
	python setup.py sdist bdist_wheel clean --all
	# showing wheel contents
	unzip -l dist/*.whl
	twine check dist/*

install:
	pip install -e .

run:
	bairy

upload:
	twine upload dist/*
