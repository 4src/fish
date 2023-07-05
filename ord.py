#!/usr/bin/env python3 -B
from fileinput import FileInput as file_or_stdin
import random,sys,re
from copy import deepcopy
from ast import literal_eval as literal
from typing import T, Self, TypeVar, Generic, Iterator, List

R= random.random

class BOX(object):
  def __init__(i,**d): i.__dict__.update(**d)
  def __repr__(i):
    f=lambda x: x.__name__ if callable(x) else (f"{x:3g}" if isinstance(x,float) else x)
    d=i.__dict__
    return "{"+" ".join([f":{k} {f(d[k])}" for k in d if  k[0] != "_"])+"}"

the = BOX(seed = 1234567891,
          min  = .5,
          cohen = .35,
          bins = 7,
          rest = 3,
          some = 256,
          beam = 10,
          file = "../data/auto93.csv")

random.seed(the.seed)
inf  = 1E30
ninf = -inf
#--------------------------------------------------------
def ROW(a)           : return BOX(this=ROW, cells=a, cooked=a[:])
def NUM(at=0, txt=""): return BOX(this=NUM, at=at, txt=txt, n=0, _kept=[], ok=True)
def SYM(at=0, txt=""): return BOX(this=SYM, at=at, txt=txt, n=0, seen={})
def COL(at=0, txt=""): return (NUM if txt and txt[0].isupper() else SYM)(at=at,txt=txt)
def COLS(names):
  x,y,all = [], [], [COL(at=n,txt=s) for n,s in enumerate(names)]
  for col in all:
    if col.txt[-1] != "X":
      (y if col.txt[-1] in "+-!" else x).append(col)
  return BOX(this=COLS, x=x, y=y, all=all)

def cols1(cols,row):
  for cols in [cols.x, cols.y]
    for col in cols:
      col1(col, row.cells[col.at])
  return row

def DATA(src):
  data = BOX(this=DATA, rows=[], cols=None)
  [data1(data,row) for row in src]
  return data

def data1(data,row)
  def _create(): data.cols  = COLS(row.cells)
  def _update(): data.rows += [cols1(data.cols, row)]
  _update() if data.cols else _create()

def ok(col):
  if col.this is NUM and not col.ok: col._kept.sort(); col.ok=True 
  return col

def col1(col,x):
  def _num():
    a = col._kept
    if   len(a) < the.some      : col.ok=False; a  += [x]
    elif R() < the.some / col.n : col.ok=False; a[int(len(a)*R())] = x
  def _sym():
    col.seen[x] = 1 + col.seen.get(x,0)
  if x != "?":
    col.n += 1
    _num() if col.this is NUM else _sym()

## have to handle the symolucs too
def discretize(col):
  for col in cols:
    if col.this is NUM:
      col.chops = chop( ok(col)._kept )
      for row in data.rows:
        old = row.cells[col.at]
        if old != "?":
          at = rows.cooked[col.at] = bisect(col.chops, old)
          tmp.add(at)
  _

def discretizes(data):
  cols = [col for col in data.cols.x if col.this is NUM]
  for col in cols:
    if col.this is NUM:
      col.chops = chop( ok(col)._kept )
      for row in data.rows:
        old = row.cells[col.at]
        if old != "?":
          at = rows.cooked[col.at] = bisect(col.chops, old)
          tmp.add(at)
#----------------------------
def bisect(a, x):
  lo,hi = 0,len(a)
  if x  < lo: return 0
  if x >= hi: return len(a) + 1
  while lo < hi:
    mid = (lo + hi) // 2
    if a[mid] < x: lo = mid + 1
    else: hi = mid
  return lo

def chop(a):
  inc = int(len(a)/the.bins)
  n, cuts, enough  = inc, [], the.cohen*stdev(a)
  b4 = a[0]
  while n < len(a) - inc - 1:
    x = a[n]
    if  x==a[n+1] or x - b4 < enough:  n += 1
    else: b4=x; n += inc; cuts += [x]
  return cuts

def ent(d):
  N = sum((n for n in d.values()))
  return - sum(( n/N * math.log(n/N,2) for n in d.values() of n>0 ))

1def stdev(a): return (per(a,.9) - per(a,.1)) / 2.56
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

d=DATA(csv(the.file))

print(d.cols.x[3])
