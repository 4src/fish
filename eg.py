#!/usr/bin/env python3 -B
# vim: set et sts=2 sw=2 ts=2 : 
from math import log,inf,sqrt 
import fileinput,random,time,ast,re

class obj: 
  def __repr__(i): return prettyd(i.__dict__, i.__class__.__name__)

class box(dict):
  def __repr__(i): return prettyd(i)
  __setattr__ = dict.__setitem__ # instead of d["slot"]=1, allow d.slot=1
  __getattr__ = dict.get         # instead of d["slot"],   allow d.slot  
#--------------------------------------------------------------------------------------------------
the = box(p     =  2,  # coeffecient on distance calculation 
          cohen = .35) # "difference" means more than .35*std 

def csv(file="-", filter=lambda a:ROW(a)):
  with fileinput.FileInput(file) as src:
    for line in src:
      line = re.sub(r'([\t\r"\' ]|#.*)', '', line) # delete spaces and comments
      if line: yield filter([str2thing(x) for x in line.split(",")])

def str2thing(x):
  try : return ast.literal_eval(x)
  except Exception: return x.strip()
#--------------------------------------------------------------------------------------------------
def numString(s)    : return s[0].isupper()
def goalString(s)   : return s[-1] in "+-"
def lessString(s)   : return s[-1] == "-"
def ignoreString(s) : return s[-1] == "X"
def isNum(x)        : return isinstance(x,list)

def per(a, p=.5): return a[int(p*len(a))]

def mid(a): 
  return per(a,.5) if isNum(a) else max(a, key=a.get)

def div(a): 
  return (per(a,.9) - per(a,.1))/2.56 if isNum(a) else ent(a)

def ent(a):
  n = sum(a.values())
  return - sum(v/n*log(v/n,2) for v in a.values() if v > 0)

def norm(col,x):
  lo,hi = col[0], col[-1]
  return x=="?" and x or (x - lo)/(hi - lo + 1E-32)

def dist(cols, fun):
  tmp = sum(fun(n,col)**the.p for n,col in cols.items())
  return (tmp / len(cols))**1/the.p
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
      i.raw         = a    # raw values
      i.discretized = a[:] # discretized values, to be found late
      i._data       = data # source table
      i.alive       = True

  def __lt__(i,j):
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

  def height(i):
    def heaven(n): return 0 if lessString(i._data.cols.names[n]) else 1
    def dist1(n,col): abs(heaven(n) - norm(col,i.raw[n]))
    return dist(i._data.cols.y, dist1)
#--------------------------------------------------------------------------------------------------
class DATA(obj):
  def __init__(i, src=[]): 
    i.rows, i.cols = [],None
    i.adds(src)
    i.cols.sorted()
    
  def adds(i,src):
    if isinstance(src,str): [i.add(Row(a,i)) for a in csv(src)]
    else:                   [i.add(row)      for row in src]

  def add(i,row):
    if i.cols: 
      i.cols.adds(row.cells)
      i.rows += [row]
    else: 
      i.cols = COLS(row.cells)

  def stats(i,what=mid,cols=None,dec=2):
    return box(N=len(i.rows), **{i.cols.names[n] : pretty(what(col),dec) 
                                 for n,col in (cols or i.cols.y).items()})

  def clone(i,rows=[]):
    return DATA([i.cols.names] + rows)

  def heights(i):
    return sorted(i.rows, key=lambda row: row.height())
#--------------------------------------------------------------------------------------------------
def pretty(x, dec=2): 
  return x.__name__+'()' if callable(x) else (round(x,dec) if dec and isinstance(x,float) else x)

def prettyd(d, pre="", dec=2): 
  return pre+'('+' '.join([f":{k} {pretty(d[k],dec)}" for k in d if k[0]=="_"])+')'

def prints(*lst): 
  print(*[pretty(x) for x in lst],sep="\t")

def printed(*dicts):
  prints(dicts[0].keys())
  [prints(d.values()) for d in dicts]

