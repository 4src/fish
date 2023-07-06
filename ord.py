#!/usr/bin/env python3 -B
# <!--- vim: set et sts=2 sw=2 ts=2 : --->
"""
ORD: simple multi objective explanation (using unsupervised discretion)   
(c) 2023 Tim Menzies <timm@ieee.org> BSD.2

USAGE:    
  ./ord.py [OPTIONS] [-g ACTIONS]

OPTIONS:  
  -b  --bins   max number of bins         = 16  
  -B  --Beam   search width               = 10   
  -c  --cohen  measure of same            = .35  
  -f  --file   data file                  = "../data/auto93.csv"  
  -g  --go     startup action             = "nothing"  
  -h  --help   show help                  = False   
  -m  --min    min size                   = .5   
  -r  --rest   best times rest            = 4   
  -s  --seed   random number seed         = 937162211  
  -S  --Some   how may nums to keep       = 256   
  -w  --want   plan|monitor|xplore|doubt  = "plan""""
#----------------------------------------------------
# def aa4Bb = some function that updated Bb using aa  
# def aa2Bb = some function that conversts aa to Bb  
# def UPPERCASE = constructor     
# xxx (where XXX is a constructor) = instance  
import random,sys,re
from copy import deepcopy
from termcolor import colored
from ast import literal_eval as literal
from fileinput import FileInput as file_or_stdin

class obj(object):
  def __init__(i,**d): i.__dict__.update(**d)
  def __repr__(i):
    f=lambda x: x.__name__ if callable(x) else (f"{x:3g}" if isinstance(x,float) else x)
    return "{"+" ".join([f":{k} {f(v)}" for k,v in i.__dict__.items() if k[0] != "_"])+"}"

keys_and_defaults = r"\n\s*-\w+\s*--(\w+)[^=]*=\s*(\S+)"
the = obj(**{m[1]:literal(m[2]) for m in re.finditer(keys_and_defaults,__doc__)})

random.seed(the.seed)
R= random.random
big  = 1E30
#--------------------------------------------------------
def TEST(col,lo,hi): return obj(this=TEST, at=col.at, txt=col.txt,lo=lo,hi=hi)
def ORS(a): return obj(this=OR, tests=[])
def ANDS(a): return obj(this=OR, ors={})

def ROW(a)        : return obj(this=ROW, cells=a, cooked=a[:])
def COL(n=0, s=""): return (NUM if s and s[0].isupper() else SYM)(n=n,s=s)
def SYM(n=0, s=""): return obj(this=SYM, at=n, txt=s, n=0, seen={}, most=0, mode=None)
def NUM(n=0, s=""): return obj(this=NUM, at=n, txt=s, n=0, _kept=[], ok=True,
                               heaven= 0 if s and s[-1]=="-" else 1)

def COLS(names):
  x,y,all = [], [], [COL(*x) for x in enumerate(names)]
  for col in all:
    if col.txt[-1] != "X":
      (y if col.txt[-1] in "+-!" else x).append(col)
  return obj(this=COLS, x=x, y=y, all=all, names=names)

def DATA(src):
  data = obj(this=DATA, rows=[], cols=None)
  [row4Data(row,data) for row in src]
  return data

def row4Data(row,data):
  def _create(): data.cols  = COLS(row.cells)
  def _update(): data.rows += [row4Cols(row,data.cols)]
  (_update if data.cols else _create)()

def row4Cols(row,cols):
  for cols in [cols.x, cols.y]:
    for col in cols:
      x4Col(row.cells[col.at],col)
  return row

def x4Col(x,col):
  def _sym():
    tmp = col.seen[x] = 1 + col.seen.get(x,0)
    if tmp> col.most: col.most,col.mode = tmp,x
  def _num():
    a = col._kept
    if   len(a) < the.Some      : col.ok=False; a  += [x]
    elif R() < the.Some / col.n : col.ok=False; a[int(len(a)*R())] = x
  if x != "?":
    col.n += 1
    (_num if col.this is NUM else _sym)()

def ok(col):
  if col.this is NUM and not col.ok: col._kept.sort(); col.ok=True 
  return col

def chops(data):
  def _sym(col):
    col.chops = col.seen.keys()
  def _num(col):
    col.chops = chop(ok(col)._kept)
    for row in data.rows:
      x = row.cells[col.at]
      if x != "?":
        row.cooked[col.at] = round(x2range(col.chops, x)/len(col.chops),2)
  for col in data.cols.x:
    (_sym if col.this is SYM else _num)(col)
  return data

def x2range(a,x):
  at=1
  for n,y in enumerate(a):
    if y > x: return at-1
    else: at += 1
  return at - 1

def range2loHi(r,col):
  n= int(len(r*len(col.chops))
  if n=0: return TEST(col, -big,col.chops[0])
  if n>= len(col.chops): return TEST(col, col.chops[-1], big)
  return TEST(col,  col.chops[n-1], col.chops[n])

def selects(x, row):
  def _test(test) : return (_sym if test.lo==test.hi else _num)(test,row[test.at])
  def _num(test,v): return v=="?" or test.lo <= v and v < test.hi
  def _sym(test,v): return v=="?" or v == test.lo
  def _ors(ors):
    for test in ors.tests:
      if _test(test): return True
  def _ands(ands):
    for ors in ands.ors.values():
      if not _ors(ors,row): return False
    return True
  return (_ands if x.this is ANDS else (_ors if x.this is ORS else _tests))(x)

def sortedRows(data):
  def _distance2heaven(row):
    nom = sum(( (col.heaven - row.cooked[col.at])**2 for col in data.cols.y ))
    return (nom/len(data.cols.y))**.5
  return sorted(data.rows, key = _distance2heaven)

def goodIdeas(data, bestRows, restRows):
  def _count():
    d={}
    for klass,rows in [(True,bestRows), (False,restRows)]:
      dk = d[klass] = {}
      for row in rows:
        for col in data.cols.x:
         x = row.cells[col.at]
         if x != "?":
           k = (col.at, col.txt, x)
           dk[k] = 1/len(rows) + dk.get(k,0)
    return d
  def _score(d):
    out = []
    hi  = 0
    for x,best in d[True].items():
      rest = d[False].get(x,0) + 1/big
      v    = score(b,r) 
      hi   = max(hi, v)
      out += [(v,  best, x, rest)]
    return [x for x in out if x[0] > hi/10]
  def _prune(lst):
    return sorted(lst, reverse=True)[:the.Beam]
  return _prune( _score( _count()))

def score(b,r)
  if the.want=="plan"    : return b**2  / (   b + r + 1/big)
  if the.want=="monitor" : return r**2  / (   b + r + 1/big)
  if the.want=="doubt"   : return (b+r) / abs(b - r + 1/big)
  if the.want=="xplore"  : return 1     / (   b + r + 1/big)
# def RULE(ranges):
#   cols={}
#   for v,b,r,x in ranges:
#      
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
  def bright(s): return colored(s[1],"yellow",attrs=["bold"])
  def white(s) : return colored(s[1],"white", attrs=["bold"])
  for k,v in d.items():
    v = str(v)
    for j,x in enumerate(sys.argv):
      if ("-"+k[0]) == x or ("--"+k) == x:
        v = "True" if v=="False" else ("False" if v=="True" else sys.argv[j+1])
    d[k] = coerce(v)
  if d["help"]: print(re.sub(r"(\n[A-Z]+:)",bright,re.sub(r"(-[-]?[\w]+)",white,__doc__)))
#----------------------------------------------------
def eg1(fun):
  the = deepcopy(EGS.saved)
  random.seed(the.seed)
  failed = fun() == False
  print("❌ FAIL " if failed else "✅ PASS", fun.__name__)
  return failed

class EGS:
  saved = deepcopy(the)
  def run(a=sys.argv): cli(the.__dict__); getattr(EGS, the.go, EGS.oops)()
  def oops()         : print("??")
  def nothing()      : ...
  def all()          : sys.exit(sum(map(eg1, [EGS.the])))
  #--------------------------------
  def the()  : print(the)

  def data() : d=DATA(csv(the.file)); print(len(d.rows), d.cols.x[3])

  def chop() :
    d=chops(DATA(csv(the.file)))
    col = d.cols.x[1]
    a  = ok(col)._kept
    #for i,row in enumerate(d.rows): print(row.cells[col.at],row.cooked[ col.at], a[0], a[-1])

  def sorted():
    rows = sortedRows(DATA(csv(the.file)))
    for row in  rows[:5]: print(row.cells)
    print("")
    for row in  rows[-5:]: print(row.cells)

  def good():
    data = DATA(csv(the.file))
    rows = sortedRows(data)
    n = int(len(rows)**the.min)
    bestRows = rows[:n]
    restRows = random.sample( rows[n+1:], n*the.rest )
    for x in goodIdeas(data,bestRows,restRows): print(x)
#----------------------------------------------------

EGS.run()
