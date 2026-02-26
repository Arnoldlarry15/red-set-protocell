.PHONY: test test-no-cov test-ci lint

test:
	pytest tests/ -v

test-no-cov:
	pytest tests/ -v --no-cov

test-ci:
	pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=70

lint:
	python -m flake8 app/ tests/
