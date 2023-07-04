#!/usr/bin/env python3 -B
# vim: set et sts=2 sw=2 ts=2 : 
from fileinput import FileInput as file_or_stdin
import random,math,sys,re,os
from copy import deepcopy
from ast import literal_eval
from typing import Self, TypeVar, Generic, Iterator

Atom  = [int | float | str | bool]
class BOX(dict): __getattr__ = dict.get

class public(object):
  def __repr__(i) -> str: 
    return show(i.__dict__, i.__class__.__name__)

the = BOX(some = 512, seed = 1234567891, go="none")

class SYM(public):
  def __init__(i, at:int=0, txt:str="") -> Self:
    i.n,i.has,i.most,i.mode = 0,[],0,None
  def add(i, x:Atom) -> Atom:
    if x != "?":
      i.n += 1
      tmp = i.has[x] = 1 + i.has.get(x,0)
      if tmp > i.most: i.most,i.mode = tmp,x

class SOME(public):
  def __init__(i, at:int=0, txt:str="") -> Self:
    i.at, i.txt, i.want = at, txt, (0 if txt and txt[-1]=="-" else 1)
    i.n,i.ok,i.has = 0,True,[]
  def add(i, x:Atom) -> None:
    if x != "?":
      i.n += 1
      if   len(i.has) < the.some : i.ok=False; i.has += [x]
      elif R() < the.some/i.n    : i.ok=False; i.has[int(len(i.has)*R())] = x
  def ok(i) -> Self:
    if not i.ok: i.has.sort(); i.ok = True
    return i

class ROW(public):
  def __init__(i, a:list[Atom]) -> Self:  
    i.cells, i.cooked = a, a[:]

def COL(at:int=0, txt:str="") -> [SOME | SYM]:
  return (SOME if txt and txt[0].isupper() else SYM)(at,txt)

class COLS(public):
  def __init__(i, names:list[str]) -> Self:
    i.x, i.y, i.names = [],[],names
    i.all = [COL(at,txt) for at,txt in enumerate(txts)]
    for col in i.all:
      if col.txt[-1] != "X": 
       (i.y if col.txt[-1] in "-+" else i.x).append(col)
  def add(i, row:ROW) -> None:
    for cols in  [i.cols.x, i.cols.y]:
      for col in cols:
        col:add(row.cells[col.at])
  def clone(i,rows: list[ROW]=[]) -> Self:
    j = COLS(i.names)
    [j.add(row) for row in rows]
    return j

#--------------------------------------------------------------------
big:float = 1E30
R:callable = random.random

def show(d:dict, pre="") -> str:
  f= lambda x: x.__name__ if callable(x) else (f"{x:3g}" if isinstance(x,float) else x)
  return pre+"{"+' '.join([f":{k} {f(v)}" for k,v in d.items() if k[0] != "_"])+"}"

def coerce(x:str):
  try: return literal_eval(x)
  except: return x

def csv(file:str,fun:callable=ROW) -> Iterator[list[Atom]]:
  "Returns an iterator that returns lists from standard input (-) or a file."
  if file=="-": file=None
  with file_or_stdin(file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r"\' ]|#.*)', '', line)
      if line:
        yield fun([coerce(s.strip()) for s in line.split(",")])

def per(a:list[float], p:float=.5):
  p=int(p*len(a) + .5); return a[max(0,min(len(a)-1,p))] 
# ---------------------------------------------
#print([COL(*x) for x in enumerate(["asdas","Aasda","asdas"])])

class EGS:
  ALL = locals()
  def RUN():
    def good(s)  : print("#passed :",s) # ; return None
    def bad(s,f) : if f()==False: print("#failed :",s); return True
    def reset(s) : the = deepcopy(b4); random.seed(the.seed); print("trying ",s")
    def relevant(s) : 
      if s[0].islower() and (s==the.go or the.go=="all"):  reset(s); return True
    b4 = deepcopy(the)
    sys.exit( sum(((bad(s,f) or good(s)) for txt,fun in EGS.ALL.items() if relevant(txt))))
  def some():
    s=SOME()
    [s.add(x) for x in range(10**6)]
    print(len(s.has))

# class COL(public):
#   "COLumns know the name, position and the count of rows seen."
#   def __init__(i, txt="",at=0): i.n,i.at,i.txt = 0,at,txt
#   def add(i,x:cell) -> cell:
#     "Ignoring empty cells, increment `n` then do the adding."
#     if x != "?":
#       i.n += 1
#       i.add1(x)
#     return x
# #---------------------------------------------
# class NUM(COL):
#   "Summarize stream of numbers. Knows the mean and standard deviation."
#   def __init__(i, txt="",at=0):
#     COL.__init__(i,txt=txt,at=at)
#     i.want = 0 if len(i.txt) > 0 and i.txt[-1] == "-" else 1
#     i.mu = i.m2 = 0
#     i.lo, i.hi = big, -big
#   def add1(i,x:float) -> None:
#     "Update `lo,hi` and the variables needed to calculate stdev."
#     i.lo = min(x, i.lo)
#     i.hi = max(x, i.hi)
#     delta = x - i.mu
#     i.mu += delta/i.n
#     i.m2 += delta*(x - i.mu)
#   def norm(i,x: cell) -> float:
#     "May `x` to 0..1 for `lo` to `hi`."
#     return x if x=="?" else  (x-i.lo)/(i.hi - i.lo + 1/big)
# #--------------------------------------------------------------------
# class SYM(COL):
#   "Summary a stream of symbols. Knows mode and entropy."
#   def __init__(i,txt="",at=0):
#     COL.__init__(i,txt=txt,at=at)
#     i.counts,i.mode, i.most = {},None,0
#   def add1(i,x):
#     "Increment counts and mode."
#     now = i.counts[x] = 1 + i.counts.get(x,0)
#     if now > i.most: i.most, i.mode = now, x
# #--------------------------------------------------------------------
# class COLS(public):
#   "Convert a list of names into NUMs and SYMs (kept different binds of cols in different lists)."
#   def __init__(i,names):
#     i.x, i.y, i.names = [],[],names
#     i.all = [(NUM if s[0].isupper() else SYM)(at=n,txt=s) for n,s in enumerate(names)]
#     for col in i.all:
#       z = col.txt[-1]
#       if z != "X": (i.y if z in "-+!" else i.x).append(col)
#   def add(i,row: record) -> record:
#     "Add a row's data to all the non-skipped columns."
#     for cols in [i.x, i.y]:
#       for col in cols: col.add(row[col.at])
#     return row
# #--------------------------------------------------------------------
# class DATA(public):
#   "Keep `rows` of data, summarized into col`umns."
#   def __init__(i,src=[]):
#     i.cols, i.rows = None,[]
#     [i.add(row) for row in src]
#   def add(i,row:record) -> None:
#     "For first row, build the `cols`. Otherwise, update summaries and the rows."
#     if i.cols: i.rows += [i.cols.add(row)]
#     else:      i.cols = COLS(row)
#   def d2h(i,row:record) -> float:
#     return (sum(((col.want -  col.norm(row[col.at]))**2 for col in i.cols.y)) /
#             len(i.cols.y))**.5
#   def sorted(i) -> list[record]:
#     return sorted(i.rows, key=lambda row: i.d2h(row)) 
# #--------------------------------------------------------------------
# d = DATA(csv("../data/auto93.csv"))
# lst = d.sorted()
# [print(x) for x in lst[:10]]; print("")
# [print(x) for x in lst[-10:]]
# 
# 
# 
