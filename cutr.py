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

# In this code, global settings are kept in `the` (which is parsed from `__doc__`).
# This variable is a `slots`, which is a neat way to represent dictionaries that
# allows easy slot access (e.g. `d.bins` instead of `d["bins"]`)
class slots(dict): __getattr__ = dict.get 
the = slots(**{m[1]: lit(m[2]) for m in re.finditer( r"\n\s*-\w+\s*--(\w+).*=\s*(\S+)",__doc__)})
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
   d0,d = defaultdict(list),{}
   [d0[cut[0]].append(cut) for cut in cuts]
   for k in d0:
      tmp = simpler(sorted(d0[k])):
      if not(tmp[0][1] == -inf and tmp[0][2] == inf):
         d[k] = tuple(tmp)
   if len(d) > 0:
      return tuple(sorted(d.values()]))

def simpler(ins):
   i,outs = 0,[]
   while i< len(ins):
      c,lo,hi = ins[i]
      while i < len(a) - 1 and hi == ins[i+1][1]:
         hi = ins[i+1][2]
         i += 1
      outs += [(c,lo,hi)]
      i += 1
   return outs

#  To combine rules, tear them down to their cuts and then build a new rule.
def rules2rule(rules):
   return cuts2Rule((cut for rule in rules
                            for cuts in rule
                               for cut in cuts))

# Rules can select rows
def selects(rule, labelledRows):
   counts, selected = Counter(), defaultdict(list)
   for label, rows in labelledRows:
      for row in rows:
         if ands(rule,row):
            selected[label] += [row]
            counts[label] += 1/len(rows)
   return counts, selected

# `rule` is a  collection of  conjunctions. If any of them are false, then
# the rule fails.
def ands(rule,row):
   for cuts in rule:
      if not ors(row[cuts[0][0]], cuts): return False
   return True

# `cuts` are  a collection of  disjunctions,  of which at least one of which must
# be true  (otherwise, return None).
def ors(x, cuts):
   for cut in cuts:
      if true(x, cut): return cut

# Is it true that this `cut` hold `x`?
def true(x, cut):
   _,lo,hi = cut
   return  x=="?" or lo==hi==x or  x > lo and x <= hi
#-------------------------------------------------------------------------------
# ## Columns

# Here's a class that can pretty print itself
class pretty: __repr__ = lambda i:showd(i.__dict__, i.__class__.__name__) 
# ### Summarize SYMs
class SYM(pretty):
   def __init__(i,a,at=0,name=" "):
      d = Counter(a)
      i.at, i.name = at, name
      i.mid, i.div = mode(d), entropy(d)
      i.cuts = [(at,x,x) for x in sorted(set(d))]
      i.cardinality = len(i.cuts)

# ### Summarize NUMs
class NUM(pretty):
   def __init__(i,a,at=0,name=" "):
      a = sorted(a)
      i.at, i.name = at, name
      i.mid, i.div = median(a), stdev(a)
      i.lo, i.hi, i.heaven = a[0], a[-1], 0 if name[-1] == "-" else 1
      i.cuts = i._unsupercuts(at,a)

   # Map `x` 0..1 for `lo..hi`".
   def norm(i,x): return x if x=="?" else (x- i.lo)/(i.hi - i.lo + 1/big)

   def _unsupercuts(i,at,a): # simplistic (equal frequency) unsupervised discretization
      n = inc = int(len(a)/(the.bins - 1))
      cuts, b4, small = [], a[0], the.cohen*i.div
      while n < len(a) -1 :
         x = a[n]
         if x==a[n+1] or x - b4 < small: 
            n += 1
         else:
            n += inc
            cuts += [(at,b4,x)] # [(col, lo, hi)]
            b4 = x
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
         return sum(( (col.heaven - col.norm(row[col.at]))**2 for col in i.cols[cols] ))**.5
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
               counts[ ors(x,cuts) ].y[ label ] += 1/len(rows)
      return sorted(counts.values(), key=lambda z:z.x)

# SXXX stoping doing the 1/len(rows) trick. bad karma
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
# Given you've found `b` or `r`, how much do we like you?
def score(b, r):
  r += 1/big # stop divide by zero errors
  match the.want:
    case "plan"    : return b**2  /    (b + r)  # seeking best
    case "monitor" : print(1); return r**2  /    (b + r)  # seeking rest
    case "doubt"   : return (b+r) / abs(b - r)  # seeking border of best/rest 
    case "xplore"  : print(2); return 1     /    (b + r)  # seeking other

def scores(data):
   rows  = data.sorted()
   n     = int(len(rows)**the.min)
   bests,rests  = rows[:n], rows[-n*the.rest:]
   labelledRows = [("best",bests), ("rests",rests)]
   for (s,x) in sorted([(score(cut.y["best"], cut.y["rest"]),cut) for cut in
                        supercuts(data,labelledRows)], reverse=True,
                        key=lambda z:z[0]):
      yield s,x.x

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
   return -sum((m/n * log(m/n,2) for m in d.values() if m>0))

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

# Some standard short cuts
big = 1e100
R = random.random

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
       def say(s)  : return re.sub(r"(\n[A-Z]+:)", yell, re.sub(r"(-[-]?[\w]+)", bold, s))
       print(say(__doc__ + "\nACTIONS:"))
       [print(say(f"  -g {x:8} {f.__doc__}")) for x,f in go._all.items() if x[0].islower()]

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
      "can we load disk rows into a TABLE?"
      table = TABLE(csv(the.file))
      prints(table.stats())

   def sorted():
      "can we find best, rest rows?"
      table= TABLE(csv(the.file))
      a    = table.sorted()
      n    = int(len(a)**the.min)
      prints(table.stats(),
             table.clone(a[:n]).stats(),
             table.clone(a[-n*the.rest:]).stats())

   def discret():
      "can i do supervised discretization?"
      for s,x in TABLE(csv(the.file)).sorted():
         print(f"{s:.3f}\t{x}")

   Weather = [["outlook","Temp","Humid","windy","play"],
              ["sunny","85","85","FALSE","no"],
              ["sunny","80","90","TRUE","no"],
              ["overcast","83","86","FALSE","yes"],
              ["rainy","70","96","FALSE","yes"],
              ["rainy","68","80","FALSE","yes"],
              ["rainy","65","70","TRUE","no"],
              ["overcast","64","65","TRUE","yes"],
              ["sunny","72","95","FALSE","no"],
              ["sunny","69","70","FALSE","yes"],
              ["rainy","75","80","FALSE","yes"],
              ["sunny","75","70","TRUE","yes"],
              ["overcast","72","90","TRUE","yes"],
              ["overcast","81","75","FALSE","yes"],
              ["rainy","71","91","TRUE","no"]]

   def rules():
      "can i do supervised discretization?"
      threes = [rule for s,rule in scores(TABLE(csv(the.file)))]
      rule = threes2Rule(threes)
      print(rules2rule([rule,rule,rule]))
      #print(  rule) #rule2Threes(rule))

if __name__ == "__main__": go._on()
