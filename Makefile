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

docs/%.html: %.py
	python3 -Bm pdoc -c sort_identifiers=False  -c  show_inherited_members=False \
		       --template-dir docs --force --html -o docs   $^

# 'Makefile'
MARKDOWN = pandoc --from gfm --to html --standalone
all: $(patsubst %.md,%.html,$(wildcard *.md)) Makefile

pretty:
	autopep8 -i -a --max-line-length 101 --indent-size 2 samplr.py

xclean:
	rm -f $(patsubst %.md,%.html,$(wildcard *.md))
	rm -f *.bak *~

%.xhtml: %.xmd
	$(MARKDOWN) $< --output $@

html: 
	cp docs/sample* ~/tmp
	docco -o $(HOME)/tmp samplr.py 
	#awk '/<h1>/{ print $$0; print "<p>"f"</p>";next} 1' f="`cat top.html`" ~/tmp/samplr.html > tmp1
	#mv tmp1 ~/tmp/samplr.html
	cp ../config/docco.css $(HOME)/tmp
	open $(HOME)/tmp/samplr.html

pdf: $(HOME)/tmp/samplr.pdf
