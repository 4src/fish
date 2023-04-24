# vim: set ts=2 sw=2 et:
from functools      import cmp_to_key as cmp2key
from typing         import Dict, Any, List
from termcolor      import colored
from copy           import deepcopy
import random, math, ast, sys, re, os

class obj(object):
  id=0
  def __init__(i, **d): i.__dict__.update(**i.slots(**d)); i.id = obj.id = obj.id+1
  def slots(i,**d)    : return d
  def __repr__(i)     : return i.__class__.__name__+showd(i.__dict__)
  def __hash__(i)     : return i.id

def entropy(d):
  N = sum((d[k] for k in d))
  return -sum((n/N*math.log(n/N,2) for n in d.values() if n > 0))

def showd(d): return "{"+(" ".join([f":{k} {show(v)}"
                         for k,v in sorted(d.items()) if k[0]!="_"]))+"}"

def show(x):
  if callable(x)         : return x.__name__+'()'
  if isinstance(x,float) : return f"{x:.2f}"
  return x

def prin(*l) :  print(*l,end="")
def round2(x):  return round(x, ndigits=2)
def yell(c,*s): print(colored(''.join(s),"light_"+c,attrs=["bold"]),end="")

def coerce(x):
  try   : x = ast.literal_eval(x)
  except: pass
  return x

def main(help,the,egs):
  print(help)
  if the.help: return yell("cyan",help.split("\nNOTES")[0])
  return sum([eg(name,the,egs) for name in dir(egs)
             if name[0] !="_" and (the.go=="." or the.go==name)])

def cli(d):
  for k,v in d.__dict__.items():
    v = str(v)
    for j,x in enumerate(sys.argv):
      if ("-"+k[0]) == x or ("--"+k) == x:
        v= "False" if v=="True" else ("True" if v=="False" else sys.argv[j+1])
        d.__dict__[k] = coerce(v)
  return d

def eg(name, the,egs):
  b4 = {k:v for k,v in the.__dict__.items()}
  f  = getattr(egs,name," ")
  yell("yellow","# ",name," ")
  random.seed(the.seed)
  tmp = f()
  yell("red"," FAIL\n") if tmp==False else yell("green", " PASS\n")
  for k in b4: the.__dict__[k] = b4[k]
  return 1 if tmp==False else 0
