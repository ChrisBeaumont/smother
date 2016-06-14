
setup:
	python setup.py develop

test:
	py.test
	coverage html
	coverage report

lint:
	flake8 smother
