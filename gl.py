"""
ESPY: a demonstrator for less is more analytics
(c) Tim Menzies <timm@ieee.org>, BSD.2 license

USAGE:
  import es

EXAMPLES:
  python3 -B eg.py [OPTIONS] [ACTIONS]
  
OPTIONS:
  -b --bins    initial number of bins  = 8
  -c --cohen   small effect size       = .35
  -f --file    csv data file           = "../data/auto93.csv"
  -F --Far     how far to look         = .85
  -H --Halves  where to find for far   = 512
  -h --help    show help               = False
  -m --min     min size                = .5
  -p --p       distance coefficient    = 2
  -s --seed    random number seed      = 1234567891
"""
from ast import literal_eval as this
import fileinput,random,time,ast,re
from collections import Counter
from math import log,inf,sqrt

class obj: 
  def __repr__(i): return prettyd(i.__dict__, i.__class__.__name__)

class box(dict):
  def __repr__(i): return prettyd(i)
  __setattr__ = dict.__setitem__ # instead of d["slot"]=1, allow d.slot=1
  __getattr__ = dict.get         # instead of d["slot"],   allow d.slot  

the=box(**{m[1]:this(m[2]) # create 'the' settings by parsing __doc__ p.
           for m in re.finditer( r"\n\s*-\w+\s*--(\w+).*=\s*(\S+)",__doc__)})
#--------------------------------------------------------------------------------------------------
def isNum(x)     : return isinstance(x,list)
def per(a, p=.5) : return a[int(p*len(a))]


def median(a)   : return per(a,.5)
def mean(a)     : return sum(a)/len(a)
def mid(col)    : return median(col) if isNum(col) else max(col, key=col.get)
def norm(col,x) : return  x=="?" and x or (x - col[0])/(col[-1] - col[0] + 1E-32)
def div(col)    : return (per(col,.9) - per(col,.1))/2.56 if isNum(col) else ent(col)

def ent(d):
  n = sum(d.values())
  return sum( -v/n*log(v/n,2) for v in d.values() if v > 0)

def merged(a,b):
  if a and b:
    n1,n2 = a.total(),b.total()
    c = a+b
    if ent(c) <= (ent(a)*n1 + ent(b)*n2)/(n1+n2): 
      return c
  
def minkowski(cols, fun):
  tmp = sum(fun(n,col)**the.p for n,col in cols.items())
  return (tmp / len(cols))**(1/the.p)

def cuts(n, klasses, supervised=False, get=lambda lst,n: lst[n]):
  xys = sorted([(get(z,n), klass) for klass,lst in klasses.items() for z in lst if get(z,n) !="?"])
  size = len(xys) // (the.bins - 1)
  small = the.cohen * (per(xys,.9)[0] - per(xys,.1)[0])/2.56
  xs, ys, ignore, b4 = {}, {}, set(),  None
  cut=xys[0][0]; xs[cut]=0; ys[cut]=Counter()
  for j,(x,y) in enumerate(xys):
    if (xs[cut] >= size and x - cut >= small and j < len(xys)-size and x != xys[j+1][0]):
      if supervised:
           if combined := merged(ys[b4],ys[cut]):
              ignore.add(cut)
              ys[b4] = combined
           else:
              b4 = cut
      cut=x; xs[cut]=0; ys[cut]=Counter()
    xs[cut] += 1
    ys[cut][y] += 1
  return sorted(xs.keys() - ignore)
#--------------------------------------------------------------------------------------------------
def nump(s)    : return s[0].isupper()
def goalp(s)   : return s[-1] in "+-"
def lessp(s)   : return s[-1] == "-"
def ignorep(s) : return s[-1] == "X"

class COLS(obj):
  def __init__(i,a):
    i.names,i.x,i.y,i.all = a,{},{},{}
    for n,s in enumerate(a):
      col = i.all[n] = [] if nump(s) else {}
      if ignorep(s): continue
      (i.y if goalp(s) else i.x)[n] = col
  def adds(i,a): [i.add(col, a[n]) for n,col in i.all.items()]

  def add(i,col,x):
    if x == "?": return
    if isNum(col): col += [x]
    else: col[x] = 1 + col.get(x,0)

  def sorted(i):[col.sort() for _,col in i.all.items() if isNum(col)]
#------------------------------------------------------------------------------------------------
class ROW(obj):
  def __init__(i,a,data=None): 
    i.raw   = a    # raw values
    i.bins  = a[:] # discretized values, to be calculated later
    i._data = data # source table
    i.alive = True
    i.evalled = False

  def __sub__(i,j):
    def _dist(n,col):
      x,y = i.raw[n],j.raw[n]
      if   x=="?" and y=="?" : return 1
      elif not isNum(col)    : return 0 if x == y else 0
      else:
        x,y = norm(col, x), norm(col,y)
        if x=="?": x=1 if y<.5 else 0
        if y=="?": y=1 if x<.5 else 0
        return abs(x-y)
    return minkowski(i._data.cols.x, _dist)

  def __lt__(i,j): return i.height() < j.height()

  def height(i):
    def _heaven(n):   return 0 if lessp(i._data.cols.names[n]) else 1
    def _dist(n,col): return abs(_heaven(n) - norm(col,i.raw[n]))
    i.evalled = True
    return minkowski(i._data.cols.y, _dist)

  def neighbors(i,rows): return sorted(rows, key=lambda j: j - i)
#--------------------------------------------------------------------------------------------------
class DATA(obj):
  def __init__(i, src=[]):
    i.rows, i.cols = [],None
    i.adds(src)
    i.cols.sorted()

  def adds(i,src):
    if isinstance(src,list): return [i.add(row) for row in src]
    [i.add(ROW(a,i)) for a in csv(src)]
    i.discretize()

  def add(i,row):
    if i.cols:
      i.cols.adds(row.raw)
      i.rows += [row]
    else:
      i.cols = COLS(row.raw)

  def stats(i,what=mid,cols=None,dec=2):
    return box(N=len(i.rows),
               **{i.cols.names[n]:pretty(what(col),dec) 
                  for n,col in (cols or i.cols.y).items()})

  def clone(i,rows=[]): return DATA([ROW(i.cols.names)] + rows)

  def discretize(i):
    if False:
      for n,s in enumerate(i.cols.names):
        if nump(s):
          a = cuts(n, dict(all=i.rows), get=lambda row,n: row.raw[n])
          for row in i.rows:
            old = row.bins[n]
            row.bins[n] = old if old=="?" else discretize(a,old)
#--------------------------------------------------------------------------------------------------
def discretize(cuts,x):
  lo = -inf
  for n,hi in enumerate(cuts):
    if lo <= x < hi: return n
    lo=hi
  return n+1

def bicluster(rows,sort=False):
  n    = len(rows)
  some = random.sample(rows, k=min(n,the.Halves))
  far  = int(the.Far*len(some))
  a    = some[0].neighbors(some)[far]
  b    = a.neighbors(some)[far]
  C    = a - b
  if sort and b < a:  a,b=b,a
  rows = sorted(rows, key=lambda r: ((r-a)**2 + C**2 - (r-b)**2)/(2*C))
  return a,b,rows[:n//2], rows[n//2:]

def tree(rows, sort=False):
  data = rows[0]._data
  stop = len(rows) ** the.min
  def _grow(rows):
    here = box(here=data.clone(rows), left=None, right=None)
    if len(rows) >= 2*stop:
      _,__,lefts,rights = bicluster(rows,sort)
      here.lefts  = _grow(lefts)
      here.rights = _grow(rights)
    return here
  return _grow(rows)

def nodes(tree, depth=0):
  if tree:
    yield tree,depth
    for kid in [tree.lefts, tree.rights]:
      for tree1,depth1 in nodes(kid, depth+1):
        yield tree1,depth1 

def showTree(tree):
  def leaf(node): return not (node.lefts or node.rights)
  stats1 = tree.here.stats()
  depth1 = int(log(len(tree.here.rows)**the.min,2)) 
  prints(*["    "*depth1] + list(stats1.keys()))
  prints(*["    "*depth1] + list(stats1.values()))
  for node,depth in nodes(tree):
    if depth > 0: 
      prints(*["|.. "*depth] + (list(node.here.stats().values()) if leaf(node) else []))
   
#--------------------------------------------------------------------------------------------------
def csv(file="-"):
  with fileinput.FileInput(file) as src:
    for line in src:
      line = re.sub(r'([\t\r"\' ]|#.*)', '', line) 
      if line: yield [coerce(x) for x in line.split(",")]

def coerce(x):
  try : return this(x)
  except Exception: return x.strip()

def pretty(x, dec=2):
  return x.__name__+'()' if callable(x) else (
         round(x,dec) if dec and isinstance(x,float) else x)

def prettyd(d, pre="", dec=2):
  return pre+'('+' '.join([f":{k} {pretty(d[k],dec)}" 
                           for k in d if k[0]!="_"])+')'

def printd(d): print(prettyd(d))
def prints(*a):
  print(*[pretty(x) for x in a],sep="\t")

def printed(*dicts):
  prints(dicts[0].keys())
  [prints(d.values()) for d in dicts]

