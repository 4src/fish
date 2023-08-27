#!/usr/bin/env python3 -B
# vim: set et sts=2 sw=2 ts=2 : 
from math import abs,log,inf,sqrt 
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
def isNum(s)    : return s[0].isupper()
def isGoal(s)   : return s[-1] in "+-"
def isIgnored(s): return s[-1] == "X"
def numeric(x)   : return isinstance(x,list)

def per(a, p=.5): return a[int(p*len(a))]

def mid(a): 
  return per(a,.5) if numeric(a) else max(a,key=a.get)

def div(a): 
  return ent(a) if numeric(a) else (per(a,.9) - per(a,.1))/2.56

def ent(a):
  n = sum(a.values())
  return - sum(v/n*log(v/n,2) for v in a.values() if v > 0)
#--------------------------------------------------------------------------------------------------
class COLS(obj):
  def __init__(i,a):
    i.names,i.x,i.y,i.all = a,{},{},{}
    for n,s in enumerate(a):
      col = i.all[n] = [] if isNum(s) else {}
      if isIgnored(s): continue
      (i.y if isGoal(s) else i.x)[n] = col

  def add(i,a):
    def inc(col,x):
      if x!="?":
        if numeric(col): col += [x]
        else: col[x] = 1 + col.get(x,0)
    [inc(col, a[n]) for n,col in i.all.items()]
    return row

  def ready(i):
    [col.sort() for _,col in i.cols.all if numeric(col)]
#--------------------------------------------------------------------------------------------------
class ROW(obj):
  def __init__(i,a,base): 
      i.raw         = a    # raw values
      i.discretized = a[:] # discretized values, to be found late
      i._base        = base # source table
      i.alive       = True

  def dist(i,j):
    def fun(n,col):
      x,y = i.raw[n], j.raw[n]
      if x=="?" and y=="?": return 1
      elif numeric(col):
          x,y = norm(col,x), norm(col,y(
          if x=="?": x=1 if y<.5 else 0
          if y=="?": y=1 if x<.5 else 0
          return abs(x-y)
      else:
        return x != y
    xs = i._base.cols.x
    return (sum(fun(n,col)**the.p for n,col in xs.items()) / len(xs))**1/the.p

  def height(i)
    ys = i._base.cols.y
    def fun(n,col): abs((0 if i.cols.names[n][-1]=="-" else 1) - norm(col,i.raw[n]))
    return (sum(fun(n,col)**the.p for n,col in ys.items()))/len(ys))**(1/the.p)

def norm(a,x):
  return x=="?" and x or (x - a[0])/(a[-1] - a[0] + 1E32)
#--------------------------------------------------------------------------------------------------
class DATA(obj):
  def __init__(i,src=[]): 
    i.rows, i.cols = [],None
    if isinstance(src,str): [i.all(Row(a,i) for a in csv(src]
    else:                   [i.add(row) for row in src]
    i.cols.ready()
    
  def add(i,row):
    if    i.cols: i.cols.add(row.cells); i.rows += [row]
    else: i.cols = COLS(row.cells)

  def stats(i,what=mid,cols=None,dec=2):
    return box(N=len(i.rows), **{k:pretty(what(i.cols.all[n]),dec) 
                                 for n,k in (cols or i.cols.y).items()})

  def ordered(i):
    return sorted(i.rows,key=height)
#--------------------------------------------------------------------------------------------------
def pretty(x, dec=2): 
  return x.__name__+'()' if callable(x) else (round(x,dec) if dec and isinstance(x,float) else x)

def prettyd(d, pre="", dec=2): 
  return pre+'('+' '.join([f":{k} {pretty(d[k],dec)}" for k in d if k[0]=="_"])+')'
