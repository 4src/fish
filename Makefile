-include ../config/do.mk

DO_what=      FISH: look around a little, find good stuff
DO_copyright= Copyright (c) 2023 Tim Menzies, BSD-2.
DO_repos=     . ../config ../data

install: ## load python3 packages (requires `pip3`)
	 pip3 install -qr requirements.txt

../data:
	(cd ..; git clone https://gist.github.com/d47b8699d9953eef14d516d6e54e742e.git data)

../config:
	(cd ..; git clone https://gist.github.com/42f78b8beec9e98434b55438f9983ecc.git config)

tests: ## run test suite
	if ./fish.py -ok;\
		then cp docs/pass.png docs/results.png; \
		else cp docs/fail.png docs/results.png; \
  fi

html: docs/fish.html

pdf: $(HOME)/tmp/fish.pdf

docs/fish.html: fish.py
	 python3 -Bm pdoc -c sort_identifiers=False  \
		       --template-dir docs --force --html -o docs $<
