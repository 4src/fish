-include ../config/do.mk

DO_what=      FISH: look around a little, find good stuff
DO_copyright= Copyright (c) 2023 Tim Menzies, BSD-2.
DO_repos=     . ../config ../data ../lua

install: ## load python3 packages (requires `pip3`)
	 pip3 install -qr requirements.txt

../lua:
	(cd ..; git clone https://github.com/4src/lua lua)

../data:
	(cd ..; git clone https://github.com/4src/data data)

../config:
	(cd ..; git clone https://github.com/4src/config config)

tests: ## run test suite
	if ./fish.py -g ok;\
		then cp docs/pass.png docs/results.png; \
		else cp docs/fail.png docs/results.png; \
  fi

html: 
	docco -o $(HOME)/tmp  lib.lua 
	awk '/<h1>/{ print $$0; print "<p>"f"</p>";next} 1' f="`cat top.html`" ~/tmp/lib.html > tmp1
	mv tmp1 ~/tmp/lib.html
	docco -o $(HOME)/tmp  tiny.lua 
	cp ../config/docco.css $(HOME)/tmp
	open $(HOME)/tmp/lib.html

#html: docs/fish.html

pdf: $(HOME)/tmp/fish.pdf

docs/fish.html: fish.py
	 python3 -Bm pdoc -c sort_identifiers=False  \
		       --template-dir docs --force --html -o docs $<
