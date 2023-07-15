#!/usr/bin/env python3 -B
# <!--- vim: set et sts=3 sw=3 ts=3 : --->
"""
uspy: a little AI tool
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
from ast import literal_eval as lit
from copy import deepcopy
import fileinput, random, ast, sys, re
from collections import Counter, defaultdict
from fileinput import FileInput as file_or_stdin
from math import pi,log,cos,sin,inf,sqrt

R = random.random
class obj(dict): __getattr__ = dict.get
the = obj(**{m[1]: lit(m[2]) for m in re.finditer( r"\n\s*-\w+\s*--(\w+).*=\s*(\S+)",__doc__)})
#-------------------------------------------------------------------------------
def norm(a,x): return x if x=="?" else (x- a[0])/(a[-1] - a[0] + 1/inf)
def median(a): return a[int(.5*len(a))]
def stdev(a) : return (a[int(.9*len(a))] - a[int(.1*len(a))])/ 2.56
def mode(d)  : return max(d, key=d.get)
def ent(d)   : n=sum(d.values()); return -sum((m/n * log(m/n, 2) for m in d.values() if m>0))

def isIgnored(s): return s[-1] == "X"
def isGoal(s)   : return s[-1] in "+-"
def isNum(s)    : return s[0].isupper()

def mid(s,a,n=None): return rnd(median(a),n) if isNum(s) else mode(Counter(a))
def div(s,a,n=None): return rnd(stdev(a)     if isNum(s) else ent(Counter(a)),n)
#-------------------------------------------------------------------------------
def ROW(a): return obj(cells=a, cooked=a[:])

def DATA(src):
   rows,cols = [],None
   for row in src:
      if cols:
         [cols[c].append(x) for c,x in enumerate(row.cells) if x != "?"]
         rows += [row]
      else:
         names= row.cells
         cols = {c:[] for c,_ in enumerate(names)}
   [cols[c].sort() for c in cols]
   return obj(names=names, rows=rows, cuts={}, cols=cols)

def clone(data,rows=[]): return DATA( [ROW(data.names)] + rows)

def sortedRows(data):
   w = {c:(0 if s[-1]=="-" else 1) for c,s in enumerate(data.names) if isGoal(s)}
   def _distance2heaven(row):
      return sum(( (w[c] - norm(data.cols[c], row.cells[c]))**2 for c in w ))**.5
   return sorted(data.rows, key=_distance2heaven)

def stats(data, cols=None, decimals=None, fun=mid):
   cols = cols or [c for c in data.cols if isGoal(data.names[c])]
   def show(c): return fun(data.names[c], data.cols[c], decimals)
   return obj(N=len(data.rows), **{data.names[c]:show(c) for c in cols or data.cols})
#-------------------------------------------------------------------------------
def within(x, cut):
   return x > cut[1] and x <= cut[2]

def discretize(data, bestRows,restRows):
   def _cut(x,cuts):
      "return the cut that contains `x`"
      if x=="?": return x
      for cut in cuts:
         if within(x,cut): return cut

   def _syms(c,a):
      "return one cut for each symbol"
      return [(c, x, x) for x in  sorted(set(a))]

   def _nums(c,a):
      "Return the.bins cuts, merging any with similar class distribution"
      n = inc = int(len(a)/(the.bins - 1))
      b4, small = a[0],  the.cohen*stdev(a)
      out = []
      while n < len(a) -1 :
         x = a[n]
         if x==a[n+1] or x - b4 < small: n += 1
         else: n += inc; out += [(c,b4,x)]; b4=x # < , <=
      out[ 0]  = (out[ 0][0], -inf,       out[0][2])
      out[-1]  = (out[-1][0], out[-1][1], inf)
      return out

   def _counts(c,cuts):
      "count how often a cut appears in best or rest"
      xys = {cut[0] : obj(x=cut, y=obj(best=0, rest=0)) for cut in cuts}
      for y,rows in [("best",bestRows), ("rest", restRows)]:
         for row in rows:
            x = row.cells[c]
            if x != "?":
               xys[_cuts(x,cuts)].y[y] += 1
      tmp = sorted(xys.values(), key=lambda xy:xy.x[0])
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

   def _merged(xy1,xy2):
      "return a combined xy, but only if the combo is not more complex than that parts"
      xy3 = obj(x=(xy1.x[0], xy1.x[1], xy2, xy[3]),
                y=obj(best= xy1.y.best + xy2.y.best,
                      rest= xy1.y.rest + xy2.y.rest))
      n1,n2 = xy1.y.best + xy1.y.rest, xy2.y.best + xy2.y.rest
      if ent(xy3.y) <= (ent(xy1.y)*n1 + ent(xy2.y)*n2) / (n1+n2):
         return xy3

   for c,name in enumerate(data.names):
      if not isGoal(name) and not isIgnored(name):
         data.cuts[c] = _counts(c, (_nums if isNum(name) else _syms)(c,data,cols[c]))
   return data

#---------------------------------------------
def rnd(x,decimals=None):
   return round(x,decimals) if decimals != None  else x

def coerce(x):
   try : return lit(x)
   except : return x.strip()

def csv(file="-", filter=ROW):
   with file_or_stdin(file) as src:
      for line in src:
         line = re.sub(r'([\n\t\r"\' ]|#.*)', '', line)
         if line:
            yield filter([coerce(x) for x in line.split(",")])

def prints(*dists):
   print(*dists[0].keys(), sep="\t")
   [print(*d.values(), sep="\t") for d in dists]

def updateFromCLI(d):
   for k, v in d.items():
      s = str(v)
      for j, x in enumerate(sys.argv):
         if ("-"+k[0]) == x or ("--"+k) == x:
            d[k] = coerce("True" if s == "False" else ("False" if s == "True" else sys.argv[j+1]))

#---------------------------------------------
class GO:
   All = locals()
   def Now(a=sys.argv): 
      updateFromCLI(the)
      if the.help: sys.exit(GO.help())
      GO.Run( GO.All.get(the.go, GO.help))

   def Run(fun):
      global the
      saved = deepcopy(the)
      random.seed(the.seed)
      failed = fun()==False
      print("❌ FAIL" if failed else "✅ OK", fun.__name__)
      the = deepcopy(saved)
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
      [print(row.cells) for row in csv(the.file)]

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
         print(f"{c:2} {lst[0]:8} {lst[-1]:8}",a)

GO.Now()

# data = discretize(data)
# tmp = sortedRows(data)
# print(*data.names,sep="\t")
# [print(*row.cells,sep="\t") for row in tmp[:10]]; print("")
# [print(*row.cells,sep="\t") for row in tmp[-10:]]