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

############################
Data= auto2 nasa93dem auto93 china healthCloseIsses12mths0001-hard \
      healthCloseIsses12mths0011-easy pom SSN SSM


cuts: 
	$(foreach f,$(Data), (echo ""; echo $f; ./l4.py -b 16 -s $$RANDOM  -f ../data/${f}.csv -e superCuts;);)

rulings: 
	$(foreach f,$(Data), (echo ""; echo $f; ./l4.py -s $$RANDOM  -f ../data/${f}.csv -e rulings;);)
unbests: 
	$(foreach f,$(Data), ./l4.py -s $$RANDOM  -S -b 8 -f ../data/${f}.csv -e Bests;)
bests: 
	$(foreach f,$(Data), ./l4.py -s $$RANDOM  -f ../data/${f}.csv -e Bests;)
trees: 
	$(foreach f,$(Data), (echo $f; ./l4.py -s $$RANDOM  -f ../data/${f}.csv -e trees;);)
branches: 
	$(foreach f,$(Data), (echo $f; ./l4.py -s $$RANDOM  -f ../data/${f}.csv -e branches;);)

%.awk : %.gold
	gawk -f gold.awk  $^ > $@
  
docs/%.html: %.py
	python3 -Bm pdoc -c sort_identifiers=False  -c  show_inherited_members=False \
		       --template-dir docs --force --html -o docs   $^

# 'Makefile'
MARKDOWN = pandoc --from gfm --to html --standalone
all: $(patsubst %.md,%.html,$(wildcard *.md)) Makefile

pretty:
	autopep8 -i -a --max-line-length 101 --indent-size 2 cutr.py

xclean:
	rm -f $(patsubst %.md,%.html,$(wildcard *.md))
	rm -f *.bak *~

%.xhtml: %.xmd
	$(MARKDOWN) $< --output $@

html: 
	cp docs/sample* ~/tmp
	docco -o $(HOME)/tmp cutr.py 
	#awk '/<h1>/{ print $$0; print "<p>"f"</p>";next} 1' f="`cat top.html`" ~/tmp/cutr.html > tmp1
	#mv tmp1 ~/tmp/cutr.html
	cp ../config/docco.css $(HOME)/tmp
	open $(HOME)/tmp/cutr.html

pdf: $(HOME)/tmp/cutr.pdf

docs/%.html : %.adoc
	asciidoctor -D docs -r asciidoctor-diagram $^

docs/%.md : %.py
	gawk -f py2md.awk $^ > $@; git add $@
