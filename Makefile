help:
	@echo 'Usage: make [target]'
	@echo
	@echo 'Development Targets:'
	@echo '  venv      Create virtual Python environment for development.'
	@echo '  checks    Run linters and tests.'
	@echo
	@echo 'Deployment Targets:'
	@echo '  service   Remove, install, configure, and run app.'
	@echo '  rm        Remove app.'
	@echo '  help      Show this help message.'


# Development Targets
# -------------------

rmvenv:
	rm -rf ~/.venv/clog venv

venv: FORCE
	python3 -m venv ~/.venv/clog
	echo . ~/.venv/clog/bin/activate > venv
	. ./venv && pip3 install -U build twine
	. ./venv && pip3 install pylint pycodestyle pydocstyle pyflakes isort

lint:
	. ./venv && ! isort --quiet --diff . | grep .
	. ./venv && pycodestyle .
	. ./venv && pyflakes .
	. ./venv && pylint -d R0903,R0913,R0914,W0718 clog

test:
	python3 -m unittest -v

coverage:
	. ./venv && coverage run --branch -m unittest -v
	. ./venv && coverage report --show-missing
	. ./venv && coverage html

check-password:
	! grep -r '"password":' . | grep -vE '^\./[^/]*.json|Makefile|\.\.\.'

checks: lint test check-password

clean:
	rm -rf *.pyc __pycache__
	rm -rf .coverage htmlcov
	rm -rf dist clog.egg-info


# Deployment Targets
# ------------------

service: rmservice
	mkdir -p /opt/data/
	adduser --system --group --home / clog
	chown -R clog:clog . /opt/data/
	chmod 600 clog.json
	systemctl enable "$$PWD/etc/clog.service"
	systemctl daemon-reload
	systemctl start clog
	@echo Done; echo

rmservice:
	-systemctl stop clog
	-systemctl disable clog
	systemctl daemon-reload
	-deluser clog
	@echo Done; echo

FORCE:
