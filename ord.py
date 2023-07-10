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
  def __init__(i,**d): i.__dict__.update(**d)
  def __repr__(i):
    f=lambda x:x.__name__ if callable(x) else (f"{x:3g}" if isinstance(x,float) else x)
    return "{"+" ".join([f":{k} {f(v)}" for k,v in i.__dict__.items() if k[0] != "_"])+"}"

key_values = r"\n\s*-\w+\s*--(\w+).*=\s*(\S+)"
the = obj(**{m[1]:literal(m[2]) for m in re.finditer(key_values,__doc__)})

random.seed(the.seed)
prints = lambda a: print(*a,sep="\t")
R= random.random
big  = 1E30
#--------------------------------------------------------
def TEST(col,lo,hi): return obj(this=TEST, isSym=col.this==SYM, at=col.at, txt=col.txt,lo=lo,hi=hi)
def ORS()          : return obj(this=ORS, tests=[])
def ANDS()         : return obj(this=ANDS, ors={}, score=0)

def score(b,r,B,R):
  b = b/(B+1/big)
  r = r/(R+1/big)
  if the.want=="plan"    : return b**2  / (   b + r)
  if the.want=="monitor" : return r**2  / (   b + r)
  if the.want=="doubt"   : return (b+r) / abs(b - r)
  if the.want=="xplore"  : return 1     / (   b + r)

def ands2Score(ands, bestRows, restRows):
  b = [_ for _ in bestRows if selects(ands,row)]
  r = [_ for _ in restRows if selects(ands,row)]
  size = sum((len(ors) for ors in ands.ors))
  ands.score= score(*map(len,[b,r,bestRows,restRows])) / size
  return ands.score

def within(x,lo,hi): return lo <= x < hi

def selects(x, row):
  def _test(test) : return (_sym if test.isSym else _num)(test,row[test.at])
  def _num(test,v): return v=="?" or within(v,test.lo,test.hi)
  def _sym(test,v): return v=="?" or v == test.lo
  def _ors(ors):
    for test in ors.tests:
      if _test(test): return True
  def _ands(ands):
    for ors in ands.ors.values():
      if not _ors(ors,row): return False
    return True
  return (_ands if x.this is ANDS else (_ors if x.this is ORS else _tests))(x)

def tests4Ands(tests,ands=None):
  ands = ands or ANDS()
  def _ors(ors, new):
    out, used = [], False
    for old in ors.tests:
      if  (new.hi == old.hi and new.lo == old.lo): used=True; out += [old];
      elif new.hi == old.lo                      : used=True; out += [old]; old.lo = new.lo
      elif new.lo == old.hi                      : used=True; out += [old]; old.hi = new.hi
      elif new.lo <  old.lo                      : used=True; out += [new,old]
    if not used: out += [new]
    return out
  def _and(new):
    ors = ands.ors[new.at] = ands.ors.get(new.at,ORS())
    ors.tests =  _ors(ors,new)
  [_ands(test) for test in tests]
  return ands

#--------------------------------------------------------
def ROW(a)         : return obj(this=ROW, cells=a, cooked=a[:])

def SYM(n=0, s="") : return obj(this=SYM, at=n, txt=s, n=0, seen={}, most=0, mode=None)
def NUM(n=0, s="") : return obj(this=NUM, at=n, txt=s, n=0, _kept=[], ok=True,
                               heaven= 0 if s and s[-1]=="-" else 1)

def COL(n=0, s=""):
  return (NUM if s and s[0].isupper() else SYM)(n=n,s=s)

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
    now = obj(lo=x1(pairs[0]), hi=x1(pairs[0]), n=obj(best=0, rest=0))
    tmp = [now]
    for i,(klass,row) in enumerate(pairs):
      here = x(row);
      if len(pairs) - i > few *.67 and here != x1(pairs[i-1]):
        if here - now.lo > tiny and now.n.best + now.n.rest > few:
          now  = obj(lo=now.hi, hi=here, n=obj(best=0,rest=0))
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
        merged = obj(lo=a.lo, hi=b.hi, n=obj(best=a.n.best+b.n.best, rest=a.n.rest+b.n.rest))
        na, nb = a.n.best+a.n.rest, b.n.best+b.n.rest
        if ent(merged.n) <= (ent(a.n)*na + ent(b.n)*nb) / (na+nb): # merged's is clearer than a or b
          a  = merged
          i += 1 # skip over b since we have just merged it with a
      outs += [a]
      i   += 1
    return ins if len(ins) == len(outs) else _merge(outs) 
  bests  = [("best",row) for row in bestRows if x(row) != "?"]
  rests  = [("rest",row) for row in restRows if x(row) != "?"]
  tmp    = [[x.lo, x.hi, x.n.best/(len(bestRows) + 1/big), x.n.rest/(len(restRows)+1/big)] 
            for x in _merge( _divide( sorted(bests+rests, key=x1)))]
  tmp[ 0][0] = -big # lowest lo is negative infinity
  tmp[-1][1] =  big # highest hi is positive infinity
  return {rnd2(k/(len(out)-1)): set(lohi) for k,lohi in enumerate(tmp)}

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

# def grow(lst,score):
#   best={}
#   sorted([(score(x),x) for x in lst], reverse=True)
#
#   for x in powerset(lst):
#     n = len(x)
#     if n==0: continue
#     v = score(x)
#     if n not in best:
#       best[n]=0
#       if n>2 and best[n-1] <= best[n=2]: lives -=1 
#
#
#       
#     best[n] = max(best[n],score(lst))
#
#      best[n] = best.get(n,0)
#
#       if n> len(best): 
#
#----------------------------------------------------
def eg(fun):
  the = deepcopy(EG.saved)
  random.seed(the.seed)
  failed = fun() == False
  print("❌ FAIL" if failed else "✅ PASS", fun.__name__)
  return failed

class EG:
  saved = deepcopy(the)
  def run(a=sys.argv): cli(the.__dict__); getattr(EG, the.go, EG.oops)()
  def oops()    : print("??")
  def nothing() : ...
  def all()     : sys.exit(sum(map(eg,
                    [EG.the,EG.data,EG.chop,EG.sorted,EG.ideas])))
  #--------------------------------
  def the()  : print(the)

  def data() :
    stats1=data2stats(DATA(csv2Rows(the.file)))
    prints(stats1.__dict__.keys())
    prints(stats1.__dict__.values())

  def chop() :
    d=DATA(csv2Rows(the.file))
    chops(d)
    for col in d.cols.x: print(col.chops)
    [prints(row.cooked) for row in d.rows[:10]]
    #col = d.cols.x[1]
    #a  = ok(col)._kept
    #for i,row in enumerate(d.rows): print(row.cells[col.at],row.cooked[ col.at], a[0], a[-1])

  def sorted():
    data = DATA(csv2Rows(the.file))
    rows = sortedRows(data)
    prints(data.cols.names)
    [prints(row.cells) for row in rows[:10]]; print("")
    [prints(row.cells) for row in rows[-10:]]

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
