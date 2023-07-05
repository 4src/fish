#!/usr/bin/env python3 -B
from fileinput import FileInput as file_or_stdin
import random,sys,re
from copy import deepcopy
from ast import literal_eval as literal
from typing import T, Self, TypeVar, Generic, Iterator, List

R= random.random

class obj(object):
  def __init__(i,**d): i.__dict__.update(**d)
  def __repr__(i):
    f=lambda x: x.__name__ if callable(x) else (f"{x:3g}" if isinstance(x,float) else x)
    d=i.__dict__
    return "{"+" ".join([f":{k} {f(d[k])}" for k in d if  k[0] != "_"])+"}"

the = obj(seed = 1234567891,
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
def ROW(a)        : return obj(this=ROW, cells=a, cooked=a[:])
def NUM(n=0, s=""): return obj(this=NUM, at=n, txt=s, n=0, _kept=[], ok=True)
def SYM(n=0, s=""): return obj(this=SYM, at=n, txt=s, n=0, seen={})
def COL(n=0, s=""): return (NUM if s and s[0].isupper() else SYM)(n=n,s=s)
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
  def _num():
    a = col._kept
    if   len(a) < the.some      : col.ok=False; a  += [x]
    elif R() < the.some / col.n : col.ok=False; a[int(len(a)*R())] = x
  def _sym():
    col.seen[x] = 1 + col.seen.get(x,0)
  if x != "?":
    col.n += 1
    _num() if col.this is NUM else _sym()

def discretize(col,data):
  def _sym(): return i.seen.keys()
  def _num(): return chop(ok(col)._kept)
  col.chops = _sym() if col.this is SYM else _num()
  for row in data.rows:
    old = row.cells[col.at]
    if old != "?":
      new = rows.coooked[col.at] = old if col.this is SYM else bisect(col.shops,old)

def range4x(a,x):
  at=1
  for n,y in enumerate(a):
    if y> x: return at-1
    else: at+= 1
  return at - 1

for x in [9,11,19,20,21,29,30,31]:
  print(x,range4x([10,20,30],x))

# ## have to handle the symolucs too
# def discretize(col):
#   for col in cols:
#     if col.this is NUM:
#       col.chops = chop( ok(col)._kept )
#       for row in data.rows:
#         old = row.cells[col.at]
#         if old != "?":
#           at = rows.cooked[col.at] = bisect(col.chops, old)
#           tmp.add(at)
#
# def ok(col):
#   if col.this is NUM and not col.ok: col._kept.sort(); col.ok=True 
#   return col
#
#
# def discretizes(data):
#   cols = [col for col in data.cols.x if col.this is NUM]
#   for col in cols:
#     if col.this is NUM:
#       col.chops = chop( ok(col)._kept )
#       for row in data.rows:
#         old = row.cells[col.at]
#         if old != "?":
#           at = rows.cooked[col.at] = bisect(col.chops, old)
#           tmp.add(at)
#----------------------------
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

#d=DATA(csv(the.file))

#print(d.cols.x[3])
