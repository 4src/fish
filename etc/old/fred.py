#!/usr/bin/env python3 -B
"""
cutr: to understand "it",  cut "it" up, then seek patterns in the pieces. E.g. here
we use cuts for multi- objective, semi- supervised, rule-based explanation.
(c) Tim Menzies <timm@ieee.org>, BSD-2 license

OPTIONS:
  -b --bins   initial number of bins     = 16
  -c --cohen  small delta = cohen*stdev  = .35
  -f --file   where to read data         = ../data/auto93.csv
  -h --help   show help                  = False
  -s --seed   random number seed         = 1234567891
  -m --min    minimum size              = .5
  -r --rest   |rest| = |best|*rest       = 3
"""
import sys,ast,re

def coerce(x):
   try : return ast.literal_eval(x)
   except Exception: return x.strip()

class slots(dict): __getattr__ = dict.get 
the = slots(**{m[1]: coerce(m[2]) 
               for m in re.finditer( r"\n\s*-\w+\s*--(\w+).*=\s*(\S+)",__doc__)})

def cli2dict(d):
   for k, v in d.items():
      s = str(v)
      for j, x in enumerate(sys.argv):
         if ("-"+k[0]) == x or ("--"+k) == x:
            d[k] = coerce("True" if s == "False" else 
                          ("False" if s == "True" else sys.argv[j+1]))
#---------------------------------------------
if __name__ == "__main__": 
   cli2dict(the)
   print(the)
   if the.help: print(__doc__)
