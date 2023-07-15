#!/usr/bin/env python3 -B
# <!--- vim: set et sts=3 sw=3 ts=3 : --->
"""
S.PY: a little AI
(c) Tim Menzies <timm@ieee.org>, BSD-2 license
"""
import fileinput, random, ast, sys, re
from collections import Counter, defaultdict
from fileinput import FileInput as file_or_stdin
from math import pi,log,cos,sin,inf,sqrt

R = random.random
class obj(dict): __getattr__ = dict.get

the=obj(file="../data/auto93.csv", bins=5, cohen=.35, min=.5, rest=3)
#-------------------------------------------------------------------------------
def norm(a,x): return x if x=="?" else (x- a[0])/(a[-1] - a[0] + 1/inf)
def median(a): return a[int(.5*len(a))]
def stdev(a) : return (a[int(.9*len(a))] - a[int(.1*len(a))])/ 2.56
def mode(d)  : return max(d, key=d.get)
def ent(d)   : n=sum(d.values()); return -sum((m/n * log(m/n, 2) for m in d.values() if m>0))

def isGoal(s): return s[-1] in "+-"
def isNum(s) : return s[0].isupper()

def mid(s,a,ndecimals=None): return rnd(median(a),ndecimals) if isNum(s) else mode(Counter(a))
def div(s,a,ndecimals=None): return rnd(stdev(a) if isNum(s) else ent(Counter(a)), ndecimals)
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
   return obj(names=names, rows=rows, cuts={}, cols={c:sorted(cols[c]) for c in cols})

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
def discretize(data, bestRows,restRows):
   def _cut(x,cuts):
      "return the cut that contains `x`"
      if x=="?": return x
      for n,v in enumerate(cuts):
         if x < v: return n/(len(cuts)-1)

   def _cuts(a):
      n = inc = int(len(a)/the.bins)
      b4, small = a[0],  the.cohen*stdev(a)
      out = []
      while n < len(a) -1 :
         x = a[n]
         if x==a[n+1] or x - b4 < small: n += 1
         else: n += inc; out += [x]; b4=x
      out += [inf]
      return out

   def _num(c):
      out, tmp = {}, _cuts(data.cols[c])
      for y,rows in [("best",bestRows), ("rest", restRows)]:
         for row in rows:
            x=row.cells[c]
            if x != "?":
               k = _cut(x, tmp)
               z = out[k] = out.get(k,None) or obj(lo=x,hi=x,n=obj(best=0, rest=0))
               z.lo = min(z.lo, x)
               z.hi = max(z.hi, x)
               z.n[y] += 1
      return [z.lo for z in _merges(sorted(out.values(), key=lambda z:z.lo))] + [inf]

   def _merged(z1,z2):
      z3 = obj(lo=z1.lo, hi=z2.hi, n=obj(best= z1.n.best + z2.n.best,
                                         rest= z1.n.rest + z2.n.rest))
      n1,n2 = z1.n.best + z1.n.rest, z2.n.best + z2.n.rest
      if ent(z3.n) <= (ent(z1.n)*n1 + ent(z2.n)*n2) / (n1+n2):
         return z3

   def _merges(ins):
      outs, n = [], 0
      while n < len(ins):
         one = ins[n]
         if n < len(ins)-1:
            if merged := _merged(one, ins[n+1]):
               one = merged
               n += 1
         outs += [one]
         n += 1
      return ins if len(ins)==len(outs) else _merges(outs)

   def _expand(c,a):
      b4,tmp = -inf,[]
      for x in a: tmp += [(c, b4,x)]; b4 = x
      return tuple(tmp)

   for c,name in enumerate(data.names):
      if not isGoal(name):
         data.cuts[c] = _expand(c, _num(c) if isNum(name) else sorted(set(data.cols[c])))
   return data

#---------------------------------------------
def rnd(x,decimals=None):
   return round(x,decimals) if decimals != None  else x

def coerce(x):
   try : return ast.literal_eval(x)
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

#---------------------------------------------
class EG:
   """asdas asd asdas da sddas d adasasd
     asdasadsdsa"""
   ALL = locals()
   def RUN(a=sys.argv): a[1:] and EG.ALL.get(a[1][2:],EG.HELP)()
   def HELP():
       print(__doc__); print("./s.py")
       [print(f"  --{x:10} : {f.__doc__}")
       for x,f in EG.ALL.items() if x[0].islower()]
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
         print(c,a)

EG.RUN()

# data = discretize(data)
# tmp = sortedRows(data)
# print(*data.names,sep="\t")
# [print(*row.cells,sep="\t") for row in tmp[:10]]; print("")
# [print(*row.cells,sep="\t") for row in tmp[-10:]]
