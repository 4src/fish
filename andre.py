#!/usr/bin/env python3
from collections import Counter
from math import log,inf
import random

class obj(dict): 
   oid = -1
   __getattr__ = dict.get
   __setattr__ = dict.__setitem__
   __hash__    = lambda i : i._id
   __repr__    = lambda i : printd(i,i.__class__.__name__)
   def __init__(i,*l,**kw): super().__init__(*l,**kw);  obj.oid += 1; i._id = obj.oid

the=obj(cohen=.35,bins=5)

def printd(d,pre=""):
   return pre+"{" + " ".join([f":{k} {prin(v,3)}" for k,v in d.items() if k[0] != "_"]) + "}"

def prin(x,d=None):
  return x.__name__ if callable(x) else (x if d is None or not isinstance(x,float) else round(x,d))

def per(a,p)  : return a[int(p*len(a))]
def median(a) : return per(a,.5)
def sd(a)     : return (per(a,.9) - per(a,.1))/2.56

def cuts(rows,at):
   xs   = sorted([row.cells[at] for row in rows if row.cells[at] != "?"])
   nmin = len(xs)/(the.bins - 1)
   xmin = the.cohen * sd(xs)
   lo   = xs[0]
   out  = [obj(at=at,lo=lo,hi=lo)]
   ns   = 0
   for n,x in enumerate(xs):
      if n < len(xs) - nmin and x != xs[n+1] and ns >= nmin and x-lo >= xmin:
         out += [obj(at=at,lo=hi,hi=x)]
         lo  = x
         ns  = 0
      hi  = x
      ns += 1
      out[-1].hi = x
   out[ 0].lo = -inf
   out[-1].hi = inf
   return out

R=random.random
class SOME(obj):
   def __init__(i): i.n, i.ok, i._all = 0, True, []
   def add(i,x):
      i.n += 1
      s, a = len(i._all), i._all
      if   s < the.some      : i.ok=False; a += [x]
      elif R() < the.some/i.n: i.ok=False; a[int(R()*s)] = x
   @property
   def all(i):
      if not i.ok: i._all.sort()
      i.ok = True
      return i._all

class ROW(obj):
   def __init__(i,a): use=True; i.cells = a; i.cooked=a[:]

class COL(obj):
   def __init__(i,a=[], name=" ", at=0):
      i.n, i.at, i.name = 0, at, name
      [i.add(x) for x in a]
   def add(i,x):
      if x !="?": i.n += 1; i.add1(x)
#---------------------------------------------------------------
class SYM(COL):
   def __init__(i,*l,**d): 
      i.has =  Counter()
      super().__init__(*l,**d)
   def mid(i)       : return max(i.has, key=i.has.get)
   def div(i)       : return ent(i.has)
   def dist1(i,x,y) : return 0 if x==y else 1
   def add1(i,x)    : i.has[x] += 1
   def cuts(i,_):
      if len(i.has) > 1:
        for k in i.has: yield (i.at, k, k)
   def diff(i,j,x,y):
      return False if (x=="?" or y=="?") else x!=y
#---------------------------------------------------------------
class NUM(COL):
   def __init__(i,*l,**d):
      i.mu, i.m2, i.lo, i.hi = 0,0,big,-big
      super().__init__(*l,**d)
      i.heaven = 0 if i.name[-1] == "-" else 1
   def mid(i): return i.mu
   def div(i): return (i.m2/(i.n-1))**.5
   def distance2heaven(i,row): return abs(i.heaven - i.norm(row.cells[i.at]))
   def norm(i,x): return "?" if x=="?" else (x- i.lo)/(i.hi - i.lo + 1/big)
   def diff(i,j,x,y):
      if (x=="?" or y=="?"): return False
      return  abs(x-y)/i.pooled(j) > the.Cohen
   def dist1(i,x,y):
      x,y = i.norm(x), i.norm(y)
      if x=="?": x= 0 if y > .5 else 1
      if y=="?": y= 0 if x > .5 else 1
      return abs(x - y)
   def add1(i,x):
      i.lo = min(x, i.lo)
      i.hi = max(x, i.hi)
      d    = x - i.mu
      i.mu += d/i.n
      i.m2 += d*(x - i.mu)
def COLS(a):
   all = [(NUM if s[0].isupper() else SYM)(at=n,name=s) for n,s in enumerate(a)]
   x,y = [],[]
   for col in all:
      if col.name[-1] != "X":
         (y if col.name[-1] in "+-!" else x).append(col)
   return obj(x=x, y=y, names=a, all=all)

class SHEET(obj):
   def __init__(i, src):
     i.rows, i.cols = [],  None
     [i.add(row) for row in src]

   def add(i,row):
      if i.cols:
            i.rows += [row]
            [col.add(row.cells[col.at]) for col in i.cols.all]
      else: i.cols = COLS(row.cells)

def cook(rows,cols):
  for col in cols.x:
    tmp = cuts(rows,col.at)
    for row in rows:
       if cut1 := cut(row.raw[col.at],tmp):
         row.cooked[col.at] = cut1

def ents(rows,cols):
   def counts(col):
      out = Counter()
      for row in rows:
        if row.cooked[col.at != "?"]: out[row.cooked[col.at]] += 1
      return counts
   return [ent(counts(col)) for col in cols.x]

def ent(d):
  n = sum(d.values())
  return - sum(m/n*log(m/n,2) for m in d.values() if m > 0)

def cut(x, cuts)-> tuple | None :
   for n,cut1 in enumerate(cuts):
      if true(x, cut1): return n

def true(x, cut): return x=="?" or cut.lo==cut.hi==x or x > cut.lo and x <= cut.hi

def coerce(x):
   try : return ast.literal_eval(x)
   except Exception: return x.strip()

def csv(file="-", filter=ROW):
   with  fileinput.FileInput(file) as src:
      for line in src:
         line = re.sub(r'([\n\t\r"\' ]|#.*)', '', line)
         if line: yield filter([coerce(x) for x in line.split(",")])

leventy
[print(cut) for cut in cuts([ROW([int(100*random.random()**2)]) for _ in range(1000)],0)]

