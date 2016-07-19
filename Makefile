
setup:
	python setup.py develop

test:
	smother erase
	py.test
	coverage html
	coverage report --show-missing

lint:
	flake8 smother
