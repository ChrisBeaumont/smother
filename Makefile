
setup:
	python setup.py develop

test:
	smother erase
	py.test --smother=smother --smother-cover --smother-append smother
	coverage html
	coverage report --show-missing

lint:
	flake8 smother
