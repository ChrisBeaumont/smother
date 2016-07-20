
setup:
	python setup.py develop

test:
	smother erase
	py.test smother
	coverage html
	coverage report --show-missing

lint:
	flake8 smother
