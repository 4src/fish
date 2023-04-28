#<!-- vim: set ts=2 sw=2 et: -->
"""
fish.py: look a little, catch some good stuff    
(c) 2023, Tim Menzies, <timm@ieee.org>  BSD-2    

              O  o    
         _\_   o    
      \\/   o\ .    
      //\___=    
         ''    

USAGE: 

      ./gofish.py [OPTIONS] [-g ACTIONs]    

OPTIONS:    

      -b  --bins    number of bins                         = 16    
      -B  --bootstrap number of bootstap samples           = 512  
      -c  --cohen   'not different' if under the.cohen*sd  = .2    
      -C  --Cliffs  Cliff's Delta limit                    = .147  
      -f  --file    data csv file                          = ../data/auto93.csv    
      -g  --go      start up action                        = nothing    
      -h  --help    show help                              = False    
      -m  --min     on N items, recurse down to N**min     = .5    
      -n  -n        explore all subsets of top ''n bins    = 7
      -r  --rest    expand to len(list)*rest               = 4    
      -s  --seed    random number seed                     = 1234567891    
      -S  --Some    max items kept in SOME                 = 512  
      -w --want     goal: plan,watch,xplore,doubt          = plan   

NOTES:

This code reads CSV files with a header row listing column names,
numeric columns, symbolic columns and goals. For example, in this
data set, we want to learn what values of `name,Age,Shoesize`
are associated with most  `Salary` and least `Weight`.

         name,  Age,  Shoesize, Salary+,  Weight-
          tim,   31,        11,  200000,      30
        susan,   41,         8,  300000,      50
         jane,   20,        20,  100000,      40
          ...   ...        ...      ...      ...

Nums start with upper case (and everything else is a Sym). Goals
end in "`-`" or "`+`" for things to minimize or maximize. Anything ending
with `X` is ignored.

Rows are then ranked on the goals, using a multi-objective domination
predicate (from Zitzler's 2004 work).  Attribute ranges are
binned, favoring those most different in the best and worst ranked
rows.  All \(2^n\) subsets of the best _n_ bins are then explored to find
the smallest subset that most selects for top ranked rows.

This code keeps code to 100 chars wide. It also uses `i` in place of `self`
and classes get initialized from a `slots` (why? causes its shorter). Also,
this code does not conform to PEP8 standards (why? causes that would be longer).
"""
from functools import cmp_to_key as cmp2key
from typing    import Dict, Any, List
from termcolor import colored
from copy      import deepcopy
import random, math, ast, sys, re, os

class obj(object):
  id=0
  def __init__(i, **d): i.__dict__.update(**i.slots(**d)); i.id = obj.id = obj.id+1
  def slots(i,**d)    : return d
  def __repr__(i)     : return i.__class__.__name__+showd(i.__dict__)
  def __hash__(i)     : return i.id

def coerce(x):
  try   : return ast.literal_eval(x)
  except: return x

the= obj(**{m[1]:coerce(m[2]) for m in re.finditer(
            r"\n\s*-\w+\s*--(\w+)[^=]*=\s*(\S+)", __doc__)})
#-----------------------------------------------------------------------------

# Summarizes  column one as `lo` to `hi` and column two by the symbols
#  in that column. Keeps the rows seen. 
class BIN(obj):

  # BIN contents.
  def slots(i, at=0, txt="", lo=None, hi=None):
    lo = lo or inf
    hi = hi or lo
    return dict(at=at,txt=txt,lo=lo,hi= hi,n=0,_rows=[],ys={},score=0)

  def add(i,x,y,row):
    "Updates `i.lo` to `i.hi` from `i.x` and  `ys` from `y`."
    if x=="?": return x
    i.n += 1
    i.lo = min(i.lo,x)
    i.hi = max(i.hi,x)
    i._rows += [row]
    i.ys[y] = 1 + i.ys.get(y,0)

  def merge(i,j):
    """Merge two adjacent bins."""
    out = BIN(at=i.at, txt=i.txt, lo=i.lo, hi=j.hi)
    out._rows = i._rows + j._rows
    out.n = i.n + j.n
    for d in [i.ys, j.ys]:
      for key in d:
        out.ys[key] = d[key] + out.ys.get(key,0)
    return out

  def merged(i,j,num):
    out   = i.merge(j)
    small = num.n / the.bins
    eps   = num.sd*the.cohen
    if i.n <= small or i.hi - i.lo < eps : return out
    if j.n <= small or j.hi - j.lo < eps : return out
    e1, e2, e3 = entropy(i.ys), entropy(j.ys), entropy(out.ys)
    if e3 <= (i.n*e1 + j.n*e2)/out.n : return out

#-----------------------------------------------------------------------------
def COLS(names):
  "Factory for turning column names into COLs."
  cols,x,y = [COL(at=i,txt=s) for i,s in enumerate(names)], [], []
  for col in cols:
    if col.txt[-1] != "X":
      (y if col.txt[-1] in "+-" else x).append(col)
  return names,cols,x,y

def COL(at=0,txt=" "):
  "Factory for turning one column name into a NUM or SYM."
  w = -1 if txt[-1] == "-" else 1
  return NUM(at=at,txt=txt,w=w) if txt[0].isupper() else SYM(at=at,txt=txt)

class col(obj):
  "Super class of NUM and SYM."
  def slots(i,at=0,txt=" "):
    "Cols have at least a name and a position in the row."
    return dict(at=at, txt=txt, bins={}, n=0)

  def adds(i,lst): 
    "Add many things to a COL."
    [i.add(x) for x in lst]; return i

  def add(i,x,inc=1):
    "Add thing `x` to a COL (ignoring empty cells)."
    if x=="?": return x
    i.n += inc
    i.add1(x,inc)

  def bin(i,x,y,row):
    k = i.descretize(x)
    if not k in i.bins: i.bins[k] = BIN(at=i.at, txt=i.txt, lo=x)
    i.bins[k].add(x,y,row)

#-------------------------------------------------------------------------------
class SYM(col):
  def slots(i,**d): return super().slots(**d) | dict(has={},mode=None,most=0)

  def mid(i): return i.mode
  def div(i): return entropy(i.has)
  def stats(i, div=False, **_) : return i.div() if div else i.mid()

  def add1(i,x,inc=1):
    i.has = i.has or {}
    tmp = i.has[x] = inc + i.has.get(x,0)
    if tmp > i.most: i.most,i.mode = tmp,x

  def descretize(i,x): return x
  def merges(i,bins): return bins

#-------------------------------------------------------------------------------
class NUM(col):
  def slots(i,at=0,txt=" ",w=1) :
    return super().slots(at=at,txt=txt) | dict(w=1,mu=0,m2=0,sd=0,lo=inf,hi=ninf)

  def mid(i): return i.mu
  def div(i): return i.sd
  def norm(i,x): return x if x=="?" else (x - i.lo) / (i.hi - i.lo + tiny)
  def stats(i,div=False,rnd=2): return round(i.div() if div else i.mid(), rnd)

  def descretize(i,x):
    lo,hi = i.mu - 2*i.sd, i.mu + 2*i.sd
    return int(the.bins*(x - lo)/(hi-lo + tiny))

  def add1(i,x,n):
    i.lo  = min(i.lo, x)
    i.hi  = max(i.hi, x)
    d     = x - i.mu
    i.mu += d/i.n
    i.m2 += d*(x - i.mu)
    i.sd  = 0 if i.n<2 else (i.m2/(i.n - 1))**.5

  def merges(i,bins):
    bins = recrusivelyMergeNeighbors(bins,i)
    for j in range(len(bins)-1): bins[j].hi = bins[j+1].lo
    bins[ 0].lo = ninf
    bins[-1].hi =  inf
    return bins

  def delta(i,j):
    return abs(i.mu - j.mu) / ((i.sd**2/i.n + j.sd**2/j.n)**.5 + tiny)

class SOME(col):
  def slots(i,w=1): return super().slots() | dict(ok=True, w=w, _has=[])

  def add1(i,x,_):
    a, r = i._has, random.random
    if   len(a) < the.Some  : i.ok=False; a += [x]
    elif r() < the.Some/i.n : i.ok=False; a[ int(len(a)*r()) ] = x

  def has(i):
    if not i.ok: i._has=sorted(i._has)
    i.sorted=True
    return i._has

  def same(i,j):
    return i.cliffsDelta(j) and i.bootstrap(j)

  def cliffsDelta(i,j):
    n,x,y = 0,i._has, j._has
    if len(x) > 10*len(y): x = random.choices(x,10*len(y))
    if len(y) > 10*len(x): y = random.choices(y,10*len(x))
    lt,gt = 0,0
    for x1 in x:
      for y1 in y:
        n = n + 1
        if x1 > y1: gt = gt + 1 
        if x1 < y1: lt = lt + 1 
    return abs(lt - gt)/n > the.Cliffs 

  def bootstrap(i,j,conf=.05):
    y0,z0   = i._has, j._has
    x, y, z = NUM(), NUM(), NUM()
    for y1 in y0: x.add(y1); y.add(y1) 
    for z1 in z0: x.add(z1); z.add(z1) 
    yhat    = [y1 - y.mu + x.mu for y1 in y0]
    zhat    = [z1 - z.mu + x.mu for z1 in z0]
    overall = y.delta(z)
    n       = 0
    for _ in range(the.bootstrap):
      ynum = NUM().adds(sample(yhat))
      znum = NUM().adds(sample(zhat))
      if ynum.delta(znum)  > overall: n += 1
    return n / the.bootstrap < conf

#-------------------------------------------------------------------------------
class ROW(obj):
  def slots(i,cells=[]): return dict(cells=cells)
  def better(i,j,data):
    s1, s2, cols, n = 0, 0, data.y, len(data.y)
    for col in cols:
      a,b  = col.norm(i.cells[col.at]), col.norm(j.cells[col.at])
      s1  -= math.exp(col.w * (a - b) / n)
      s2  -= math.exp(col.w * (b - a) / n)
    return s1 / n < s2 / n

#-------------------------------------------------------------------------------
class DATA(obj):
  def slots(i):  return dict(x=[], y=[], cols=[], names=[], rows=[])
  def clone(i,rows=[]):
    d = DATA()
    d.names, d.cols, d.x, d.y = COLS(i.names)
    [d.add(row) for row in rows]
    return d

  def read(i,file):
    with open(file) as fp:
      for line in fp:
        line = re.sub(r'([\n\t\r"\' ]|#.*)', '', line)
        if line:
          i.add(ROW(cells = [coerce(s.strip()) for s in line.split(",")]))
    return i

  def add(i,row):
    if i.x:
      [col.add(row.cells[col.at]) for cols in [i.x, i.y] for col in cols]
      i.rows += [row]
    else:
      i.names, i.cols, i.x, i.y = COLS(row.cells)
    return i

  def stats(i, cols=None, div=False, rnd=2):
    return obj(N=len(i.rows), **{col.txt: col.stats(div=div, rnd=rnd)
                                 for col in (cols or i.y)})

  def betters(i):
    rows = sorted(i.rows, key=cmp2key(lambda r1,r2: r1.better(r2,i)))
    cut  = len(rows) - int(len(rows))**the.min
    best,rest = [],[]
    for j,row in enumerate(rows):
      row.y = j > cut
      (best if j > cut else rest).append(row)
    rest = random.sample(rest, len(best)*the.rest)
    return i.clone(best), i.clone(rest)

#-------------------------------------------------------------------------------
def contrasts(data1,data2):
  data12 = data1.clone(data1.rows + data2.rows)
  for col in data12.x:
    for klass,rows in dict(best=data1.rows, rest=data2.rows).items():
      for row in rows:
        col.bin(row.cells[col.at], klass, row)
    for bin in col.merges(sorted(col.bins.values(),key=lambda b:b.lo)):
      bin.score = want(bin.ys.get("best",0), bin.ys.get("rest",0),
                       len(data1.rows), len(data2.rows))
      yield bin

def want(b,r,B,R):
  b, r = b/(B+tiny), r/(R+tiny)
  match the.want:
    case "plan":   return b**2/(b+r)
    case "watch":  return r**2/(b+r)
    case "xplore": return 1/(b+r)
    case "doubt":  return (b+r)/abs(b - r)

def rules(data1,data2):
  a = sorted((bin for bin in contrasts(data1,data2)),
              reversed=True, key=lambda x:x.score)
  print([x.score for x in a])

#-------------------------------------------------------------------------------
# # Misc Stuff

inf  = 1E60
tiny = 1/inf
ninf = -inf

def sample(a):
  return random.choices(a,k=len(a))

def recrusivelyMergeNeighbors(a, *l):
  b,j = [],0
  while j < len(a):
    now = a[j]
    if j < len(a) - 1:
      if new := now.merged(a[j+1], *l):
        now, j = new, j+1
    b += [now]
    j += 1
  return a if len(a) == len(b) else recrusivelyMergeNeighbors(b, *l)

def entropy(d):
  N = sum((d[k] for k in d))
  return -sum((n/N*math.log(n/N,2) for n in d.values() if n > 0))

def showd(d):
   return "{"+(" ".join([f":{k} {show(v)}" for k,v in sorted(d.items()) if k[0]!="_"]))+"}"

def show(x):
  if callable(x)         : return x.__name__+'()'
  if isinstance(x,float) : return f"{x:.2f}"
  return x

def prin(*l) :  print(*l,end="")
def round2(x):  return round(x, ndigits=2)


def flip(file):
  with open(file) as fp:
    s= fp.read()
    f= lambda m:"\n\n# "+ re.sub("\n","\n# ",m[4].strip("[\s]+"))+"\n"+m[2]+m[1]+"\n"
    return re.sub(
              r'\n(([ \t]*)(def|class)[^\n]+)\n[ \t]*"""([^"]+)[\n]?"""[\s]*\n',f,s)