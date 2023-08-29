#!/usr/bin/env python3 -B
from eg import *
import sys

def cli(d):
  for k, v in d.items():
    s = str(v)
    for j, x in enumerate(sys.argv):
      if ("-"+k[0])==x or ("--"+k)==x:
        d[k] = coerce("True" if s=="False" else ("False" if s=="True" else sys.argv[j+1]))
  return d

def run(name,fun):
  saved = {k:v for k,v in  the.items()}
  random.seed(the.seed)
  out = fun()
  if out==False: print("❌ FAIL", name)
  for k,v in saved.items(): the[k]=v
  return out
 
def eg_settings(): print(the)
def eg_fail(): return 1 > 2
def eg_all(): sys.exit(sum(run(s,fun)==False for s,fun in todo.items() if s!="all"))

the = cli(the)
todo = {k[3:]:fun for k,fun in locals().items() if k[:3]=="eg_"}
[run(x, todo[x]) for x in sys.argv if x in todo]
