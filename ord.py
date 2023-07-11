#!/usr/bin/env python3 -B
# <!--- vim: set et sts=2 sw=2 ts=2 : --->
"""
ORD: simple multi objective explanation (using unsupervised discretion)   
(c) 2023 Tim Menzies <timm@ieee.org> BSD.2

USAGE:    
  ./ord.py [OPTIONS] [-g ACTIONS]

OPTIONS:  
  -b  --bins   max number of bins         = 7  
  -B  --Beam   search width               = 10   
  -c  --cohen  measure of same            = .35  
  -f  --file   data file                  = "../data/auto93.csv"  
  -g  --go     startup action             = "nothing"  
  -h  --help   show help                  = False   
  -m  --min    min size                   = .5   
  -r  --rest   best times rest            = 4   
  -s  --seed   random number seed         = 937162211  
  -S  --Some   how may nums to keep       = 256   
  -w  --want   plan|monitor|xplore|doubt  = "plan"
"""
#----------------------------------------------------
# def aa4Bb = some function that updated Bb using aa  
# def aa2Bb = some function that conversts aa to Bb  
# def UPPERCASE = constructor   ; e.g. def ROW  
# xxx (where XXX is a constructor) = an instance of XXX ; e.g. row isa ROW
# xxxs = a list of xxx. eg. rows= list of ROW
import random,sys,re
from copy import deepcopy
from termcolor import colored
from ast import literal_eval as literal
from fileinput import FileInput as file_or_stdin

class obj(object):
  def __init__(i,**d): i.it.update(**d)
  @property
  def it(i): return i.__dict__
  def __repr__(i):
    f=lambda x:x.__name__ if callable(x) else (f"{x:3g}" if isinstance(x,float) else x)
    return "{"+" ".join([f":{k} {f(v)}" for k,v in i.it.items() if k[0] != "_"])+"}"

key_values = r"\n\s*-\w+\s*--(\w+).*=\s*(\S+)"
the = obj(**{m[1]:literal(m[2]) for m in re.finditer(key_values,__doc__)})

random.seed(the.seed)
prints = lambda a: print(*a,sep="\t")
R= random.random
big  = 1E30
#--------------------------------------------------------
def score(b,r,B,R):
  b = b/(B+1/big)
  r = r/(R+1/big)
  if the.want=="plan"    : return b**2  / (   b + r)
  if the.want=="monitor" : return r**2  / (   b + r)
  if the.want=="doubt"   : return (b+r) / abs(b - r)
  if the.want=="xplore"  : return 1     / (   b + r)

def within(x,lo,hi): return lo <= x < hi
#--------------------------------------------------------
def COL(n=0, s=""):
  return (NUM if s and s[0].isupper() else SYM)(n=n,s=s)

class ROW(obj):
  def __init__(i,a):
    i.this=ROW; i.cells=a;  i.cooked=a[:]

class SYM(obj):
  def __init__(i,n=0,s="") :
    i.this=SYM; i.at=n; i.txt=s; i.n=0; i.seen={}; i.most=0; i.mode=None

class NUM(obj):
  def __init__(i, n=0, s="") :
    i.this=NUM;i.at=n; i.txt=s; i.n=0; i._kept=[]; i.ok=True; i.heaven= 0 if s and s[-1]=="-" else 1

class COLS(obj):
  def __init__(i,names):
    i.x,i.y,i.names, i.klass =  [], [], names, None
    i.all = [COL(*x) for x in enumerate(names)]
    for col in i.all:
      z = col.txt[-1]
      if z == "!": i.klass = col
      if z != "X": (i.y if z in "+-!" else i.x).append(col)

def DATA(src):
  data = obj(this=DATA, rows=[], cols=None)
  [row4Data(row,data) for row in src]
  return data

def clone(data,rows=[]):
  out=DATA([ROW(data.cols.names)])
  [row4Data(row,out) for row in rows]
  return out

def row4Data(row,data):
  def _create(): data.cols  = COLS(row.cells)
  def _update(): data.rows += [row4Cols(row,data.cols)]
  _update() if data.cols else _create()

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

def colIsOk(col):
  if col.this is NUM and not col.ok: col._kept.sort(); col.ok=True
  return col

def col2mid(col, decimals=None):
  return col.mode if col.this is SYM else rnd(median(colIsOk(col)._kept), decimals)

def col2div(col, decimals=None):
  return rnd(ent(col.seen) if col.this is SYM else stdev(colIsOk(col)._kept),
             decimals)

def data2stats(data,cols=None,fun=col2mid,decimals=3):
  return obj(N=len(data.rows), **{col.txt: fun(col,decimals) for col in (cols or data.cols.y)})

def sortedRows(data):
  def _distance2heaven(row):
    nom = sum(( (col.heaven - row.cooked[col.at])**2 for col in data.cols.y ))
    return (nom/len(data.cols.y))**.5
  return sorted(data.rows, key = _distance2heaven)
#----------------------------------------------------
# pass1: over all values
# pass2ab: counts for best.rest
# pass3: merge using entropy
def num2Chops(num,bestRows,restRows,cohen,bins):
  def x(row)  : return row.cells[num.at]
  def x1(pair): return x(pair[1])
  def _divide(pairs):
    few = int(len(pairs)/bins) - 1
    tiny= cohen*col2div(num)
    now = obj(lo=x1(pairs[0]), hi=x1(pairs[0]), n=it(best=0, rest=0))
    tmp = [now]
    for i,(klass,row) in enumerate(pairs):
      here = x(row);
      if len(pairs) - i > few *.67 and here != x1(pairs[i-1]):
        if here - now.lo > tiny and now.n.best + now.n.rest > few:
          now  = obj(lo=now.hi, hi=here, n=it(best=0,rest=0))
          tmp += [now]
      now.hi = here
      now.n[klass] += 1
    return tmp
  def _merge(ins):
    outs,i = [],0
    while i < len(ins):
      a = ins[i]
      if i < len(ins)-1:
        b = ins[i+1]
        merged = obj(lo=a.lo, hi=b.hi, n=it(best=a.n.best+b.n.best, rest=a.n.rest+b.n.rest))
        na, nb = a.n.best+a.n.rest, b.n.best+b.n.rest
        if ent(merged.n) <= (ent(a.n)*na + ent(b.n)*nb) / (na+nb): # merged's is clearer than a or b
          a  = merged
          i += 1 # skip over b since we have just merged it with a
      outs += [a]
      i   += 1
    return ins if len(ins) == len(outs) else _merge(outs) 
  bests  = [("best",row) for row in bestRows if x(row) != "?"]
  rests  = [("rest",row) for row in restRows if x(row) != "?"]
  B,R    = len(bestRows) + 1/big, len(restRows)+1/big 
  tmp    = [[x.lo, x.hi, x.n.b/B, x.n.r/R] for x in _merge( _divide( sorted(bests+rests, key=x1)))]
  tmp[ 0][0] = -big # lowest lo is negative infinity
  tmp[-1][1] =  big # highest hi is positive infinity
  return {rnd2(k/(len(out)-1)): tuple(lohi) for k,lohi in enumerate(tmp)}

def cols2Chops(data):
  def _sym(col):
    col.chops = {k:(k,k) for k in col.seen.keys()}
  def _num(col):
    col.chops = num2Chops(col/2,colIsOk(col)._kept, the.cohen, the.bins)
    for row in data.rows:
      row.cooked[col.at] = x2range(row.cells[col.at], col.chops)
  for col in data.cols.x:
    (_sym if col.this is SYM else _num)(col)
  return data

def sortedChops(data, bestRows, restRows):
  def _count():
    d={}
    for klass,rows in [(True,bestRows), (False,restRows)]:
      dk = d[klass] = {}
      for row in rows:
        for col in data.cols.x:
         x = row.cooked[col.at]
         if x != "?":
           k = (col.at, col.txt, x)
           dk[k] = 1 + dk.get(k,0)
    return d
  def _score(d):
    out = []
    hi  = 0
    for x,best in d[True].items():
      rest = d[False].get(x,0) + 1/big
      v    = score(best,rest,len(bestRows), len(restRows))
      hi   = max(hi, v)
      out += [(rnd3(v),  rnd3(best), rnd3(rest), x)]
    return [x for x in out if x[0] > hi/10]
  return sorted( _score( _count()), reverse=True)[:the.Beam]
#----------------------------------------------------
def rows2dist(data,row1,row2):
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
# XXX waht ranges and mtj etc/ return dict.
# d[short] = lomho
#-- this needs to be in a test
def x2range(x,ranges):
  if x=="?": return x
  for k,(lo,hi) in ranges.items(): 
    if  within(x,lo,hi): return k
  assert False,"should never get here"

def rnd3(x): return rnd(x,3)
def rnd2(x): return rnd(x,2)
def rnd(x,decimals=None): return x if decimals==None else round(x,decimals)

def median(a): return per(a,.5)

def ent(d):
  N = sum((n for n in d.values()))
  return - sum(( n/N * math.log(n/N,2) for n in d.values() if n>0 ))

def stdev(a): return (per(a,.9) - per(a,.1)) / 2.56
def per(a, p=.5): return a[int(p*len(a))]

def str2thing(x:str):
  try:    return literal(x)
  except: return x

def csv2Rows(file):
  with file_or_stdin(None if file =="-" else file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r"\' ]|#.*)', '', line)
      if line:
        yield ROW([str2thing(s.strip()) for s in line.split(",")])

def hue(s,c): return colored(s,c,attrs=["bold"])

def cli(d):
  yell = lambda s: hue(s[1],"yellow")
  bold = lambda s: hue(s[1],"white")
  for k,v in d.items():
    s = str(v)
    for j,x in enumerate(sys.argv):
      if ("-"+k[0]) == x or ("--"+k) == x:
        s = "True" if s=="False" else ("False" if s=="True" else sys.argv[j+1])
    d[k] = str2thing(s)
  if d["help"]: print(re.sub(r"(\n[A-Z]+:)",yell,re.sub(r"(-[-]?[\w]+)",bold,__doc__)))

#--- oops! two scores
#- hide bestRows,restORws inside a lambda
def grow(lst,bestRows,restRows,peeks=32,beam=None):
  beam = beam or len(lst)
  if beam < 2 : return lst
  lst = sorted(lst, key=lambda y: -y[0])[:int(.5+beam)]
  tmp = []
  for a,b in pick2(lst,peeks):
    c= TEST([test for ab in [a,b] for ors in ab.ors.values() for test in ors])
    b= [row for row in bestRows if selects(c,row)]
    r= [row for row  in restRows if selects(c,row)]
    v= score(*map(len,[b,r,bests,rests]))
    tmp += [(v,c)]
  return grow(lst+tmp,bestRows,restRows, peeks,beam/2)

def pick(lst,n):
  r = R()
  for (m,x) in lst:
    r -= m/n
    if r <= 0: return x
  assert False,"should never get here"
#----------------------------------------------------
def eg(fun):
  the = deepcopy(EG.saved)
  random.seed(the.seed)
  failed = fun() == False
  print("❌ FAIL" if failed else "✅ PASS", fun.__name__)
  return failed

class EG:
  saved = deepcopy(the)
  def run(a=sys.argv): cli(the.it); getattr(EG, the.go, EG.oops)()
  def oops()    : print("??")
  def nothing() : ...
  def all()     : sys.exit(sum(map(eg,
                    [EG.the,EG.data,EG.chop,EG.sorted,EG.ideas])))
  #--------------------------------
  def the()  : print(the)

  def data() :
    stats1=data2stats(DATA(csv2Rows(the.file)))
    prints(stats1.it.keys())
    prints(stats1.it.values())

  # its flopped
  def sorted():
    data = DATA(csv2Rows(the.file))
    rows = sortedRows(data)
    prints(data.cols.names)
    [prints(row.cells) for row in rows[:10]]; print("")
    [prints(row.cells) for row in rows[-10:]]
    stats1=data2stats(clone(data,rows[:40]))
    stats2=data2stats(clone(data,rows[40:]))
    prints(["\n"]+list(stats1.it.keys()))
    prints(["best"]+list(stats1.it.values()))
    prints(["rest"]+list(stats2.it.values()))

  def ideas():
    data = DATA(csv2Rows(the.file))
    rows = sortedRows(data)
    chops(data)
    n    = int(len(rows)**the.min)
    bestRows = rows[:n]
    restRows = random.sample( rows[n+1:], n*the.rest )
    prints(data.cols.names)
    [prints(row.cooked) for row in rows[:10]]; print("")
    [prints(row.cooked) for row in rows[-10:]]
    prints(["\nv","b","r","x"])
    for x in goodChops(data,bestRows,restRows): prints(x)
#----------------------------------------------------

EG.run()
