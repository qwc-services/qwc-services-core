all: test

sdist:
	rm -rf dist
	python3 setup.py sdist bdist_wheel
	python3 -m twine check dist/*

test: sdist
	# https://packaging.python.org/guides/using-testpypi
	python3 -m twine upload --repository testpypi dist/*
	echo Test with `python -m pip install --index-url https://test.pypi.org/simple/ qwc-services-core`

publish: sdist
	python3 -m twine upload dist/*
