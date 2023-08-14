help:
	@echo 'Usage: make [target]'
	@echo
	@echo 'Development Targets:'
	@echo '  venv      Create virtual Python environment for development.'
	@echo '  checks    Run linters and tests.'
	@echo '  pull      Pull data from remote server.'
	@echo
	@echo 'Deployment Targets:'
	@echo '  service   Remove, install, configure, and run app.'
	@echo '  rm        Remove app.'
	@echo '  help      Show this help message.'


# Development Targets
# -------------------

VENV = $(HOME)/.venv/clog
BIN = $(VENV)/bin

rmvenv:
	rm -rf "$(VENV)"

venv: FORCE
	python3 -m venv "$(VENV)"
	"$(BIN)/pip3" install pylint pycodestyle pydocstyle pyflakes isort

lint:
	! "$(BIN)/isort" --quiet --diff . | grep .
	"$(BIN)/pycodestyle" .
	"$(BIN)/pyflakes" .
	"$(BIN)/pylint" -d R0903,R0913,R0914,W0718 clog.py

test:
	python3 -m unittest -v

coverage:
	"$(BIN)/coverage" run --branch -m unittest -v
	"$(BIN)/coverage" report --show-missing
	"$(BIN)/coverage" html

check-password:
	! grep -r '"password":' . | grep -vE '^\./[^/]*.json|Makefile|\.\.\.'

checks: lint test check-password

clean:
	rm -rf *.pyc __pycache__
	rm -rf .coverage htmlcov
	rm -rf dist clog.egg-info

pull:
	@echo remote: $(remote)
	[ -n "$(remote)" ]
	ssh "$(remote)" "tar -czf - -C /opt/data/ clog/" > /tmp/clog.tgz
	rm -rf clog/
	tar -xvf /tmp/clog.tgz
	du -sh /tmp/clog.tgz clog/

cat:
	cat clog/*.txt

cmsg:
	cat clog/*.txt | wc -l
	sed -n 's/\(.\{19\}\) \(.*\) PRIVMSG \([^ ]*\) :\(.*\)/\1 \3 <\2> \4/p' clog/*.txt


# Deployment Targets
# ------------------

service: rmservice
	mkdir -p /opt/data/clog/
	adduser --system --group --home / clog
	chown -R clog:clog . /opt/data/clog/
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
