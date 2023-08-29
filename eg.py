"""
eg: a demonstrator for less is more analytics
(c) Tim Menzies <timm@ieee.org>, BSD-2 license

OPTIONS:
  -b --bins        initial number of bins = 8
  -f --file        csv data file          = "../data/auto93.csv"
  -F --Far         how far to look        = .85
  -H --Halves      where to find for far  = 512
  -m --min         min size               = .5
  -p --p           distance coefficient   = 2
  -s --seed        random number seed     = 1234567891
"""
from math import log,inf,sqrt 
import fileinput,random,time,ast,re
from ast import literal_eval as literal
from contextlib import contextmanager
from collections import Counter

class obj: 
  def __repr__(i): return prettyd(i.__dict__, i.__class__.__name__)

class box(dict):
  def __repr__(i): return prettyd(i)
  __setattr__ = dict.__setitem__ # instead of d["slot"]=1, allow d.slot=1
  __getattr__ = dict.get         # instead of d["slot"],   allow d.slot  

the=box(**{m[1]:literal(m[2]) for m in re.finditer( r"\n\s*-\w+\s*--(\w+).*=\s*(\S+)",__doc__)})
#--------------------------------------------------------------------------------------------------
def numString(s)    : return s[0].isupper()
def goalString(s)   : return s[-1] in "+-"
def lessString(s)   : return s[-1] == "-"
def ignoreString(s) : return s[-1] == "X"
def isNum(x)        : return isinstance(x,list)

def per(lst, p=.5): return lst[int(p*len(lst))]

def mid(col):
  return per(col,.5) if isNum(col) else max(col, key=a.get)

def div(col):
  return (per(col,.9) - per(col,.1))/2.56 if isNum(col) else ent(col)

def ent(d):
  n = sum(d.values())
  return sum( -v/n*log(v/n,2) for v in d.values() if v > 0)

def merged(a,b):
  if a and b:
    n1,n2 = a.total(),b.total()
    c = a+b
    if ent(c) <= (ent(a)*n1 + ent(b)*n2)/(n1+n2): 
      return c

def norm(col,x):
  lo,hi = col[0],col[-1]
  return x=="?" and x or (x - lo)/(hi - lo + 1E-32)

def dist(cols, fun):
  tmp = sum(fun(n,col)**the.p for n,col in cols.items())
  return (tmp / len(cols))**1/the.p

def cuts(n,klasses,supervised=False):
  xys   = sorted([(r.raw[n],y) for y,rows in klasses.items() for r in rows if r.raw[n] !="?"])
  size  = len(xys) // (the.bins - 1)
  small = the.cohen * (per(xys,.9)[0] - per(xys,.1)[0])/2.56
  xs,y,last = {},{},None
  cut=xys[0][0]; xs[cut]=0; ys[cut]=Counter()
  ignore = set()
  for j,(x,y) in enumerate(xys):
    if xs[cut] >= size and x - cut >= small and j < len(xys)-size and x != xys[j+1][0]:
      if supervised:
        if combined := merged(ys[last],ys[cut]):
          ignore.add(cut)
          ys[last] = combined
        else:
          last = cut
      cut=x; xs[cut]=0; ys[cut]=Counter()
    xs[cut] += 1
    ys[cut][y] += 1
  return sorted(xs.keys - ignore)
#--------------------------------------------------------------------------------------------------
class COLS(obj):
  def __init__(i,a):
    i.names,i.x,i.y,i.all = a,{},{},{}
    for n,s in enumerate(a):
      col = i.all[n] = [] if numString(s) else {}
      if ignoreString(s): continue
      (i.y if goalString(s) else i.x)[n] = col

  def adds(i,a):
    [i.add(col, a[n]) for n,col in i.all.items()]

  def add(i,col,x):
    if x == "?": return
    if isNum(col): col += [x]
    else: col[x] = 1 + col.get(x,0)

  def sorted(i):
    [col.sort() for _,col in i.cols.all if isNum(col)]
#--------------------------------------------------------------------------------------------------
class ROW(obj):
  def __init__(i,a,data): 
    i.raw   = a    # raw values
    i.bins  = a[:] # discretized values, to be calculated later
    i._data = data # source table
    i.alive = True
    i.evalled = False

  def __sub__(i,j):
    def dist1(n,col):
      x,y = i.raw[n],j.raw[n]
      if   x=="?" and y=="?" : return 1
      elif not isNum(col)    : return 0 if x == y else 0
      else:
        x,y = norm(col, x), norm(col,x)
        if x=="?": x=1 if y<.5 else 0
        if y=="?": y=1 if x<.5 else 0
        return abs(x-y)
    return dist(i._data.cols.x, dist1)

  def __lt__(i,j):
    return i.height() < j.height()

  def height(i):
    def heaven(n): return 0 if lessString(i._data.cols.names[n]) else 1
    def dist1(n,col): abs(heaven(n) - norm(col,i.raw[n]))
    i.evalled = True
    return dist(i._data.cols.y, dist1)

  def far(i,rows):
    return sorted(rows,key=lambda j: j - i)[int(the.Far*len(rows))]

  def twoFar(i,rows):
    x = i.far(rows)
    y = x.far(rows)
    return x,y, x - y
#--------------------------------------------------------------------------------------------------
class DATA(obj):
  def __init__(i, src=[]):
    i.rows, i.cols = [],None
    i.adds(src)
    i.cols.sorted()

  def adds(i,src):
    if isinstance(src,str): [i.add(Row(a,i)) for a in csv(src)]; self.discretize()
    else:                   [i.add(row)      for row in src]

  def add(i,row):
    if i.cols:
      i.cols.adds(row.cells)
      i.rows += [row]
    else:
      i.cols = COLS(row.cells)

  def stats(i,what=mid,cols=None,dec=2):
    return box(N=len(i.rows),
               **{i.cols.names[n]:pretty(what(col),dec) for n,col in (cols or i.cols.y).items()})

  def clone(i,rows=[]):
    return DATA([i.cols.names] + rows)

  def bicluster(i,rows,sort=False):
    n = len(rows)
    some  = rows if n <= the.Halves else random.sample(rows, k=the.Halves)
    a,b,C = random.choice(some).twoFar(some)
    if sort and b < a:  a,b=b,a
    rows = sorted(rows, key= lambda r: ((r-a)**2 + C**2 - (r-b)**2)/(2*C))
    return a,b,rows[:n//2], rows[n//2:]

  def discretize(i):
    for n,s in enumerate(i.cols.names):
      if numericString(s):
        lst = cuts(n,dist(all=i.rows))
        for row in i.rows:
          old = row.bins[n]
          row.bins[n] = old if old=="?" else discretize(lst,old)

def discretize(cuts,x):
  lo = -inf
  for n,hi in enumerate(cuts):
    if lo <= x < hi: return n
    lo=hi
  return n+1
#--------------------------------------------------------------------------------------------------
def csv(file="-"):
  with fileinput.FileInput(file) as src:
    for line in src:
      line = re.sub(r'([\t\r"\' ]|#.*)', '', line) # delete spaces and comments
      if line: yield [coerce(x) for x in line.split(",")]

def coerce(x):
  try : return literal(x)
  except Exception: return x.strip()

def pretty(x, dec=2):
  return x.__name__+'()' if callable(x) else (round(x,dec) if dec and isinstance(x,float) else x)

def prettyd(d, pre="", dec=2):
  return pre+'('+' '.join([f":{k} {pretty(d[k],dec)}" for k in d if k[0]!="_"])+')'

def prints(*lst):
  print(*[pretty(x) for x in lst],sep="\t")

def printed(*dicts):
  prints(dicts[0].keys())
  [prints(d.values()) for d in dicts]


