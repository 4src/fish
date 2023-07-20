<img align=right  width=350 src="/docs/right-Fly-Fishing_art.png">

<img
src="https://img.shields.io/badge/language-python3.11-yellow"> <img
src="docs/results.png"> <img
src="https://img.shields.io/badge/license-BSD2-ff69b4"> <img
src="https://img.shields.io/badge/purpose-se--ai-blueviolet"> <img
src="https://img.shields.io/badge/platform-osx,linux-pink">  <a 
href="https://zenodo.org/badge/latestdoi/631627449"><img
src="https://zenodo.org/badge/631627449.svg"></a> 

# Fish

Look around a little, catch good stuff.
o
# Rules of merging

some cuts are more ifnromative that others

unformative cuts can be ignored

keys effect: most cts are uniformative; different goals lead to different cuts


cuts can we equal frequency or equal width (i prefer equal frequency)

cuts can nonly cut whenthe n+1 thing is different to the n thing

cuts should be abovied whene cut-hi - cut.lo is too small (e.g. 33% of sd)

if a rule'attr  contains all values of a symbolic colum, ignore that attr

similarlay, if a merge runs -nf to inf, ignore it

if all attr of a rule are ignored, ignore the rule

select ranges where B> R, and score is no worse than top 10% of top


if a cut has a similar clas sdistribution to its neighbor, it can be merged

if A abd B abd merged into AB without making AB more complicated, then do that merge
