---
description: |
    API documentation for modules: ord.

lang: en

classoption: oneside
geometry: margin=1in
papersize: a4

linkcolor: blue
links-as-notes: true
...


    
# Module `ord` {#id}

ORD: simple multi objective explanation (using unsupervised discretion)   
(c) 2023 Tim Menzies <timm@ieee.org> BSD.2   
   
USAGE:   
  ./ord.py [OPTIONS] [-g ACTIONS]   
   
OPTIONS:   
  -b  --bins   max number of bins         = 7   
  -B  --Beam   search width               = 10   
  -c  --cohen  measure of same            = .35   
  -f  --file   data file                  = "../data/auto93.csv"   
  -g  --go     startup action             = "nothing"   
  -h  --help   show help                  = False   
  -m  --min    min size                   = .5   
  -r  --rest   best times rest            = 4   
  -s  --seed   random number seed         = 937162211   
  -S  --Some   how may nums to keep       = 256   
  -w  --want   plan|monitor|xplore|doubt  = "plan"




    
## Functions


    
### Function `R` {#id}




>     def R()


random() -> x in the interval [0, 1).

    
### Function `cols2Chops` {#id}




>     def cols2Chops(
>         data
>     )




    
### Function `csv2Rows` {#id}




>     def csv2Rows(
>         file
>     )




    
### Function `ent` {#id}




>     def ent(
>         d
>     )




    
### Function `grow` {#id}




>     def grow(
>         lst,
>         bestRows,
>         restRows,
>         peeks=32,
>         beam=None
>     )




    
### Function `num2Chops` {#id}




>     def num2Chops(
>         num,
>         bestRows,
>         restRows,
>         cohen,
>         bins
>     )




    
### Function `pick` {#id}




>     def pick(
>         lst,
>         n
>     )




    
### Function `rnd` {#id}




>     def rnd(
>         x,
>         decimals=3
>     )




    
### Function `score` {#id}




>     def score(
>         b,
>         r,
>         B,
>         R
>     )


Given you've found <code>b</code> or <code>r</code> items of <code>B,[Random.random()](#ord.R "ord.R")</code>, how much do we like you?

    
### Function `sortedChops` {#id}




>     def sortedChops(
>         data,
>         bestRows,
>         restRows
>     )




    
### Function `str2thing` {#id}




>     def str2thing(
>         x: str
>     )




    
### Function `within` {#id}




>     def within(
>         x,
>         lo,
>         hi
>     )




    
### Function `x2range` {#id}




>     def x2range(
>         x,
>         ranges
>     )





    
## Classes


    
### Class `COLS` {#id}




>     class COLS(
>         names
>     )


My base objects:  pretty prints; can be initialized easily;
all content available via self.it.


    
#### Ancestors (in MRO)

* [ord.obj](#ord.obj)






    
#### Methods


    
##### Method `add` {#id}




>     def add(
>         i,
>         row
>     )




    
### Class `DATA` {#id}




>     class DATA(
>         src=[]
>     )


My base objects:  pretty prints; can be initialized easily;
all content available via self.it.


    
#### Ancestors (in MRO)

* [ord.obj](#ord.obj)






    
#### Methods


    
##### Method `add` {#id}




>     def add(
>         i,
>         row
>     )




    
##### Method `adds` {#id}




>     def adds(
>         i,
>         l
>     )




    
##### Method `clone` {#id}




>     def clone(
>         data,
>         rows=[]
>     )




    
##### Method `dist` {#id}




>     def dist(
>         i,
>         row1,
>         row2
>     )




    
##### Method `sortedRows` {#id}




>     def sortedRows(
>         i,
>         rows=None,
>         cols=None
>     )




    
##### Method `stats` {#id}




>     def stats(
>         i,
>         cols=None,
>         what='mid',
>         decimals=3
>     )




    
### Class `EG` {#id}




>     class EG










    
#### Methods


    
##### Method `DO` {#id}




>     def DO(
>         a={'__module__': 'ord', '__qualname__': 'EG', 'DO': <function EG.DO>, 'RUN': <function EG.RUN>, 'RUN1': <function EG.RUN1>, 'all': <function EG.all>, 'the': <function EG.the>, 'data': <function EG.data>, 'sorted': <function EG.sorted>, 'ideas': <function EG.ideas>}
>     )




    
##### Method `RUN` {#id}




>     def RUN(
>         a=['/opt/homebrew/bin/pdoc3', '--pdf', 'ord.py']
>     )




    
##### Method `RUN1` {#id}




>     def RUN1(
>         fun
>     )




    
##### Method `all` {#id}




>     def all()


run all actions, return sum of failures.

    
##### Method `data` {#id}




>     def data()


can we read data from disk and print its stats?

    
##### Method `ideas` {#id}




>     def ideas()


can we find good ranges?

    
##### Method `sorted` {#id}




>     def sorted()


can we sort the rows into best and rest?

    
##### Method `the` {#id}




>     def the()


show config options

    
### Class `NUM` {#id}




>     class NUM(
>         n=0,
>         s=''
>     )


My base objects:  pretty prints; can be initialized easily;
all content available via self.it.


    
#### Ancestors (in MRO)

* [ord.obj](#ord.obj)




    
#### Instance variables


    
##### Variable `kept` {#id}








    
#### Methods


    
##### Method `add` {#id}




>     def add(
>         i,
>         x
>     )




    
##### Method `dist` {#id}




>     def dist(
>         i,
>         a,
>         b
>     )




    
##### Method `div` {#id}




>     def div(
>         i,
>         decimals=None
>     )




    
##### Method `mid` {#id}




>     def mid(
>         i,
>         decimals=None
>     )




    
### Class `ROW` {#id}




>     class ROW(
>         a
>     )


My base objects:  pretty prints; can be initialized easily;
all content available via self.it.


    
#### Ancestors (in MRO)

* [ord.obj](#ord.obj)






    
### Class `SETTINGS` {#id}




>     class SETTINGS(
>         s
>     )


My base objects:  pretty prints; can be initialized easily;
all content available via self.it.


    
#### Ancestors (in MRO)

* [ord.obj](#ord.obj)






    
#### Methods


    
##### Method `cli` {#id}




>     def cli(
>         i
>     )




    
##### Method `exitWithHelp` {#id}




>     def exitWithHelp(
>         i
>     )




    
### Class `SYM` {#id}




>     class SYM(
>         n=0,
>         s=''
>     )


My base objects:  pretty prints; can be initialized easily;
all content available via self.it.


    
#### Ancestors (in MRO)

* [ord.obj](#ord.obj)






    
#### Methods


    
##### Method `add` {#id}




>     def add(
>         i,
>         x
>     )




    
##### Method `dist` {#id}




>     def dist(
>         i,
>         a,
>         b
>     )




    
##### Method `div` {#id}




>     def div(
>         i,
>         decimals=None
>     )




    
##### Method `mid` {#id}




>     def mid(
>         i,
>         decimals=None
>     )




    
### Class `obj` {#id}




>     class obj(
>         **d
>     )


My base objects:  pretty prints; can be initialized easily;
all content available via self.it.



    
#### Descendants

* [ord.COLS](#ord.COLS)
* [ord.DATA](#ord.DATA)
* [ord.NUM](#ord.NUM)
* [ord.ROW](#ord.ROW)
* [ord.SETTINGS](#ord.SETTINGS)
* [ord.SYM](#ord.SYM)



    
#### Instance variables


    
##### Variable `it` {#id}









-----
Generated by *pdoc* 0.10.0 (<https://pdoc3.github.io>).
