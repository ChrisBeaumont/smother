default: help

.PHONY: help
help:
	@echo ""
	@echo "Targets:"
	@echo "    install      Install smother on your machine"
	@echo "    setup        Setup local development environment"
	@echo "                 (remember to \`source venv/bin/activate\`)"
	@echo "    test         Run full test suite"
	@echo "    lint         Run flake8 linter"
	@echo "    teardown     WARNING: Brings repo to a pristine state."
	@echo "                 This removes ALL files not tracked by git including untracked"
	@echo "                 files and temporary files made by text editors"

WITH_ENV:=source venv/bin/activate;

venv: venv/bin/activate
venv/bin/activate: requirements_test.txt
	test -d venv || virtualenv venv
	$(WITH_ENV) pip install -Ur requirements_test.txt

.PHONY: clean
clean:
	python setup.py clean
	find smother -type d -name "__pycache__" -exec rm -fr "{}" +
	find smother -type d -name ".cache" -exec rm -fr "{}" +
	find smother -type f -name '*.pyc' -delete
	find smother -type f -name '*$py.class' -delete
	rm -f nosetests.xml
	rm -f memory_usage.txt

.PHONY: teardown
teardown: clean
	git clean -fxd

.PHONY: setup
setup: clean venv
	$(WITH_ENV) python setup.py develop

.PHONY: install
install:
	python setup.py install

.PHONY: test
test: setup
	$(WITH_ENV) smother erase
	$(WITH_ENV) py.test --smother=smother --smother-cover --smother-append smother
	$(WITH_ENV) coverage html
	$(WITH_ENV) coverage report --show-missing

.PHONY: lint
lint: venv
	$(WITH_ENV) flake8 smother
