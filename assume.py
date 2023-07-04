#!/usr/bin/env python3 -B
# vim: set et sts=2 sw=2 ts=2 : 
"""
assume: reason via pairs of contstraints between c attribites   
(c) 2023 Tim Menzies <timm@ieee.org> BSD-2

USAGE:    
  python3 -B assume.lua [OPTIONS]

OPTIONS:  
  -f  --file    data file                 = "../data/auto93.csv"  
  -g  --go      start-up action           = "nothing"  
  -h  --help    show help                 = False  
  -s  --seed    random number seed        = 937162211  
  -S  --Some    how many numbers to keep  = 512  
"""
from fileinput import FileInput as file_or_stdin
import random,sys,re
from copy import deepcopy
from ast import literal_eval as make
from typing import T, Self, TypeVar, Generic, Iterator, List

Atom  = [int | float | str | bool]
class BOX(dict):
  "A `BOX` is a dictionary that supports `d['slot']` and `d.slot` access."
  __getattr__ = dict.get

the=BOX(**{m[1]:make(m[2]) for m in re.finditer(r"\n\s*-\w+\s*--(\w+)[^=]*=\s*(\S+)",__doc__)})
"""Parse help test to  create a BOX of  `key=default` pairs."""

class obj(object):
  "A class that knows how to pretty print itself."
  def __repr__(i) -> str:
    return show(i.__dict__, i.__class__.__name__)

class SYM(obj):
  "Summarize a stream of symbols."
  def __init__(i, at:int=0, txt:str="") -> Self:
    i.n, i.at, i.txt = 0, at, txt
    i.n,i.has,i.most,i.mode = 0,{},0,None
  def add(i, x:Atom) -> Atom:
    """Update count of thing seen (in `n`); the counts of each thing (in `has`) and the
    most commonly seen thing (in `mode`)."""
    if x != "?":
      i.n += 1
      tmp = i.has[x] = 1 + i.has.get(x,0)
      if tmp > i.most: i.most,i.mode = tmp,x

class NUM(obj):
  "Summarize stream of numbers."
  def __init__(i, at:int=0, txt:str="") -> Self:
    i.n, i.at, i.txt = 0, at, txt
    i.want = 0 if txt and txt[-1]=="-" else 1
    i.mu, i.m2, i.lo, i.hi = 0,0,big, -big
  def add(i, x:Atom) -> None:
    """Update count of thing seen (in `n`); the mean of things seen so far (in `mu`)
    and the second moment (in `m2`) which is need to calculate standard deviation."""
    if x != "?":
      i.n += 1
      i.lo = min(x, i.lo)
      i.hi = max(x, i.hi)
      delta = x - i.mu
      i.mu += delta/i.n
      i.m2 += delta*(x - i.mu)
  def div(i, decimals:[int | None]=None) -> float:
    "Return diversity around the central tendency."
    return rnd((i.m2/(i.n - 1))**.5 if i.m2>0 and i.n > 1 else 0, decimals)
  def mid(i, decimals:[int | None]==None) -> float:
    "Return central tendency."
    return rnd(i.mu, decimals)
  def norm(i,x:[float | str]) -> [float | str]:
    "May `x` to 0..1 for `lo` to `hi`."
    return x if x=="?" else  (x-i.lo)/(i.hi - i.lo + 1/big)

class ROW(obj):
  "Keep a row of data."
  def __init__(i, a:List[Atom]) -> Self: 
    i.cells, i.cooked = a, a[:]
  def d2h(i, ycols:List[NUM]) -> float;
    "Distance to heaven (best performance). Returns 0..1 where _lower_ is _better_"
    return sqrt(sum(((col.want - col.norm(i.cells[col.at]))**2 for col in ycols)) / len(ycols))

def COL(at:int=0, txt:str="") -> [NUM | SYM]:
  "Factory. returns `NUM`s if name is upper case. Else return `SYM`."
  return (NUM if txt and txt[0].isupper() else SYM)(at,txt)

class COLS(obj):
  """Maintain a list of `NUM`s and `SYM`s (in `all`). Remember which are dependent `x` 
    columns or dependent `y` columns. Ignore colums with names ending in `X`"""
  def __init__(i, names:List[str]) -> Self:
    i.x, i.y, i.names = [],[],names
    i.all = [COL(at,txt) for at,txt in enumerate(names)]
    for col in i.all:
      if col.txt[-1] != "X":
        (i.y if col.txt[-1] in "-+" else i.x).append(col)
  def add(i, row:ROW) -> None:
    "Update the independent and dependent columns from `row`."
    for cols in  [i.x, i.y]:
      for col in cols:
        col.add(row.cells[col.at])
  def clone(i, rows: List[ROW] = []) -> Self: 
    "Return a `COLS` with the same structure as `i`. Optionally, add in some rows."
    return adds(COLS(i.names), rows)
  def sort(i,rows: List[ROW]):
    return sorted(rows, key=lambda row: row.d2h(i.y))

# the usual suspects
class DATA(obj):
  def __init__(i,rows=[]):
    i.rows=[], i.cols=None
    adds(i, rows)
  def add(i,row)
    if not cols: cols=COLS(row.cells)
    else:  cols.add(row)
#--------------------------------------------------------------------
big:float = 1E30
R:callable = random.random

def adds(i, a:List=[]) -> T:
  "Add everything in `a` into `i. Return `i`."
  [i.add(x) for x in a]
  return i

def show(d:dict, pre:str="") -> str:
  "Show `d`, shortening decimals on floats and  just printing function nams."
  f= lambda x: x.__name__ if callable(x) else (f"{x:3g}" if isinstance(x,float) else x)
  return pre+"{"+' '.join([f":{k} {f(v)}" for k,v in d.items() if k[0] != "_"])+"}"

def coerce(x:str):
  try: return make(x)
  except: return x

def csv(file:str,fun:callable=ROW) -> Iterator[List[Atom]]:
  "Returns an iterator that returns lists from standard input (-) or a file."
  if file=="-": file=None
  with file_or_stdin(file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r"\' ]|#.*)', '', line)
      if line:
        yield fun([coerce(s.strip()) for s in line.split(",")])

def per(a:List[float], p:float=.5):
  p=int(p*len(a) + .5); return a[max(0,min(len(a)-1,p))] 

def cli(d:dict, help: str) -> dict:
  """For k,v in i, update `v` if there is a command-line flag `-k[0]` or `--k`. Note
  that boolean values need no argument (since we will just negate `v`)."""
  for k,v in d.items():
    v = str(v)
    for j,x in enumerate(sys.argv):
      if ("-"+k[0]) == x or ("--"+k) == x:
        v = "True" if v=="False" else ("False" if v=="True" else sys.argv[j+1])
    d[k] = coerce(v)
  if d.help: print(help)
  return d
#--------------------------------------------------------------------
class EGS:
  """Stored examples as function starting in a lower case letter. If an example returns `False`
  then that will add one to a count of failed examples."""
  All = locals()
  def Failures(the:dict) -> int:
    """Return a count of how often any example fails (indicated by returning False).
    When running any example, first reset globals and random seed to default values."""
    def reset()     : the.update(**b4); random.seed(the.seed); return True
    def relevant(s) : return s[0].islower() and (the.go==s or the.go=="all") and reset()
    def bad(s,fail) : print("#❌ failed:" if fail else "#✅ passed:",s); return fail
    #----------------------------------
    b4 = deepcopy(the)
    return sum((bad(s, fun()==False) for s,fun in EGS.All.items() if relevant(s) ))

  def some() -> [None | bool]:
    n=adds(NUM(), range(10**6))
    print(n.mu)

  def main() -> [None | bool]:
    cols=None
    for row in csv(the.file):
      if not cols: cols=COLS(row.cells)
      else:  cols.add(row)
    print(cols.x[1])

  def sort() -> [None | bool]:
    cols=None
    for row in csv(the.file):
      if not cols: cols=COLS(row.cells)
      else:  cols.add(row)
    print(cols.x[1])

if __name__== "__main__": 
  sys.exit(                 # return failure count to the operating system
    EGS.Failures(           # run some (or all) or the eamples
        cli(the, __doc__))) # update the settings from the command line
