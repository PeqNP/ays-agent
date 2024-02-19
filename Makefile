init:
	pip install -r requirements.txt

test:
	pytest -vv --log-cli-level Debug ./tests

.PHONY: init test
