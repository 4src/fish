#!/usr/bin/env python3 -B
#vim: set et sts=2 sw=2 ts=2 : 
# https://en.wikipedia.org/wiki/Effect_size#Other_metrics
from fileinput import FileInput as file_or_stdin
import traceback,random,math,sys,re
from termcolor import colored
from functools import cmp_to_key
from ast import literal_eval

class BAG(dict): 
  __getattr__ = dict.get
  __repr__    = lambda i: str({k:i[k] for k in i.__dict__ if not k[0].isupper()})

the=BAG(seed=1234567890, 
        file="../data/auto93.csv")

#----------------------------------------------------------------------------------------
def DATA(data=None,rows=[]):
  data = data or BAG(This=DATA,rows=[],cols=None)
  [adds(data,row) for row in rows]
  return data

def COLS(names):
  x,y,klass,all = [], [], None, [COL(at,txt) for at,txt in enumerate(names)]
  for col in all:
    z= col.txt[-1]
    if z != "X":
      (y if z in "+-!" else x).append(col)
      if z=="!": klass=col
  return BAG(This=COLS, x=x, y=y, names=names, all=all,klass=klass)

def COL(at=0,txt=""):
  return (NUM if txt[0].isupper() else SYM)(at,txt)

def SYM(at,txt):
  return BAG(This=SYM,at=at,txt=txt,n=0, has={},most=0,mode=None)

def NUM(at,txt):
  return BAG(This=NUM, at=at, txt=txt, n=0, mu=0, m2=0,  hi= -1E30, lo=1E30,
             w= 0 if txt[-1]=="-" else 1)
#----------------------------------------------------------------------------------------
def adds(data,row):
  def create(): data.cols  = COLS(row)
  def update(): data.rows += [[add(col,row[col.at]) for col in data.cols.all]]
  update() if data.cols else create()

def add(col,x):
  def num():
    col.lo = min(x, col.lo)
    col.hi = max(x, col.hi)
    d       = x - col.mu
    col.mu += d/col.n
    col.m2 += d*(x - col.mu)
  def sym():
    tmp = col.has[x] = 1 + col.has.get(x,0)
    if tmp > col.most: col.most, col.mode = tmp, x
  if x != "?":
    col.n += 1
    num() if col.This is NUM  else sym()
  return x

def norm(col,x):
  if x=="?" or col.This is SYM: return x
  return (x - col.lo) / (col.hi - col.lo + 1/1E30)

def d2h(data,row):
  return (sum((col.w - norm(col,row[col.at]))**2
            for col in data.cols.y)
             /  len(data.cols.y))*.5

def better(data,row1,row2): return d2h(data,row1) < d2h(data,row2)

def ordered(data,rows=None):
  return sorted(rows or data.rows, key=cmp_to_key(lambda a,b: better(a,b)))

def mid(col): 
  return col.mode if col.This is SYM else col.mu

def div(col):
  log2 = lambda x: math.log(x,2)
  p    = lambda k: col.has[k]/col.n
  return -sum((p(k)*log2(p(k)) for k in d) if col.This is SYM else (col.m2/(col.n - 1))**.5

def stats(data, cols=None, fun=mid):
  tmp = {col.txt: fun(col) for col in (cols or data.cols.y)}
  tmp["N"] = len(data.rows)
  return BAG(**tmp)
#----------------------------------------------------------------------------------------
def coerce(x):
  try: return literal_eval(x)
  except: return x

def csv(file):
  if file=="-": file=None
  with file_or_stdin(file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r"\' ]|#.*)', '', line)
      if line:
        yield [coerce(s.strip()) for s in line.split(",")]
#----------------------------------------------------------------------------------------
class EGS:
  def Rows():
    for row in csv(the.file): print(row)
  def Data():
    print(DATA(rows=csv(the.file)).cols.y)
#----------------------------------------------------------------------------------------
random.seed(the.seed)

EGS.Data()

