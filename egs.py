#!/usr/bin/env python3 -B
from eg import *
import traceback,sys,eg

def cli(d):
  for k, v in d.items():
    s = str(v)
    for j, x in enumerate(sys.argv):
      if x == ("-"+k[0]) or x == ("--"+k):
        d[k] = coerce("True" if s=="False" else ("False" if s=="True" else sys.argv[j+1]))
  return d

def run(name,fun):
  saved = {k:v for k,v in the.items()}
  random.seed(the.seed)
  try                   : out = fun()
  except Exception as e : out = False; print(traceback.format_exc())
  if out==False: print("❌ FAIL", name)
  for k,v in saved.items(): the[k]=v
  return out

def eg_settings(): print(the)
def eg_crash(): return a[1]
def eg_fail(): return 1 > 2
def eg_all(): sys.exit(sum(run(s,fun)==False for s,fun in todo.items() if s!="all"))

def eg_cols(): 
  c = COLS(["name", "Age", "Weight-"])
  c.y[2] += [100]
  print(box(x=c.x, y=c.y, all=c.all, names=c.names))
  return c.y[2] == c.all[2] 

the = cli(the)
todo = {k[3:]:fun for k,fun in locals().items() if k[:3]=="eg_"}
[run(x, todo[x]) for x in sys.argv if x in todo]
