#!/usr/bin/env python3 -B
# <!--- vim: set et sts=2 sw=2 ts=2 : --->
""" 
ORD: simple multi objective explanation (using unsupervised discretion)   
(c) 2023 Tim Menzies <timm@ieee.org> BSD.2   
   
USAGE:   
  ./ord.py [OPTIONS] [-g ACTIONS]   
   
OPTIONS:   
  -b  --bins   max number of bins         = 7   
  -B  --Beam   search width               = 10   
  -c  --cohen  measure of same            = .35   
  -f  --file   data file                  = "../data/auto93.csv"   
  -g  --go     startup action             = "nothing"   
  -h  --help   show help                  = False   
  -m  --min    min size                   = .5   
  -r  --rest   best times rest            = 4   
  -s  --seed   random number seed         = 937162211   
  -S  --Some   how may nums to keep       = 256   
  -w  --want   plan|monitor|xplore|doubt  = "plan"   
"""
# ----------------------------------------------------
import random, sys, re
from copy import deepcopy
from termcolor import colored
from ast import literal_eval as literal
from fileinput import FileInput as file_or_stdin
# --------------------------------------------------------
class obj(object):
  """My base objects:  pretty prints; can be initialized easily;
  all content available via self.it.""" 
  def __init__(i, **d): i.it.update(**d)
  @property
  def it(i): return i.__dict__
  def __repr__(i):
    def f(x): return x.__name__ if callable(x) else (f"{x:3g}" if isa(x, float) else x)
    return "{"+" ".join([f":{k} {f(i.it[k])}" for k in i.it if k[0] != "_"])+"}"
# --------------------------------------------------------
def score(b, r, B, R):
  "Given you've found `b` or `r` items of `B,R`, how much do we like you?"
  b = b/(B+1/big)
  r = r/(R+1/big)
  match the.want:
    case "plan"    : return b**2 / (   b + r)    # seeking best
    case "monitor" : return r**2 / (   b + r)    # seeking rest
    case "doubt"   : return (b+r) / abs(b - r)   # seeking border of best/rest 
    case "xplore"  : return 1 / (   b + r)       # seeking other

def within(x, lo, hi): return lo <= x < hi
# --------------------------------------------------------
class ROW(obj):
  def __init__(i, a):
    i.cells, i.cooked = a, a[:]
# --------------------------------------------------------
class SYM(obj):
  def __init__(i, n=0, s="") :
    i.at,i.txt,i.n = n,s,0
    i.seen, i.most, i.mode = {},0,None

  def add(i, x):
    if x != "?":
      i.n += 1
      tmp = i.seen[x] = 1 + i.seen.get(x, 0)
      if tmp > i.most:
        i.most, i.mode = tmp, x

  def dist(i, a, b):
    return 0 if a==b else 1

  def div(i, decimals=None):
    return rnd(ent(i.seen), decimals)

  def getChops(i, bestRows, restRows):
    tmp = {}
    for klass,rows in dict(best=bestRows, rest=restRows).items():
      for row in rows:
        x = row.cells[i.at]
        if x != "?":
          if x not in tmp: tmp[x] = obj(lo=x, hi= x, n=it(best=0, rest=0))
          tmp[x][klass] += 1
    return [[x.lo, x.hi, x.n.b, x.n.r] for x in tmp.values]

  def mid(i, decimals=None):
    return i.mode
# -----------------------------------------------------------------------------
class NUM(obj):
  def __init__(i, n=0, s="") :
    i.at,i.txt,i.n = n,s,0
    i._kept, i.ok = [],True
    i.heaven = 0 if s and s[-1] == "-" else 1

  def add(i, x):
    if x != "?":
      i.n += 1
      if len(i._kept) < the.Some:
        i.ok = False
        i._kept += [x]
      elif R() < the.Some / i.n:
        i.ok = False
        i._kept[int(len(i._kept)*R())] = x

  def dist(i,a,b):
    a = a if a != "?" else (1 if b < .5 else 0)
    b = b if b != "?" else (1 if a < .5 else 0)
    return abs(a-b)

  def div(i, decimals=None):
    n=len(i.kept)
    return rnd((i.kept[.9*n//1] - i.kept[.1*n//1])/2.56, decimals)

  def getChops(i, bestRows, restRows):
    def x(row)  : return row.cells[i.at]
    def x1(pair): return x(pair[1])
    def _divide(pairs):
      few = int(len(pairs)/the.bins) - 1
      tiny = the.cohen*i.div()
      now = obj(lo=x1(pairs[0]), hi=x1(pairs[0]), n=it(best=0, rest=0))
      tmp = [now]
      for i, (klass, row) in enumerate(pairs):
        here = x(row)
        if len(pairs) - i > few * .67 and here != x1(pairs[i-1]):
          if here - now.lo > tiny and now.n.best + now.n.rest > few:
            now = obj(lo=now.hi, hi=here, n=it(best=0, rest=0))
            tmp += [now]
        now.hi = here
        now.n[klass] += 1
      return tmp

    def _merge(ins):
      outs, i = [], 0
      while i < len(ins):
        a = ins[i]
        if i < len(ins)-1:
          b = ins[i+1]
          merged = obj(lo=a.lo, hi=b.hi, n=it(best=a.n.best+b.n.best, rest=a.n.rest+b.n.rest))
          A, B = a.n.best+a.n.rest, b.n.best+b.n.rest
          if ent(merged.n) <= (ent(a.n)*A + ent(b.n)*B) / (A+B): # merged's is clearer than a or b
            a = merged
            i += 1  # skip over b since we have just merged it with a
        outs += [a]
        i += 1
      return ins if len(ins) == len(outs) else _merge(outs)
    bests = [("best", row) for row in bestRows if x(row) != "?"]
    rests = [("rest", row) for row in restRows if x(row) != "?"]
    B, R = len(bestRows) + 1/big, len(restRows)+1/big
    tmp = [[x.lo, x.hi, x.n.b, x.n.r] for x in _merge( _divide( sorted(bests+rests, key=x1)))]
    tmp[ 0][0] = -big  # lowest lo is negative infinity
    tmp[-1][1] = big  # highest hi is positive infinity
    return {rnd(k/(len(out)-1)): tuple(lohi) for k, lohi in enumerate(tmp)}


  @property
  def kept(i):
    if not i.ok:
      i._kept, i.ok = sorted(i._kept), True
    return i._kept

  def mid(i, decimals=None):
    n=len(i.kept)
    return rnd(i.kept[.5*n//1], decimals)
# -----------------------------------------------------------------------------
class COLS(obj):
  def __init__(i, names):
    i.x, i.y, i.all, i.names = [], [], [], names
    for n, s in enumerate(names):
      col = (NUM if s and s[0].isupper() else SYM)(n=n, s=s)
      i.all += [col]
      if col.txt[-1] != "X":
        (i.y if col.txt[-1] in "+-" else i.x).append(col)

  def add(i, row):
    [col.add(row.cells[col.at]) for cols in [i.x, i.y] for col in cols]
# -----------------------------------------------------------------------------
class DATA(obj):
  def __init__(i, src=[]):
    i.rows, i.cols = [], None
    i.adds(src)

  def add(i, row):
    def _create(): i.cols = COLS(row.cells)
    def _update(): i.rows += [i.cols.add(row)]
    _update() if i.cols else _create()

  def adds(i, l):
    [i.add(x) for x in l]; return i

  def clone(data, rows=[]):
    return DATA([ROW(data.cols.names)]).add(rows)

  def dist(i,row1,row2):
    def _dist1(col):
      a,b= row1.cooked[a], row2.cooked[2]
      return 1 if a=="?" and b=="?" else col.dist(a,b)
    return sum((_dist(col)**the.p for col in i.cols.x))**1/the.p /  len(i.cols.x)**1/the.p

  def sortedRows(i, rows=None, cols=None):
    def _distance2heaven(row):
      nom = sum(( (col.heaven - row.cooked[col.at])**2 for col in cols or i.cols.y ))
      return (nom/len(data.cols.y))**.5
    return sorted(rows or i.rows, key=_distance2heaven)

  def stats(i, cols=None, what="mid", decimals=3):
    def fun(col): return (col.mid if what == "mid" else col.div)(decimals)
    return obj(N=len(i.rows),**{col.txt: fun(col) for col in cols or i.cols.y})
# -----------------------------------------------------------------------------
def cols2Chops(data):
  def _sym(col):
    col.chops = {k: (k, k) for k in col.seen.keys()}

  def _num(col):
    col.chops = num2Chops(col/2, col.kept, the.cohen, the.bins)
    for row in data.rows:
      row.cooked[col.at] = x2range(row.cells[col.at], col.chops)
  for col in data.cols.x:
    (_sym if col.this is SYM else _num)(col)
  return data

def sortedChops(data, bestRows, restRows):
  def _count():
    d = {}
    for klass, rows in [(True, bestRows), (False, restRows)]:
      dk = d[klass] = {}
      for row in rows:
        for col in data.cols.x:
          x = row.cooked[col.at]
          if x != "?":
            k = (col.at, col.txt, x)
            dk[k] = 1 + dk.get(k, 0)
    return d

  def _score(d):
    out = []
    hi = 0
    for x, best in d[True].items():
      rest = d[False].get(x, 0) + 1/big
      v = score(best, rest, len(bestRows), len(restRows))
      hi = max(hi, v)
      out += [(rnd3(v), rnd3(best), rnd3(rest), x)]
    return [x for x in out if x[0] > hi/10]
  return sorted( _score( _count()), reverse=True)[:the.Beam]
# ----------------------------------------------------
# XXX waht ranges and mtj etc/ return dict.
# d[short] = lomho
# -- this needs to be in a test
the = None
R = random.random
isa = isinstance
big = 1E30

class SETTINGS(obj):
  def __init__(i,s):
    i.help = s
    want = r"\n\s*-\w+\s*--(\w+).*=\s*(\S+)"
    super().__init__(**{m[1]: literal(m[2]) for m in re.finditer(want, s)})

  def cli(i):
    for k, v in i.it.items():
      s = str(v)
      for j, x in enumerate(sys.argv):
        if ("-"+k[0]) == x or ("--"+k) == x:
          s = "True" if s == "False" else ("False" if s == "True" else sys.argv[j+1])
      i.it[k] = str2thing(s)
    if i.it["help"]: i.exitWithHelp()
    return i

  def exitWithHelp(i):
    def yell(s): return colored(s[1], "yellow",attrs=["bold"])
    def bold(s): return colored(s[1], "white", attrs=["bold"])
    egs= "ACTIONS:\n"+"\n".join([f"  -g  {s:8} {i.help}" for s,f in EG.DO().items()])
    print(re.sub(r"(\n[A-Z]+:)", yell, re.sub(r"(-[-]?[\w]+)", bold, __doc__ + "\n" + egs)))
    sys.exit(0)

def csv2Rows(file):
  with file_or_stdin(None if file == "-" else file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r"\' ]|#.*)', '', line)
      if line:
        yield ROW([str2thing(s.strip()) for s in line.split(",")])

def ent(d):
  N = sum(d.values())
  return - sum(( n/N * math.log(n/N, 2) for n in d.values() if n > 0 ))

def rnd(x, decimals=3): 
  return x if decimals is None else round(x, decimals)

def str2thing(x: str):
  try:
    return literal(x)
  except BaseException:
    return x

def x2range(x, ranges):
  if x == "?":
    return x
  for k, (lo, hi) in ranges.items():
    if within(x, lo, hi):
      return k
  assert False, "should never get here"

def pick(lst, n):
  r = R()
  for (m, x) in lst:
    r -= m/n
    if r <= 0:
      return x
  assert False, "should never get here"
# --- oops! two scores
# - hide bestRows,restORws inside a lambda
def grow(lst, bestRows, restRows, peeks=32, beam=None):
  beam = beam or len(lst)
  if beam < 2 :
    return lst
  lst = sorted(lst, key=lambda y: -y[0])[:int(.5+beam)]
  tmp = []
  for a, b in pick2(lst, peeks):
    c = TEST([test for ab in [a, b] for ors in ab.ors.values() for test in ors])
    b = [row for row in bestRows if selects(c, row)]
    r = [row for row in restRows if selects(c, row)]
    v = score(*map(len, [b, r, bests, rests]))
    tmp += [(v, c)]
  return grow(lst+tmp, bestRows, restRows, peeks, beam/2)

# ----------------------------------------------------
class EG:
  def DO(a=locals()) : return {s:fun for s,fun in a.items() if s[0].islower()}
  def RUN(a=sys.argv): the.cli(); getattr(EG, the.go, dir)()
  def RUN1(fun):
    saved = deepcopy(the)
    random.seed(the.seed)
    failed = fun() == False
    print("❌ FAIL" if failed else "✅ PASS", fun.__name__)
    the = deepcopy(saved)
    return failed
  # --------------------------------
  def all() :
    "run all actions, return sum of failures."
    sys.exit(sum(map(EG.RUN1,EG.DO())))

  def the() :
    "show config options"
    print(the)

  def data() :
    "can we read data from disk and print its stats?"
    stats1 = DATA(csv2Rows(the.file)).stats()
    print(*stats1.it.keys(),sep="\t")
    print(*stats1.it.values(),sep="\t")

  # its flopped
  def sorted():
    "can we sort the rows into best and rest?"
    data = DATA(csv2Rows(the.file))
    rows = data.sortedRows()
    print(*data.cols.names,sep="\t")
    [print(*row.cells,sep="\t") for row in rows[:10]]
    print("")
    [print(*row.cells,sep="\t") for row in rows[-10:]]
    stats1 = clone(data, rows[:40]).stats()
    stats2 = clone(data, rows[40:]).stats()
    print(*["\n"]+list(stats1.it.keys()),sep="\t")
    print(*["best"]+list(stats1.it.values()),sep="\t")
    print(*["rest"]+list(stats2.it.values()),sep="\t")

  def ideas():
    "can we find good ranges?"
    data = DATA(csv2Rows(the.file))
    rows = data.sortedRows()
    chops(data)
    n = int(len(rows)**the.min)
    bestRows = rows[:n]
    restRows = random.sample( rows[n+1:], n*the.rest )
    print(*data.cols.names,sep="\t")
    [print(*row.cooked,sep="\t") for row in rows[:10]]
    print("")
    [print(*row.cooked,sep="\t") for row in rows[-10:]]
    print(*["\nv", "b", "r", "x"],sep="\t")
    for x in goodChops(data, bestRows, restRows):
      print(*x,sep="\t")
# ----------------------------------------------------

the = SETTINGS(__doc__)
EG.RUN()
