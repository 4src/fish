-include ../config/do.mk

DO_what=      fishn: multi-objective semi-supervised explanation
DO_copyright= Copyright (c) 2023 Tim Menzies, BSD-2.
DO_repos=     . ../config ../data

install: ## load python3 packages (requires `pip3`)
	 pip3 install -qr requirements.txt

../data:
	(cd ..; git clone https://gist.github.com/d47b8699d9953eef14d516d6e54e742e.git data)

../config:
	(cd ..; git clone https://gist.github.com/42f78b8beec9e98434b55438f9983ecc.git config)

doc: ## generate documentation
	python3 -B -m pdoc  \
	--logo="https://raw.githubusercontent.com/4src/fishn/main/docs/ice.png" \
	fishn.py

tests: ## run test suite
	python3 -B fishn.py -g .
