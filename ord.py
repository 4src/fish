#!/usr/bin/env python3 -B
# <!--- vim: set et sts=2 sw=2 ts=2 : --->
"""
ord: simple multi-objective explanation (using unsupervised discretion)
(c) 2023 Tim Menzies <timm@ieee.org> BSD-2

USAGE:    
  python3 -B ord.py [OPTIONS] [-g ACTIONS]

OPTIONS:  
  -b  --bins   max number of bins = 10  
  -c  --cohen  measure of same = .35  
  -f  --file  data file                 = "../data/auto93.csv"  
  -g  --go    start-up action           = "nothing"  
  -h  --help  show help                 = False
  -s  --seed  random number seed        = 937162211  
  -S  --Some  how may nums to keep      = 256"""

from fileinput import FileInput as file_or_stdin
import random,sys,re
from copy import deepcopy
from ast import literal_eval as literal
from typing import T, Self, TypeVar, Generic, Iterator, List

class obj(object):
  def __init__(i,**d): i.__dict__.update(**d)
  def __repr__(i):
    f=lambda x: x.__name__ if callable(x) else (f"{x:3g}" if isinstance(x,float) else x)
    return "{"+" ".join([f":{k} {f(v)}" for k,v in i.__dict__.items() if k[0] != "_"])+"}"

find_keys_defaults = r"\n\s*-\w+\s*--(\w+)[^=]*=\s*(\S+)"
the = obj(**{m[1]:literal(m[2]) for m in re.finditer(find_keys_defaults,__doc__)})

random.seed(the.seed)
R= random.random
big  = 1E30
#--------------------------------------------------------
def ROW(a)        : return obj(this=ROW, cells=a, cooked=a[:])
def COL(n=0, s=""): return (NUM if s and s[0].isupper() else SYM)(n=n,s=s)
def SYM(n=0, s=""): return obj(this=SYM, at=n, txt=s, n=0, seen={}, most=0, mode=None)
def NUM(n=0, s=""): return obj(this=NUM, at=n, txt=s, n=0, _kept=[], ok=True,
                               heaven= 0 if s and s[-1]=="-" else 1)

def ok(col):
  if col.this is NUM and not col.ok: col._kept.sort(); col.ok=True 
  return col

def COLS(names):
  x,y,all = [], [], [COL(*x) for x in enumerate(names)]
  for col in all:
    if col.txt[-1] != "X":
      (y if col.txt[-1] in "+-!" else x).append(col)
  return obj(this=COLS, x=x, y=y, all=all, names=names)

def DATA(src):
  data = obj(this=DATA, rows=[], cols=None)
  [row2Data(row,data) for row in src]
  return data

def row2Data(row,data):
  def _create(): data.cols  = COLS(row.cells)
  def _update(): data.rows += [row2Cols(row,data.cols)]
  _update() if data.cols else _create()

def row2Cols(row,cols):
  for cols in [cols.x, cols.y]:
    for col in cols:
      x2Col(row.cells[col.at],col)
  return row

def x2Col(x,col):
  def _sym():
    tmp = col.seen[x] = 1 + col.seen.get(x,0)
    if tmp> col.most: col.most,col.mode = tmp,x
  def _num():
    a = col._kept
    if   len(a) < the.Some      : col.ok=False; a  += [x]
    elif R() < the.Some / col.n : col.ok=False; a[int(len(a)*R())] = x
  if x != "?":
    col.n += 1
    _num() if col.this is NUM else _sym()

def chops(data):
  for col in data.cols.x:
    if col.this is SYM:
      col.chops = col.seen.keys()
    else:
      col.chops = chop(ok(col)._kept)
      for row in data.rows:
        x = row.cells[col.at]
        if x != "?":
          row.cooked[col.at] = range4x(col.chops, x)/len(col.chops)
  return data

def range4x(a,x):
  at=1
  for n,y in enumerate(a):
    if y> x: return at-1
    else: at += 1
  return at - 1

def dist(data,row1,row2):
  def _sym(col,a,b):
    return 0 if a==b else 1
  def _num(col,a,b):
    if a=="?" : a=1 if b<.5 else 0
    if b=="?" : b=1 if a<.5 else 0
    return abs(a-b)
  def _col(col):
    a,b = row1.cooked[col.at], rows2.cooked[col.at]
    return a=="?" and b=="?" and 1 or (_num if col.this is NUM else _sym)(col,a,b)
  return sum(map(_col, data.cols.x)) / len(data.cols.x)
#----------------------------------------------------
def chop(a):
  n = inc = int(len(a)/the.bins)
  small   = the.cohen*stdev(a)
  b4,out  = a[0],[]
  while n < len(a) - 1:
    x = a[n]
    if x==a[n+1] or x - b4 < small: n += 1 # keep looking for a cut
    else                          : n += inc; out += [x]; b4=x
  return out

def ent(d):
  N = sum((n for n in d.values()))
  return - sum(( n/N * math.log(n/N,2) for n in d.values() if n>0 ))

def stdev(a): return (per(a,.9) - per(a,.1)) / 2.56
def per(a, p=.5): return a[int(p*len(a))]

def coerce(x:str):
  try:    return literal(x)
  except: return x

def csv(file, filter=ROW):
  with file_or_stdin(None if file =="-" else file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r"\' ]|#.*)', '', line)
      if line:
        yield filter([coerce(s.strip()) for s in line.split(",")])

def cli(d):
  for k,v in d.items():
    v = str(v)
    for j,x in enumerate(sys.argv):
      if ("-"+k[0]) == x or ("--"+k) == x:
        v = "True" if v=="False" else ("False" if v=="True" else sys.argv[j+1])
    d[k] = coerce(v)
  if d["help"]: print(__doc__)
#----------------------------------------------------
def eg1(fun):
  the = deepcopy(EGS.saved)
  random.seed(the.seed)
  failed = fun() == False
  print("❌ FAIL " if failed else "✅ PASS", fun.__name__)
  return failed

class EGS:
  saved = deepcopy(the)
  def run(a=sys.argv) : cli(the.__dict__); getattr(EGS, the.go, EGS.oops)()
  def oops()          : print("??")
  def nothing()       : ...
  def all()           : sys.exit(sum(map(eg1, [EGS.the])))
  #--------------------------------
  def the()  : print(the)
  def data() : d=DATA(csv(the.file)); print(len(d.rows), d.cols.x[3])
  def chop() :
    d=chops(DATA(csv(the.file)))
    for i,row in enumerate(d.rows):
                        print([row.cooked[col.at] for col in d.cols.x])

#----------------------------------------------------

EGS.run()
