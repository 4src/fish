#!/usr/bin/env python3 -B
#<!--- vim: set et sts=3 sw=3 ts=3 : --->
"""
samplr: a little smart sampling goes a long way
(multi- objective, semi- supervised, explanations)
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
  -w --want   plan|xplore|monitor|doubt  = "plan"
"""
#-------------------------------------------------------------------------------
# ## Set-up
from ast import literal_eval as lit
from copy import deepcopy
import fileinput, random, ast, sys, re
from collections import Counter, defaultdict
from fileinput import FileInput as file_or_stdin
from termcolor import colored
from math import pi,log,cos,sin,sqrt,inf

# Some standard short cuts
big = 1e100
R = random.random

# `obj` are `dicts` where you can access a slot using either `d["fred"]` or `d.fred`
class obj(dict): __getattr__ = dict.get
# `the` is an `obj` of settings and defaults pulled from `__doc__` string.
the = obj(**{m[1]: lit(m[2]) for m in re.finditer( r"\n\s*-\w+\s*--(\w+).*=\s*(\S+)",__doc__)})
#-------------------------------------------------------------------------------
# ## Stats

# ### Dict,Lists to Stats
# Given a sorted list of numbers `a` or a dictionary `d` containing frequency counts
# for each key, what can we report?  
def per(a,n):     return a[int(n*len(a))]
def median(nums): return per(nums, .5) # middle number
def stdev(nums):  return (per(nums,.9) - per(nums,.1))/ 2.56 # div=diversity
def mode(d):      return max(d, key=d.get) # most frequent number
def ent(d):       # entropy
   n=sum(d.values())
   return -sum((m/n * log(m/n,2) for m in d.values() if m>0))

# ### Conventions for column names
def nump(s):  return s[0].isupper() # nums have upper case
def goalp(s): return s[-1] in "+-" # goals in "+-"
def skipp(s): return s[-1] == "X"  #  skip anything ending with "X"
def xnump(s): return not goalp(s) and nump(s)
def xsymp(s): return not goalp(s) and not nump(s)

# Given those conventions, how to compute `mid` (central tendency) 
# or `div` (divergence from central tendency)? If `n` is non-nil,
# round `median`s,`stdev`,`ent`  to `n` decimal places (and leave `mode` unrounded)
def mid(s,x,n=None): return rnd(median(x),n) if nump(s) else mode(Counter(x))
def div(s,x,n=None): return rnd(stdev(x)     if nump(s) else ent(Counter(x)),n)

# If decimals offered, then round to that. else just return `x`
def rnd(x,decimals=None): return round(x,decimals) if decimals != None  else x
#-------------------------------------------------------------------------------
# ## Data
# Store many `rows` and  the no "?" values in each column (in `cols`).
# Also, small detail, the first `row` is a list of column `names`.
def DATA(src): 
   "rc is a list of list, or an iterator that returns froms from files"
   def _just(names,fun=lambda _:True):
      "returns a function that can interate over certain kinds of columns"
      some = [col for col,name in enumerate(names) if not skipp(name) and fun(name)]
      def iterator(row=names):
         for c in some:
            x = row[c]
            if not(isinstance(x,str) and s== "?"):  yield c,x
      return iterator

   def _unsuper(a, div):
      "simplistic (equal frequency) unsupervised discretization"
      n = inc = int(len(a)/(the.bins - 1))
      cuts, b4, small = [], a[0],  the.cohen*div
      while n < len(a) -1 :
         x = a[n]
         if x==a[n+1] or x - b4 < small:
            n += 1
         else:
            n += inc
            cuts += [(c,b4,x)]
            b4 = x # < , <=
      return cuts

   def _stretch(cuts):
      if len(cuts) < 2: return [(c, -inf, inf)] # happen when all nums are the same
      cuts[ 0] = (c, -inf,        cuts[0][2])
      cuts[-1] = (c, cuts[-1][1], inf)
      return cuts

   def _summarize(name, c,a)
      if nump(name):
         a=sorted(a)
         return obj(name=name, mid=median(a), div=stdev(a), cuts=_stretch(_unsuper(c, stdev(a))),
                    lo=a[0], hi=a[-1], heaven= 0 if name[-1]=="-" else 1)
      else:
         d=Counter(a)
         return obj(name=name, mid=mode(d), div=ent(d), cuts=[(c,x,x) for x in sorted(set(a))])

   rows,tmp = [],{}
   for n,row in enumerate(src):
      if n==0:
         names = row
         tmp   = {c:[] for c,_ in enumerate(names)}
      else:
         rows += [row]
         [tmp[c].append(x) for c,x in enumerate(row) if x != "?"]
   return obj(rows=rows, just=justs, names=names,
              justs = obj( **{f.__name__:just(names,f) for f in [goalp,xnump,xsymp]}),
              cols  = {c:summarize(names[c],c,a) for c,a in tmp.items()})

   # How to report stats on each column.
def stats(data, just="goalp", n=None what="mid")
   def show(col,x): rnd(x,n) if (nump(col.name) or what="div") else x
   return obj(N=len(data.rows),
              **{col.name:show(col,col[what]) for _,col in data.just[just](data.cols)})

# How to sort the rows closest to furthest from most desired.
def sortedRows(data):
   def _distance2heaven(row):
      return sum(( (col.heaven - norm(col, row[c]))**2 for c,col in data.just.goalp(data.cols) ))**.5
   return sorted(data.rows, key=_distance2heaven)

def norm(col,x): return x if x=="?" else (x- col.lo)/(col.hi - col.lo + 1/big) # normalize

# How to make a new DATA that copies the structure of an old data (and fill in with `rows`).
def clone(data,rows=[]): return DATA( [data.names] + rows)

#-------------------------------------------------------------------------------
# ## Discretization

# A cut is a 3-part tuple `(columIndex, lo, hi)`
def within(x, cut):
   _,lo,hi = cut
   return  x=="?" and True or lo==hi==x or  x > lo and x <= hi

# Cuts are generated by our discretizer. For syms, we return one cut per key.
# For nums, an unsupervised descretizer sorts the nums then divides them into
# `the.bins` cuts. A supervised algorithm then counts how often those cuts
# appear in `bestRows` and `restRows` (and adjacent cuts with similar counts are merged).
# sorts nums, then breaks them. <p>This function yields items of the form   
# `obj(x=(columnIndex,lo, hi) y=obj(best=bests, rest=rests))`   
# where `y` reports how often we see `x` in `best` and `rest`.
def xys(data, bestRows,restRows):
   def _counts(c,cuts, finalFun= lambda x:x):
      "count how often  `cut` (in `cuts`) appears in `bestRows` or `restRows`"
      counts = {cut : obj(x=cut, y=obj(best=0, rest=0)) for cut in cuts}
      for y,rows in [("best",bestRows), ("rest", restRows)]:
         for row in rows:
             x = row[c]
             if x != "?":
                for cut in cuts:
                   if within(x,cut): break  # at the break, "cut" is the one we want.
                counts[cut].y[y] += 1/len(rows)
      return finalFun( sorted(counts.values(), key=lambda z:z.x))

   def _merges(ins):
      "Try merging any thing with its neighbor. Stop when no more merges found."
      outs, n = [], 0
      while n < len(ins):
         thing = ins[n]
         if n < len(ins)-1:
            neighbor = ins[n+1]
            if merged := _merge(thing, neighbor):
               thing = merged # switch to "merged" 
               n += 1  # skip over the thing we "merged" with
         outs += [thing] 
         n += 1
      return ins if len(ins)==len(outs) else _merges(outs)

   def _merge(a,b):
      "combines a,b (and returns None if the whole is more complex than that parts)"
      ab = obj(x= (a.x[0], a.x[1], b.x[2]), y= obj(best= a.y.best + b.y.best,
                                                   rest= a.y.rest + b.y.rest))
      n1 = a.y.best + a.y.rest + 1/big
      n2 = b.y.best + b.y.rest + 1/big
      if ent(ab.y) <= (ent(a.y)*n1 + ent(b.y)*n2) / (n1+n2):
         return ab

   for c,col in data.just.xnump(data.cols):
      for cut in  _counts(c, col.cuts,  _merges):
         if not (cut.x[1] == -inf and cut.x[2] == inf): # ignore it if it spans whole range
            yield cut
   for c,col in data.just.xsymp(data.cols):
      if len(cuts) > 1:
         for cut in _counts(c, col.cuts):
            yield cut
#---------------------------------------------
def score(b, r):
  "Given you've found `b` or `r`, how much do we like you?"
  r += 1/big # stop divide by zero errors
  match the.want:
    case "plan"    : return b**2  /    (b + r)  # seeking best
    case "monitor" : print(1); return r**2  /    (b + r)  # seeking rest
    case "doubt"   : return (b+r) / abs(b - r)  # seeking border of best/rest 
    case "xplore"  : print(2); return 1     /    (b + r)  # seeking other

def scores(data):
   rows  = sortedRows(data)
   n     = int(len(rows)**the.min)
   bests,rests = rows[:n], rows[-n*the.rest:]
   for (s,x) in sorted([(score(cut.y.best, cut.y.rest),cut) for cut in
                        discretize(data,bests,rests)], reverse=True,
                        key=lambda z:z[0]):
      yield s,x.x
#---------------------------------------------
def pick(pairs,n):
   r = R()
   for s,x in pairs:
      r -= s/n
      if r <=0: yield x

def grow(bestRows, restRows, a=[], scores={}, top=None):
   top = top or the.rules*the.gens
   a = set(a) # no repeats
   for x in a:
      if x not in scores: scores[x] = score(*selects(x,bestRows,restRows))
   a.sort(reversed=True, key=lambda x:scores[x])
   a = a[:top]
   if len(a) < the.rules: return {x:scores[x] for x in a}
   n = sum((x[0] for x in a))
   picks = [combine(pick(a,n), pick(a,n)) for _ in range(the.grows)]
   grow(bestRows, restRows, a+picks, scores,top//2)

# def select(data,ranges,row):
#   def _ors(chops,vals):
#     for val in vals:
#       if  within(row.cooked[col],*chops[val]): return True
#   for col,vals in ranges:
#     if not _ors(data.cols.all[col].chops, vals): return False
#   return True
#
# def selects(data,ranges,rows):
#   return [row for row in rows if select(data,ranges,row)]
#
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
class go:
   _saved = deepcopy(the)
   _all = locals()
   def _on(a=sys.argv): 
      cli2dict(the)
      if the.help: sys.exit(go.help())
      go._run( go._all.get(the.go, go.help))

   def _run(fun):
      global the
      random.seed(the.seed)
      failed = fun() is False
      print("❌ FAIL" if failed else "✅ OK", fun.__name__)
      the = deepcopy(go._saved)
      return failed

   def all():
      "run all actions, return number of failures"
      sys.exit(sum(map(go._run,[fun for s,fun in go._all.items() if s != "all" and s[0].islower()])))

   def help():
       "show help"
       def yell(s) : return colored(s[1], "yellow",attrs=["bold"])
       def bold(s) : return colored(s[1], "white", attrs=["bold"])
       def show(s) : return re.sub(r"(\n[A-Z]+:)", yell, re.sub(r"(-[-]?[\w]+)", bold, s))
       print(show(__doc__ + "\nACTIONS:"))
       [print(show(f"  -g {x:8} {f.__doc__}")) for x,f in go._all.items() if x[0].islower()]

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
      for s,x in scores(DATA(csv(the.file))):
         print(f"{s:.3f}\t{x}")

if __name__ == "__main__": go._on()

# data = discretize(data)
# tmp = sortedRows(data)
# print(*data.names,sep="\t")
