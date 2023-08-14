#!/usr/bin/env python3
import random
from math import inf

class slots(dict): 
   __getattr__ = dict.get
   __setattr__ = dict.__setitem__
   __repr__    = lambda i:printd(i,i.__class__.__name__)

the=slots(cohen=.35,bins=5)

def printd(d,pre=""):
   return pre+"{" + " ".join([f":{k} {prin(v,3)}" for k,v in d.items() if k[0] != "="]) + "}"

def prin(x,d=None):
  return x.__name__ if callable(x) else (x if d is None or not isinstance(x,float) else round(x,d))

def per(a,p)  : return a[int(p*len(a))]
def median(a) : return per(a,.5)
def sd(a)     : return (per(a,.9) - per(a,.1))/2.56

def cuts(rows,at):
   xs   = sorted([row[at] for row in rows if row[at] != "?"])
   nmin = len(xs)/(the.bins - 1)
   xmin = the.cohen * sd(xs)
   lo   = xs[0]
   out  = [slots(at=at,lo=lo,hi=lo)]
   ns   = 0
   for n,x in enumerate(xs):
      if n < len(xs) - nmin and x != xs[n+1] and ns >= nmin and x-lo >= xmin:
         out += [slots(at=at,lo=hi,hi=x)]
         lo  = x
         ns  = 0
      hi  = x
      ns += 1
      out[-1].hi = x
   out[ 0].lo = -inf
   out[-1].hi = inf
   return out

class ROW(obj):
   def __init__(i,a): use=True; i.cells = a; i.cooked=a[:]

def COLS(a):
   all = [(NUM if s[0].isupper() else SYM)(at=n,name=s) for n,s in enumerate(a)]
   x,y = [],[]
   for col in all:
      if col.name[-1] != "X":
         (y if col.name[-1] in "+-!" else x).append(col)
   return slots(x=x, y=y, names=a, all=all)

def ents(rows,cols):
  rows = [row for row in rows if row.use]

def ors(x, cuts):
   for cut in cuts:
      if true(x, cut): return cut

def true(x, cut): return x=="?" or cut.lo==cut.hi==x or x > cut.lo and x <= cut.hi


[print(cut) for cut in cuts([[int(100*random.random()**2)] for _ in range(1000)],0)]

