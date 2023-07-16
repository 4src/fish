#!/usr/bin/env python3 -B
#<!--- vim: set et sts=3 sw=3 ts=3 : --->
"""
uspy: a (very) little AI tool
(c) Tim Menzies <timm@ieee.org>, BSD-2 license

OPTIONS:
  -b --bins   initial number of bins     = 16
  -c --cohen  small delta = cohen*stdev  = .35
  -f --file   where to read data         = "../data/auto93.csv"
  -g --go     start up action            = "help"
  -h --help   show help                  = False
  -s --seed   random number seed         = 1234567890
  -m --min    minuimum size              = .5
  -r --rest   |rest| = |best|*rest       = 3
"""
#-------------------------------------------------------------------------------
# ## Set-up
from ast import literal_eval as lit
from copy import deepcopy
import fileinput, random, ast, sys, re
from collections import Counter, defaultdict
from fileinput import FileInput as file_or_stdin
from math import pi,log,cos,sin,sqrt,inf

# Some standard short cuts
big = 1e100
R = random.random

# `obj` are `dicts` where you can access a slot using either `d["fred"]` or `d.fred`
class obj(dict): __getattr__ = dict.get
# `the` is an `obj` of settings and defaults pulled from `__doc__` string.
the = obj(**{m[1]: lit(m[2]) for m in re.finditer( r"\n\s*-\w+\s*--(\w+).*=\s*(\S+)",__doc__)})
#-------------------------------------------------------------------------------
# ## Statistics
# Given a sorted list `a` or a dictionary `d`, what can we report?
def norm(a,x): return x if x=="?" else (x- a[0])/(a[-1] - a[0] + 1/big)
def median(a): return a[int(.5*len(a))]
def stdev(a) : return (a[int(.9*len(a))] - a[int(.1*len(a))])/ 2.56
def mode(d)  : return max(d, key=d.get)
def ent(d)   : n=sum(d.values()); return -sum((m/n * log(m/n, 2) for m in d.values() if m>0))

# Ignore columns whose names end in "X".   
# Goal columns end in some maximize/minimize symbol.    
# Numeric columns have names starting in upper case.
def isIgnored(s): return s[-1] == "X"  # ig
def isGoal(s)   : return s[-1] in "+-"
def isNum(s)    : return s[0].isupper()

# How to compute `mid` (central tendency) or `div` (divergence from central tendency)?
def mid(s,a,n=None): return rnd(median(a),n) if isNum(s) else mode(Counter(a))
def div(s,a,n=None): return rnd(stdev(a)     if isNum(s) else ent(Counter(a)),n)
#-------------------------------------------------------------------------------
# ## Store Data
# Store many `rows` and  the no "?" values in each column (in `cols`).
# Also, small detail, the first `row` is a list of column `names`.
def DATA(src):
   rows,cols = [],{}
   for n,row in enumerate(src):
      if n==0:
         names = row
         for c,_ in enumerate(names): cols[c] = []
      else:
         rows += [row]
         [cols[c].append(x) for c,x in enumerate(row) if x != "?"]
   return obj(names=names, rows=rows, cols= {c:sorted(a) for c,a in cols.items()})

# How to report stats on each column.
def stats(data, cols=None, decimals=None, fun=mid):
   cols = cols or [c for c in data.cols if isGoal(data.names[c])]
   def show(c): return fun(data.names[c], data.cols[c], decimals)
   return obj(N=len(data.rows), **{data.names[c]:show(c) for c in cols or data.cols})

# How to sort the rows closest to furthest from most desired.
def sortedRows(data):
   w = {c:(0 if s[-1]=="-" else 1) for c,s in enumerate(data.names) if isGoal(s)}
   def _distance2heaven(row):
      return sum(( (w[c] - norm(data.cols[c], row[c]))**2 for c in w ))**.5
   return sorted(data.rows, key=_distance2heaven)

# How to make a new DATA that copies the structure of an old data (and fill in with `rows`).
def clone(data,rows=[]): return DATA( [data.names] + rows)

#-------------------------------------------------------------------------------
def within(x, cut):
   _,lo,hi = cut
   return  x=="?" and True or lo==hi==x or  x > lo and x <= hi

def discretize(data, bestRows,restRows):
   "Yields cuts `((colNumber, lo1, hi1) (colNumber lo2 hi2)...)`"
   def _cut(x,cuts):
      "return the cut that contains `x`"
      if x=="?": return x
      for cut in cuts:
         if within(x,cut): return cut

   def _syms(c,a):
      "return one cut for each symbol"
      return [(c, x, x) for x in  sorted(set(a))]

   def _nums(c,a):
      "simplistic (equal frequency) unsupervised learning "
      n = inc = int(len(a)/(the.bins - 1))
      cuts, b4, small = [], a[0],  the.cohen*stdev(a)
      while n < len(a) -1 :
         x = a[n]
         if x==a[n+1] or x - b4 < small: n += 1
         else: n += inc; cuts += [(c,b4,x)]; b4=x # < , <=
      return _infinite(c,cuts)

   def _infinite(c,cuts):
      "extend `cuts` to minus/plus infinity"
      if len(cuts) < 2: return [(c, -inf, inf)] # very rare case
      cuts[ 0] = (c, -inf,       out[0][2])
      cuts[-1] = (c, out[-1][1], inf)
      return cuts

   def _counts(c,cuts):
      "count how often a cut appears in best or rest"
      xys = {cut : obj(x=cut, y=obj(best=0, rest=0)) for cut in cuts}
      for y,rows in [("best",bestRows), ("rest", restRows)]:
         for row in rows:
            x = row[c]
            if x != "?":
               xys[_cut(x,cuts)].y[y] += 1/len(rows)
      tmp = sorted(xys.values(), key=lambda xy:xy.x)
      return _merges(tmp) if isNum(data.names[c]) else tmp

   def _merges(ins):
      "Try merging any thing with its neighbor. Stop when no more merges found."
      outs, n = [], 0
      while n < len(ins):
         thing = ins[n]
         if n < len(ins)-1:
            neighbor = ins[n+1]
            if merged := _merged(thing, neighbor):
               thing = merged
               n += 1
         outs += [thing]
         n += 1
      return ins if len(ins)==len(outs) else _merges(outs)

   def _merged(a,b):
      "return a combined xy, but only if the combo is not more complex than that parts"
      c = obj(x= (a.x[0], a.x[1], b.x[2]),
              y= obj(best= a.y.best + b.y.best,
                     rest= a.y.rest + b.y.rest))
      n1 = a.y.best + a.y.rest + 1/big
      n2 = b.y.best + b.y.rest + 1/big
      if ent(c.y) <= (ent(a.y)*n1 + ent(b.y)*n2) / (n1+n2):
         return c

   for c,name in enumerate(data.names):
      if not isGoal(name) and not isIgnored(name):
         cuts = (_nums if isNum(name) else _syms)(c,data.cols[c])
         for cut in _counts(c, cuts):
            yield cut
#---------------------------------------------
def score(b, r):
  "Given you've found `b` or `r` items of `B,R`, how much do we like you?"
  r += 1/big # stop divide by zero errors
  match the.want:
    case "plan"    : return b**2 / (   b + r)    # seeking best
    case "monitor" : return r**2 / (   b + r)    # seeking rest
    case "doubt"   : return (b+r) / abs(b - r)   # seeking border of best/rest 
    case "xplore"  : return 1 / (   b + r)       # seeking other

#---------------------------------------------
def rnd(x,decimals=None):
   return round(x,decimals) if decimals != None  else x

def coerce(x):
   try : return lit(x)
   except Exception: return x.strip()

def csv(file="-"):
   with file_or_stdin(file) as src:
      for line in src:
         line = re.sub(r'([\n\t\r"\' ]|#.*)', '', line)
         if line:
            yield [coerce(x) for x in line.split(",")]

def prints(*dists):
   print(*dists[0].keys(), sep="\t")
   [print(*d.values(), sep="\t") for d in dists]

def cli2dict(d):
   for k, v in d.items():
      s = str(v)
      for j, x in enumerate(sys.argv):
         if ("-"+k[0]) == x or ("--"+k) == x:
            d[k] = coerce("True" if s == "False" else ("False" if s == "True" else sys.argv[j+1]))

#---------------------------------------------
# ## Start-up Actions

# Before eacha ction, reset the random num 
class GO:
   Saved = deepcopy(the)
   All = locals()
   def Now(a=sys.argv): 
      cli2dict(the)
      if the.help: sys.exit(GO.help())
      GO.Run( GO.All.get(the.go, GO.help))

   def Run(fun):
      global the
      random.seed(the.seed)
      failed = fun()==False
      print("❌ FAIL" if failed else "✅ OK", fun.__name__)
      the = deepcopy(GO.Saved)
      return failed

   def all():
      "run all actions, return to operating system a count of the number of failures"
      sys.exit(sum(map(GO.Run,[fun for s,fun in GO.All.items() if s != "all" and s[0].islower()])))

   def help():
       "show help"
       print(__doc__); print("ACTIONS:")
       [print(f"  -g {x:8} {f.__doc__}")
       for x,f in GO.All.items() if x[0].islower()]

   def the():
      "show config"
      print(the)

   def nums():
      "can we find mean and sd of N(10,1)?"
      g= lambda mu,sd: mu+sd*sqrt(-2*log(R())) * cos(2*pi*R())
      a= sorted([g(10,1) for x in range(1000)])
      print(median(a),stdev(a))

   def read():
      "can we print rows from a disk-based csv file?"
      [print(*row,sep=",\t") for r,row in enumerate(csv(the.file)) if r < 10]

   def data():
      "can we load disk rows into a DATA?"
      data1 = DATA(csv(the.file))
      prints(stats(data1))

   def sorted():
      "can we find best, rest rows?"
      data1= DATA(csv(the.file))
      rows = sortedRows(data1)
      n    = int(len(rows)**the.min)
      prints(stats(data1),
             stats(clone(data1, rows[:n])),
             stats(clone(data1, rows[-n*the.rest:])))

   def discret():
      "can i do supervised discretization?"
      data1 = DATA(csv(the.file))
      rows  = sortedRows(data1)
      n     = int(len(rows)**the.min)
      bests,rests = rows[:n], rows[-n*the.rest:]
      discretize(data1, bests,rests)
      for c,a in data1.cuts.items():
         lst = data1.cols[c]
         print(f"{c:2} {lst[0]:8} {lst[-1]:8}",
               [xy.x[1] for xy in a]+([big] if isNum(data1.names[c]) else []))

if __name__ == "__main__": GO.Now()

# data = discretize(data)
# tmp = sortedRows(data)
# print(*data.names,sep="\t")
