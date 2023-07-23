#!/usr/bin/env python3 -B
# <!--- vim: set et sts=3 sw=3 ts=3 : --->
# [src](https://github.com/4src/fish/blob/main/cutr.py)
# &sol; [cite](https://github.com/4src/fish/blob/main/CITATION.cff)
# &sol; [issues](https://github.com/4src/fish/issues)
# &sol; [&copy;2023](https://github.com/4src/fish/blob/main/LICENSE.md)
# by [timm](mailto:timm@ieee.org)
#
# <img  src="sample3.png"   width=450>
"""
cutr: to understand "it",  cut "it" up, then seek patterns in the pieces. E.g. here
we use cuts for multi- objective, semi- supervised, rule-based explanation.
(c) Tim Menzies <timm@ieee.org>, BSD-2 license

OPTIONS:
  -b --bins   initial number of bins      = 16
  -B --Bootstraps number of bootstraps    = 512
  -c --cohen  parametric small delta      = .35
  -C --Cliffs  non-parametric small delta = 0.2385 
  -f --file   where to read data          = "../data/auto93.csv"
  -g --go     start up action             = "help"
  -h --help   show help                   = False
  -s --seed   random number seed         = 1234567891
  -m --min    minuimum size              = .5
  -r --rest   |rest| = |best|*rest       = 3
  -T --Top    max. good cuts to explore   = 10
  -w --want   plan|xplore|monitor|doubt  = "plan"
"""
from collections import Counter, defaultdict
from math import pi, log, cos, sin, sqrt, inf
import fileinput, random, time, copy, ast, sys, re
from termcolor import colored

def coerce(x):
   try : return ast.literal_eval(x)
   except Exception: return x.strip()

# In this code, global settings are kept in `the` (which is parsed from `__doc__`).
# This variable is a `slots`, which is a neat way to represent dictionaries that
# allows easy slot access (e.g. `d.bins` instead of `d["bins"]`)
class slots(dict): __getattr__ = dict.get 
the = slots(**{m[1]:coerce(m[2]) for m in re.finditer( r"\n\s*-\w+\s*--(\w+).*=\s*(\S+)",__doc__)})
#-------------------------------------------------------------------------------
# ## What is a "cut"?
# This code finds `cuts`, then uses those `cuts` to explore data.
# A `cut` is a tuple `(col, lo, hi)` which represents a constraint on
# column `col` (and if `lo==hi` then this is a symbolic column). `Cuts`
# are generated initially by a simplistic algorithm (one `cut` for each symbolic
# column while numerics are divided into equal frequency bins). Then we try
# combining `cut`s;  e.g. for numerics, does it make sense to merge it with its
# neighbor?; e.g. after merging, can we combine `cut`s into `rules` (where rules
# are just a set of cuts grouped by their column id).

# A rule bundles together all the cuts that reference the same column.
def cuts2Rule(cuts):
   d = defaultdict(list)
   [d[cut[0]].append(cut) for cut in cuts]
   return tuple(sorted([tuple(sorted(set(x))) for x in d.values()]))

#  To combine rules, tear them down to their cuts and then build a new rule.
def rules2rule(rules):
   return cuts2Rule(cut for rule in rules for cuts in rule for cut in cuts)

# `Rule`s can select rows from multiple `labelledRows`.
def selects(rule, labelledRows):
   return {label: select(rule,rows) for label,rows in labelledRows}

# `Rule`s can pull specific `rows`.
def select(rule, rows): return [row for row in rows if ands(rule,row)]

# `Rule` is a  collection of  conjunctions. If any are false, then the rule fails.
def ands(rule,row):
   for cuts in rule:
      if not ors(row[cuts[0][0]], cuts): return False
   return True

# For each disjunction in `cuts`, at least one c`cut` must be true (else, return None).
def ors(x, cuts):
   for cut in cuts:
      if true(x, cut): return cut

# Is it true that this `cut` hold `x`?
def true(x, cut):
   _,lo,hi = cut
   return  x=="?" or lo==hi==x or  x > lo and x <= hi

# To display a rule, within an attribute, combine adjacent cuts.
# Note that this returns a new rule since, once combined, this
# new rule can no longer be used if `cuts2rule` or rules2rule`,
def showRule(rule):
   def spread(ins):
      i,outs = 0,[]
      while i < len(ins):
         c,lo,hi = ins[i]
         while i < len(a) - 1 and hi == ins[i+1][1]:
            hi = ins[i+1][2]
            i += 1
         outs += [(c,lo,hi)]
         i += 1
      return tuple(outs)
   return tuple(spread(v) for k,v in rule.items())
#-------------------------------------------------------------------------------
# ## Columns

# Here's a class that can pretty print itself
class pretty: __repr__ = lambda i:showd(i.__dict__, i.__class__.__name__)
# ### Summarize SYMs
class SYM(pretty):
   def __init__(i,a,at=0,name=" "):
      d = Counter(a)
      i.n, i.at, i.name = len(a), at, name
      i.mid, i.div = mode(d), entropy(d)
      i.cuts = [(at,x,x) for x in sorted(set(d))]
      i.cardinality = len(i.cuts)

# ### Summarize NUMs
class NUM(pretty):
   def __init__(i,a,at=0,name=" "):
      a = sorted(a)
      i.n, i.at, i.name = len(a), at, name
      i.mid, i.div = median(a), stdev(a)
      i.lo, i.hi, i.heaven = a[0], a[-1], 0 if name[-1] == "-" else 1
      i.cuts = i._unsupercuts(at,a)

   # Map `x` 0..1 for `lo..hi`".
   def norm(i,x): return x if x=="?" else (x- i.lo)/(i.hi - i.lo + 1/big)

   def _unsupercuts(i,at,a): # simplistic (equal frequency) unsupervised discretization
      n = inc = int(len(a)/(the.bins - 1))
      cuts, lo, small = [], a[0], the.cohen*i.div
      while n < len(a) -1 :
         hi = a[n]
         if hi==a[n+1] or hi - lo < small:
            n += 1
         else:
            n += inc
            cuts += [(at,lo,hi)] # [(col, lo, hi)]
            lo = hi
      if len(cuts) < 2: return [(at, -inf, inf)] # ensure cuts run -inf to inf
      cuts[ 0] = (at, -inf,        cuts[0][2])
      cuts[-1] = (at, cuts[-1][1], inf)
      return cuts
#---------------------------------------------------------------------------------------------------
# ## TABLE
# Store many `rows` and  the none "?" values in each column (in `cols`).
# Note that first `row` is a list of column `names`. Also, the column `names` can be
# categories as follows:
ako = slots(num  = lambda s: s[0].isupper(),
            goal = lambda s: s[-1] in "+-",
            skip = lambda s: s[-1] == "X",
            xnum = lambda s: not ako.goal(s) and ako.num(s),
            xsym = lambda s: not ako.goal(s) and not ako.num(s))

class TABLE(pretty):
   def __init__(i, src): i._cols( i._rows(src))

   def _rows(i,src): # src is a list of list, or an iterator that returns lists from files
      for n,row in enumerate(src):
         if n==0:
            i.rows, i.names, cache = [], row, [[] for _ in row]
         else:
            i.rows += [row]
            [a.append(x) for a,x in zip(cache,row) if x != "?"]
      return cache

   def _cols(i,cache): # Make columns using the information cached while reading rows
      i.cols = slots(all = [(NUM if ako.num(name) else SYM)(a, at, name)
                            for at,(name,a) in enumerate(zip(i.names,cache))])
      for k,fun in ako.items():
         i.cols[k] = [c for c in i.cols.all if not ako.skip(c.name) and fun(c.name)]

  # How to report stats on each column.
   def stats(i, cols="goal", decimals=None, want="mid"):
      return slots(N=len(i.rows), **{c.name:show(c.__dict__[want],decimals) for c in i.cols[cols]})

   # How to sort the rows closest to furthest from most desired
   def sorted(i, cols="goal"):
      def _distance2heaven(row):
         return sum((col.heaven - col.norm(row[col.at]))**2 for col in i.cols[cols])**.5
      return sorted(i.rows, key=_distance2heaven)

   # How to make a new TABLE that copies the structure of an this TABLE (and fill in with `rows`).
   def clone(i, a=[]): return TABLE( [i.names] + a)

#-------------------------------------------------------------------------------
# ## Discretization
# `Merging` contains ranges to be used in the rule generation.
# It looks for ways to combine `col.cuts` and reports 
# `slots(x=(columnIndex,lo, hi) y=Counter(labelCounts))`
# showing frequency counts of these ranges amongst these `labelledRows`.
# (and this  is a set of pairs `[(label1,rows1),(label2,rows2)...]`).
def supercuts(data, labelledRows):
   def _counts(col, cuts, labelledRows): # how often is `cit` seen in different rows?
      counts = {cut : slots(x=cut, y=Counter()) for cut in cuts}
      for label,rows in labelledRows:
         for row in rows:
            x = row[col.at]
            if x != "?":
               counts[ ors(x,cuts) ].y[ label ] += 1
      return sorted(counts.values(), key=lambda z:z.x)

   def _merges(ins): # Try merging any thing with its neighbor. Stop when no merges found
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

   def _merge(a,b): # merge  a,b unless the whole is more complex than that parts
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
def scores(table):
   rows = table.sorted()
   n    = int(len(rows)**the.min)
   bests, rests = rows[:n], random.sample(rows[n:], n*the.rest)
   labelledRows = [("best",bests), ("rest", rests)]
   cuts = supercuts(table, labelledRows)
   ordered = sorted([(score(cut.y["best"], cut.y["rest"], len(bests), len(rests)),cut) 
                     for cut in cuts],
                     reverse = True,
                     key = lambda z:z[0])
   return [z[1].x for z in ordered], bests,rests

# Given you've found `b` or `r`, how much do we like you?
def score(b, r, B,R):
  b, r = b/(B+1/big), r/(R+1/big)
  r += 1/big
  match the.want:
    case "plan"    : return b**2 /    (b + r)  # seeking best
    case "monitor" : print(1); return r**2  /    (b + r)  # seeking rest
    case "doubt"   : return (b+r) / abs(b - r)  # seeking border of best/rest 
    case "xplore"  : print(2); return 1     /    (b + r)  # seeking other

#---------------------------------------------
def showd(d,pre=""):
   return pre + "{" + (" ".join([f":{k} {show(v,3)}" for k,v in d.items() if k[0] != "_"])) + "}"

# If decimals offered, then round to that. else just return `x`
def show(x,decimals=None):
  if callable(x): return x.__name__
  if decimals is None or not isinstance(x,float): return x
  return round(x,decimals)

# Given a sorted list of numbers `a` or a dictionary `d` containing frequency counts
# for each key, what can we report?  
def per(a,n=.5):  return a[int(n*len(a))]
def median(nums): return per(nums, .5) # middle number
def stdev(nums):  return (per(nums,.9) - per(nums,.1))/ 2.56 # div=diversity
def mode(d):      return max(d, key=d.get) # most frequent number
def entropy(d):   # measures diversity for symbolic distributions
   n = sum(d.values())
   return -sum(m/n * log(m/n,2) for m in d.values() if m>0)

# Some standard short cuts
big = 1e100
R = random.random

def csv(file="-"):
   with  fileinput.FileInput(file) as src:
      for line in src:
         line = re.sub(r'([\n\t\r"\' ]|#.*)', '', line)
         if line:
            yield [coerce(x) for x in line.split(",")]

def cli2dict(d):
   for k, v in d.items():
      s = str(v)
      for j, x in enumerate(sys.argv):
         if ("-"+k[0]) == x or ("--"+k) == x:
            d[k] = coerce("True" if s == "False" else ("False" if s == "True" else sys.argv[j+1]))

def powerset(s):
  x = len(s)
  for i in range(1 << x):
     if tmp :=  [s[j] for j in range(x) if (i & (1 << j))]: yield tmp

def prints(*t): print(*t,sep="\t")

def printd(*d):
   prints(*list(d[0].keys()))
   [prints(*list(d1.values())) for d1 in d]

def different(x,y):
  return cliffsDelta(x,y) and bootstrap(x,y)

def cliffsDelta(x,y):
   if len(x) > 10*len(y) : return cliffsDelta(random.choices(x,10*len(y)),y)
   if len(y) > 10*len(x) : return cliffsDelta(x, random.choices(y,10*len(x)))
   n,lt,gt = 0,0,0
   for x1 in x:
      for y1 in y:
         n = n + 1
         if x1 > y1: gt = gt + 1
         if x1 < y1: lt = lt + 1
   return abs(lt - gt)/n > the.Cliffs # true if different

def bootstrap(y0,z0,conf=.05):
   obs= lambda x,y: abs(x.mid-y.mid) / ((x.div**2/x.n + y.div**2/y.n)**.5 + 1/big)
   x, y, z = NUM(y0+z0), NUM(y0), NUM(z0)
   d = obs(y,z)
   yhat = [y1 - y.mid + x.mid for y1 in y0]
   zhat = [z1 - z.mid + x.mid for z1 in z0]
   n      = 0
   for _ in range(the.Bootstraps):
      ynum = NUM(random.choices(yhat,k=len(yhat)))
      znum = NUM(random.choices(zhat,k=len(zhat)))
      if obs(ynum, znum) > d:
         n += 1
   return n / the.Bootstraps < conf # true if different
#---------------------------------------------
# ## Start-up Actions

# Before eacha ction, reset the random num 
class go:
   _saved = copy.deepcopy(the)
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
      the = copy.deepcopy(go._saved)
      return failed

   def all():
      "run all actions, return number of failures"
      sys.exit(sum(map(go._run,[fun for s,fun in go._all.items() if s != "all" and s[0].islower()])))

   def help():
       "show help"
       def yell(s) : return colored(s[1], "yellow",attrs=["bold"])
       def bold(s) : return colored(s[1], "white", attrs=["bold"])
       def say(s)  : return re.sub(r"(\n[A-Z]+:)", yell, re.sub(r"(-[-]?[\w]+)", bold, s))
       print(say(__doc__ + "\nACTIONS:"))
       [print(say(f"  -g {x:8} {f.__doc__}")) for x,f in go._all.items() if x[0].islower()]

   def the():
      "show config"
      print(the)

   def powerset():
      "Can we find all subsets of 4 things?"
      [print(x) for x in powerset("abcd")]
      t1= time.perf_counter()
      n=1
      for y  in powerset("01234567"): n = n+1
      print(n,time.perf_counter() - t1)

   def sym():
      "can we find entropy of some syms"
      a = SYM('aaaabbc')
      print(a.mid, a.div, ' '.join([f"({c} {x} {y})" for c,x,y in  a.cuts]))

   Normal= lambda mu,sd: mu+sd*sqrt(-2*log(R())) * cos(2*pi*R())
   def nums():
      "can we find mean and sd of N(10,1)?"
      a= NUM([go.Normal(10,1) for x in range(1000)])
      print(a.mid,a.div,' '.join([f"({c} {x:.2f} {y:.2f})" for c,x,y in  a.cuts]))

   def stats():
      a = [go.Normal(10,1) for _ in range(128)]
      yn = lambda x: "y" if x else "."
      print(the.seed)
      r = 0
      prints("a.mu","b.mu","cliffs","boot","c+b")
      while r <= 3:
         b = [go.Normal(10+r,3) for _ in range(128)]
         prints(10,f"{10+r}", yn(cliffsDelta(a,b)),yn(bootstrap(a,b)),yn(different(a,b)))
         r += .25

   def read():
      "can we print rows from a disk-based csv file?"
      [prints(*row) for r,row in enumerate(csv(the.file)) if r < 10]

   def data():
      "can we load disk rows into a TABLE?"
      table = TABLE(csv(the.file))
      printd(table.stats())

   def sorted():
      "can we find best, rest rows?"
      table= TABLE(csv(the.file))
      a    = table.sorted()
      n    = int(len(a)**the.min)
      printd(table.stats(),
             table.clone(a[:n]).stats(),
             table.clone(a[-n*the.rest:]).stats())

   def discret():
      "can i do supervised discretization?"
      table = TABLE(csv(the.file))
      cuts0, bests, rests = scores(table)
      cuts0 = cuts0[:the.Top]
      all = []
      for cuts1 in powerset(cuts0):
         rule = cuts2Rule(cuts1)
         small = len(cuts1)/(2**len(cuts0))
         d = selects(rule, [("best",bests), ("rest",rests)])
         all += [((score(*map(len,[d["best"],d["rest"],bests,rests]))**2+(1-small)**2)**.5/2**.5,
                  rule)]
      bestRule = sorted(all, key=lambda x:x[0], reverse=True)[0][1]
      selected = select(bestRule, table.rows)
      prints("","N", *[col.name for col in table.cols.goal])
      prints("old",  *table.stats().values())
      prints("want", *table.clone(bests).stats().values())
      prints("got",  *table.clone(selected).stats().values())
      print(R())

   Weather=[
      ("best",[["overcast", 83, 86, "FALSE", "yes"],
               ["rainy",    70, 96, "FALSE", "yes"],
               ["rainy",    68, 80, "FALSE", "yes"],
               ["overcast", 64, 65, "TRUE",  "yes"],
               ["sunny",    69, 70, "FALSE", "yes"],
               ["rainy",    75, 80, "FALSE", "yes"],
               ["sunny",    75, 70, "TRUE",  "yes"],
               ["overcast", 72, 90, "TRUE",  "yes"],
               ["overcast", 81, 75, "FALSE", "yes"]]),
      ("rest",[["sunny",    85, 85, "FALSE", "no"],
               ["rainy",    65, 70, "TRUE",  "no"],
               ["sunny",    72, 95, "FALSE", "no"],
               ["rainy",    71, 91, "TRUE",  "no"],
               ["sunny",    80, 90, "TRUE",  "no"]])]

   def cuts():
      "can i do supervised discretization?"
      threes = [rule for s,rule in scores(TABLE(csv(the.file)))]
      rule = cuts2Rule( ((0,"overcast", "overcast"),(1,80, 90), (1, -inf,  65) ) )
      rule = rules2rule([rule,rule,rule,rule])
      print(rule)
      selected = selects(rule, go.Weather)
      [print("best",x) for x in selected["best"]]
      [print("rest",x) for x in selected["rest"]]


if __name__ == "__main__": go._on()
