#!/usr/bin/env python3 -B
# <!--- vim: set et sts=3 sw=3 ts=3 : --->
# <img src="sample.jpg" width=400>
"""
samplr: a little smart sampling goes a long way
(multi- objective, semi- supervised, rule-based explanations)
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
from ast import literal_eval as lit
from copy import deepcopy
import fileinput, random, ast, sys, re
from collections import Counter, defaultdict
from fileinput import FileInput as file_or_stdin
from termcolor import colored
from math import pi,log,cos,sin,sqrt,inf
#-------------------------------------------------------------------------------
# ## Base classes (and settings)
class pretty(object):
   def __repr__(i):
      slots = [f":{k} {rnd(v)}" for k,v in i.__dict__.items() if k[0] != "-"]
      return i.__class__.__name__ + "{" + (" ".join(slots)) + "}"

# `the` is an `obj` of settings and defaults pulled from `__doc__` string.
class slots(dict): __getattr__ = dict.get # allows easy slot access (`e.g. d.fred, not d["fred"])
the = slots(**{m[1]: lit(m[2]) for m in re.finditer( r"\n\s*-\w+\s*--(\w+).*=\s*(\S+)",__doc__)})
#-------------------------------------------------------------------------------
# ## Stats

# Given a sorted list of numbers `a` or a dictionary `d` containing frequency counts
# for each key, what can we report?  
def per(a,n=.5):  return a[int(n*len(a))]
def median(nums): return per(nums, .5) # middle number
def stdev(nums):  return (per(nums,.9) - per(nums,.1))/ 2.56 # div=diversity
def mode(d):      return max(d, key=d.get) # most frequent number
def entropy(d):   # measures diversity for symbolic distributions
   n = sum(d.values())
   return -sum((m/n * log(m/n,2) for m in d.values() if m>0))

# ### Conventions for column names
ako = slots(num  = lambda s: s[0].isupper(),
            goal = lambda s: s[-1] in "+-",
            skip = lambda s: s[-1] == "X",
            xnum = lambda s: not ako.goal(s) and ako.num(s),
            xsym = lambda s: not ako.goal(s) and not ako.num(s))
#-------------------------------------------------------------------------------
# ## Columns

# ### Summarize SYMs
class SYM(pretty):
   def __init__(i,a,at=0,name=" "):
      d = Counter(a)
      i.at, i.name = at, name
      i.mid, i.div = mode(d), entropy(d)
      i.cuts = [(at,x,x) for x in sorted(set(d))]

# ### Summarize NUMs
class NUM(pretty):
   def __init__(i,a,at=0,name=" "):
      a = sorted(a)
      i.at, i.name = at, name
      i.mid, i.div = median(a), stdev(a)
      i.lo, i.hi, i.heaven = a[0], a[-1], 0 if name[-1] == "-" else 1
      i.cuts = i._unsuper(at,a)

   def norm(i,x):
      "map `x` 0..1 for `lo..hi`"
      return x if x=="?" else (x- i.lo)/(i.hi - i.lo + 1/big)

   def _unsuper(i,at,a):
      "simplistic (equal frequency) unsupervised discretization"
      n = inc = int(len(a)/(the.bins - 1))
      cuts, b4, small = [], a[0], the.cohen*i.div
      while n < len(a) -1 :
         x = a[n]
         if x==a[n+1] or x - b4 < small: n += 1
         else:
            n += inc
            cuts += [(at,b4,x)] # [(col, lo, hi)]
            b4 = x
      if len(cuts) < 2: return [(at, -inf, inf)] # ensure cuts run -inf to inf
      cuts[ 0] = (at, -inf,        cuts[0][2])
      cuts[-1] = (at, cuts[-1][1], inf)
      return cuts
#---------------------------------------------------------------------------------------------------
# ## Data
# Store many `rows` and  the no "?" values in each column (in `cols`).
# Also, small detail, the first `row` is a list of column `names`.
class DATA(pretty):
   def __init__(i, src):
      "src is a list of list, or an iterator that returns froms from files"
      for n,row in enumerate(src):
         if n==0:
            i.rows, i.names, cache = [], row, [[] for _ in row]
         else:
            i.rows += [row]
            [a.append(x) for a,x in zip(cache,row) if x != "?"]
      i.cols = slots(all = [(NUM if ako.num(name) else SYM)(a, at, name)
                          for at,(name,a) in enumerate(zip(i.names,cache))])
      for k,fun in ako.items():
         i.cols[k] = [c for c in i.cols.all if not ako.skip(c.name) and fun(c.name)]

   def stats(i, cols="goal", decimals=None, want="mid"):
      "How to report stats on each column."
      return slots(N=len(i.rows), **{c.name:rnd(c.__dict__[want],decimals) for c in i.cols[cols]})

   def sortedRows(i, cols="goal"):
      "How to sort the rows closest to furthest from most desired"
      def _distance2heaven(row):
         return sum(( (col.heaven - col.norm(row[col.at]))**2 for col in i.cols[cols] ))**.5
      return sorted(i.rows, key=_distance2heaven)

# How to make a new DATA that copies the structure of an old data (and fill in with `rows`).
def clone(data,rows=[]): return DATA( [data.names] + rows)
#-------------------------------------------------------------------------------
# ## Discretization

# A cut is a 3-part tuple `(columIndex, lo, hi)`
def withins(x, cuts):
   for cut in cuts:
      if within(x,cut): return cut

def within(x, cut):
   _,lo,hi = cut
   return  x=="?" or lo==hi==x or  x > lo and x <= hi

# Gen0 contains ranges to be used in the rule generation.
# It looks for ways to combine `col.cuts` and reports 
# `slots(x=(columnIndex,lo, hi) y=Counter(labelCounts))`
# showing frequency counts of these ranges amongst these `labelledRows`.
# (and this  is a set of pairs `[(label1,rows1),(label2,rows2)...]`).
def gen0(data, labelledRows):
   def _counts(col, cuts, labelledRows):
      "count how often `cut` (in `cuts`) appears among the different labels?"
      counts = {cut : slots(x=cut, y=Counter()) for cut in cuts}
      for label,rows in labelledRows:
         for row in rows:
            x = row[col.at]
            if x != "?":
               counts[ withins(x,cuts) ].y[ label ] += 1/len(rows)
      return sorted(counts.values(), key=lambda z:z.x)

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
      ab = slots(x= (a.x[0], a.x[1], b.x[2]), y= a.y + b.y)
      n1 = a.y.total() + 1/big
      n2 = b.y.total() + 1/big
      if entropy(ab.y) <=  (entropy(a.y)*n1 + entropy(b.y)*n2) / (n1+n2):
         return ab

   for col in data.cols.xsym:
      if len(col.cuts) > 1:
         for cut in _counts(col, col.cuts, labelledRows):
            yield cut
   for col in data.cols.xnum:
      for cut in  _merges( _counts(col, col.cuts, labelledRows)):
         if not (cut.x[1] == -inf and cut.x[2] == inf): # ignore it if it spans whole range
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
   rows  = data.sortedRows()
   n     = int(len(rows)**the.min)
   bests,rests  = rows[:n], rows[-n*the.rest:]
   labelledRows = [("best",bests), ("rests",rests)]
   for (s,x) in sorted([(score(cut.y["best"], cut.y["rest"]),cut) for cut in
                        gen0(data,labelledRows)], reverse=True,
                        key=lambda z:z[0]):
      yield s,x.x

def threes2Rule(threes):
   #( ((1 4 5) (1 5 8))
   #  ((2 10 30))
   #  ((3 2 10) (3 10 12)))
   d={}
   for x in threes:
      print(x)
      at,lo,hi = x
      d[at]  = d.get(at,[])
      d[at] += [(at,lo,hi)]
   return tuple(sorted([tuple(sorted(d[k])) for k in d]))

def rule2Threes(rules):
   return [three for  threes in rule for three in threes]
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

# Some standard short cuts
big = 1e100
R = random.random

# If decimals offered, then round to that. else just return `x`
def rnd(x,decimals=None): 
  if decimals is None or not instance(x,float): return x
  return round(x,decimals)

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
      a= NUM([g(10,1) for x in range(1000)])
      print(a.mid,a.div,a.cuts)

   def read():
      "can we print rows from a disk-based csv file?"
      [print(*row,sep=",\t") for r,row in enumerate(csv(the.file)) if r < 10]

   def data():
      "can we load disk rows into a DATA?"
      data = DATA(csv(the.file))
      prints(data.stats())

   def sorted():
      "can we find best, rest rows?"
      data= DATA(csv(the.file))
      rows = data.sortedRows()
      n    = int(len(rows)**the.min)
      prints(data.stats(),
             clone(data, rows[:n]).stats(),
             clone(data, rows[-n*the.rest:]).stats())

   def discret():
      "can i do supervised discretization?"
      for s,x in scores(DATA(csv(the.file))):
         print(f"{s:.3f}\t{x}")

   def rules():
      "can i do supervised discretization?"
      threes = [rule for s,rule in scores(DATA(csv(the.file)))]
      rule = threes2Rule(threes)
      print(  rule2Threes(rule))

if __name__ == "__main__": go._on()
