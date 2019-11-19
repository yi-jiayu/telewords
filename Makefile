.PHONY: test format start coverage

test:
	PYTHONHASHSEED=0 pipenv run python -m pytest -vv

format:
	pipenv run black .

start:
	pipenv run python server.py

coverage:
	PYTHONHASHSEED=0 pipenv run python -m pytest --cov