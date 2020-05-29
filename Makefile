.PHONY: clean-pyc clean-build docs

help:
	@echo "clean - remove build artifacts"
	@echo "test - run tests quickly with the default Python"
	@echo "release - package and upload a release"

clean:
	@echo Cleaning....
	@rm -rf build
	@rm -rf dist
	@rm -rf djangoiot.egg-info
	@rm -rf .pytest_cache
	@rm -rf coverage
	@echo Removed build files
build:
	@echo building...
	@python3 setup.py sdist bdist_wheel
	@echo finished build
release:
	twine upload dist/*
