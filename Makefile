init:
	pip3 install -r requirements.txt

test:
	pytest -vv --log-cli-level Debug ./tests

build:
	python3 setup.py sdist bdist_wheel

install:
	pip3 install dist/ays_agent-1.0-py3-none-any.whl --force-reinstall

.PHONY: init test build install
