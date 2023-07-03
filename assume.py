#!/usr/bin/env python3 -B
#vim: set et sts=2 sw=2 ts=2 : 
from fileinput import FileInput as file_or_stdin
import random,math,sys,re
from functools import cmp_to_key
from ast import literal_eval

big = 1E30

def coerce(x):
  try: return literal_eval(x)
  except: return x

def csv(file):
  "Returns an iterator that returns lists from standard input (-) or a file."
  if file=="-": file=None
  with file_or_stdin(file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r"\' ]|#.*)', '', line)
      if line:
        yield [coerce(s.strip()) for s in line.split(",")]
#--------------------------------------------------------------------
class pretty(object):
  "Objects support pretty print, hiding privates slots (those starting with `_`)"
  def __repr__(i):
    f=lambda x: x.__name__ if callable(x) else (f"{x:3g}" if isinstance(x,float) else x)
    return i.__class__.__name__+"{"+\
           ' '.join([f":{k} {f(v)}" for k,v in i.__dict__.items() if k[0] != "_"])+"}"
#---------------------------------------------
class COL(pretty):
  "COLumns know the name, position and the count of rows seen."
  def __init__(i, txt="",at=0): i.n,i.at,i.txt = 0,at,txt
  def add(i,x):
    "Ignoring empty cells, increment `n` then do the adding."
    if x != "?":
      i.n += 1
      i.add1(x)
    return x
#---------------------------------------------
class NUM(COL):
  "Summarize stream of numbers. Knows the mean and standard deviation."
  def __init__(i, txt="",at=0):
    COL.__init__(i,txt=txt,at=at)
    i.want = 0 if len(i.txt) > 0 and i.txt[-1] == "-" else 1
    i.mu = i.m2 = 0
    i.lo, i.hi = big, -big 
  def add1(i,x):
    "Update `lo,hi` and the variables needed to calculate stdev."
    i.lo = min(x, i.lo)
    i.hi = max(x, i.hi)
    delta = x - i.mu
    i.mu += delta/i.n
    i.m2 += delta*(x - i.mu)
  def norm(i,x):
    "May `x` to 0..1 for `lo` to `hi`."
    return x if x=="?" else  (x-i.lo)/(i.hi - i.lo + 1/big)

#--------------------------------------------------------------------
class SYM(COL):
  "Summary a stream of symbols. Knows mode and entropy."
  def __init__(i,txt="",at=0):
    COL.__init__(i,txt=txt,at=at)
    i.counts,i.mode, i.most = {},None,0
  def add1(i,x):
    "Increment counts and mode."
    now = i.counts[x] = 1 + i.counts.get(x,0)
    if now > i.most: i.most, i.mode = now, x
#--------------------------------------------------------------------
class COLS(pretty):
  "Convert a list of names into NUMs and SYMs (kept different binds of cols in different lists)."
  def __init__(i,names):
    i.x, i.y, i.names = [],[],names
    i.all = [(NUM if s[0].isupper() else SYM)(at=n,txt=s) for n,s in enumerate(names)]
    for col in i.all:
      z = col.txt[-1]
      if z != "X":
        if z=="!": i.klass= col
        (i.y if z in "-+!" else i.x).append(col)
  def add(i,row):
    "Add a row's data to all the non-skipped columns."
    for cols in [i.x, i.y]:
      for col in cols: col.add(row[col.at])
    return row
#--------------------------------------------------------------------
class DATA(pretty):
  "Keep `rows` of data, summarized into col`umns."
  def __init__(i,src=[]):
    i.cols, i.rows = None,[]
    [i.add(row) for row in src]
  def add(i,row):
    "For first row, build the `cols`. Otherwise, update summaries and the rows."
    if i.cols: i.rows += [i.cols.add(row)]
    else:      i.cols = COLS(row)
  def d2h(i,t):
    return (sum(((col.want -  col.norm(t[col.at]))**2 for col in i.cols.y)) /
            len(i.cols.y))**.5
  def sorted(i):
    return sorted(i.rows, key=lambda row: i.d2h(row)) 
#--------------------------------------------------------------------
d = DATA(csv("../data/auto93.csv"))
lst = d.sorted()
[print(x) for x in lst[:10]]; print("")
[print(x) for x in lst[-10:]]



