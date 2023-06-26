#!/usr/bin/env python3 -B
#vim : set et sts=2 sw=2 ts=2 : 
# https://en.wikipedia.org/wiki/Effect_size#Other_metrics
from fileinput import FileInput as file_or_stdin
import traceback,random,math,sys,re
from termcolor import colored
from functools import cmp_to_key
from ast import literal_eval

class BOX(object): 
  def __init__(i,**d): i.__dict__.update(**d)
  def __repr__(i):
    show = lambda x: x.__name__ if callable(x) else (f"{x:3g}" if isinstance(x,float) else x)
    d    = i.__dict__
    return "{"+" ".join([f":{k} {show(d[k])}" for k in d if  k[0] != "_"])+"}"

the = BOX(seed = 1234567891, 
          min  = .5,
          rest = 3,
          file = "../data/auto93.csv")
#----------------------------------------------------------------------------------------
def COL(at=0, name=""):
  return (NUM if name and name[0].isupper() else SYM)(at=at, name=name)

def SYM(at=0, name=""):
  return BOX(this=SYM, name=name, at=at, n=0, has={}, most=0, mode=None, prep=lambda x:x)

def NUM(at=0, name=""):
  return BOX(this=NUM, name=name, at=at, n=0, mu=0, m2=0, 
             hi= -1E30, lo=1E30, prep=int,
             want= 0 if (name and name[-1]) =="-" else 1)

def COLS(names):
  x,y,klass, = [], [], None
  all = [COL(at,name) for at,name in enumerate(names)]
  for col in all:
    z = col.name[-1]
    if z != "X":
      (y if z in "+-!" else x).append(col)
      if z=="!": klass=col
  return BOX(this=COLS, x=x, y=y, names=names, all=all,klass=klass)

def DATA(rows=[], data=None):
  data = data or BOX(this=DATA,rows=[],cols=None)
  [adds(data,lst) for lst in rows]
  return data
#----------------------------------------------------------------------------------------
def add(col,x):
  def _num():
    col.lo = min(x, col.lo)
    col.hi = max(x, col.hi)
    d       = x - col.mu
    col.mu += d/col.n
    col.m2 += d*(x - col.mu)
    if type(x) == float: col.prep = float
  def _sym():
    tmp = col.has[x] = 1 + col.has.get(x,0)
    if tmp > col.most: col.most, col.mode = tmp, x
  if x != "?":
    col.n += 1
    _num() if col.this is NUM  else _sym()

def norm(col,x):
  return x if (x=="?" or col.this is SYM) else (x-col.lo)/(col.hi-col.lo + 1/1E30)

def mid(col):
  return col.mode if col.this is SYM else col.mu

def div(col):
  def _ent(ns) : return -sum((n/col.n*math.log(n/col.n,2) for n in ns))
  def _std()   : return (col.m2/(col.n-1))**.5
  return _std() if col.this is NUM else _ent(col.has.values()) 

def cross(num1,num2)
  mu1, std1 = num1.mu, div(num1)
  mu2, std2 = num2.mu, div(num2)
  if mu2 < mu1: return cross(num2, num1)
  if std1==0 or std2==0 or std1==std2: return (mu1+mu2)/2
  a  = 1/(2*std1**2) - 1/(2*std2**2)
  b  = mu2/(std2**2) - mu1/(std1**2)
  c  = mu1**2 /(2*std1**2) - mu2**2 / (2*std2**2) - math.log(std2/std1)
  x1 = (-b + (b**2 - 4*a*c)**.5)/(2*a)
  x2 = (-b - (b**2 - 4*a*c)**.5)/(2*a)
  return x1 if mu1 <= x1 <= mu2 else x2
#----------------------------------------------------------------------------------------
def adds(data, row):
  def _create(): data.cols = COLS(row)
  def _update(): [add(col,row[col.at]) for col in data.cols.all]
                 data.rows += [row]
  _update() if data.cols else _create()

def d2h(data,row):
  return (sum((col.want - norm(col,row[col.at]))**2 for col in data.cols.y) / len(data.cols.y))*.5

def ordered(data,rows=None):
  return sorted(rows or data.rows, key=lambda r: d2h(data,r))

def stats(data, cols=None, fun=lambda c: mid(c)):
  return BOX(N=len(data.rows), **{col.name: fun(col) for col in (cols or data.cols.y)})

def clone(data,rows=[]):
  return DATA(data=DATA(rows=[data.cols.names]),rows=rows)
#----------------------------------------------------------------------------------------
def KEY(col,lo,hi):
  return BOX(this=KEY, at=col.at, lo=lo, hi=hi, name=col.name)

def RULE(keys=[]):
  rule = BOX(this=RULE, score = 0, cols={})
  [key(rule,k) for k in keys]
  return rule

def key(rule, new):
  if new.this is RULE:
    [key(rule, k) for keys in new.cols.values() for k in keys]
  else:
    b4 = rule.cols[new.at] = rule.cols.get(new.at,[])
    overlaps = False
    for  old in b4:
      if new.lo <= old.lo and old.lo <= new.hi <= old.hi: old.hi = new.hi; overlaps = True
      if new.hi >= old.hi and old.lo <= new.lo <= old.hi: old.lo = new.lo; overlaps = True
    if not overlaps: b4 += [new]
  return rule

def selects(rule,row):
  def _or(keys):
    for key in keys:
      x = row[key.at]
      if x=="?" or key.lo <= x <= key.hi: return True
  for keys in rule.cols.values():
    if not _or(keys): return False
  return True

def score(rule, bests, rests, B=1, R=1):
  bs  = [row for row in best.rows if selects(rule,row)]
  rs  = [row for row in rest.rows if selects(rule,row)]
  b,r = len(bs)/B, len(rs)/R
  rule.score = b**2/(b+r)
  yield rule

def rules(bests,rests,B=1,R=1):
  for best,rest in zip(bests.cols.x, rests.cols.x):
    for key in keys(best,rest):
      yield score(RULE([ key ]), bests,rests,B,R)

def keys(best,rest):
  "Returns ranges (lo,hi) being values more often in `best` than `rest`."
  def _sym():
    freq = lambda col,l: col.has.get(k,0) / col.n
    return [(k,k) for k in best.has if freq(best,k) > freq(rest,k)]
  def _num():
    a,z,mu,d = -1E30, 1E30, best.mu, abs(best.mu - cross(best.mu,rest.mu,div(best), div(rest)))
    tmp = [(a, mu),(a, mu+d/2),(a, mu+d)] if mu < rest.mu else [(mu, z),(mu-d/2, z),(mu-d, z)]
    f   = best.prep
    return [ (f(lo), f(hi)) for lo,hi in tmp + [(mu-d, mu+d), (mu-d/2, mu+d/2)] ]
  for lo,hi in set( _sym() if best.this is SYM else _num() ):
    yield KEY(best,lo,hi)

def bore(bests,rests,b4=0,stop=None,B=None,R=None):
  stop = stop or len(bests.rows)**the.min
  B,R  = B or len(bests.rows), R or len(rests.rows)
  if stop < len(bests.rows):
    criterion = sorted(criteria(bests,rests,B,R),reverse=True,key=lambda c:c.score)[0] 
    if criterion,score > b4:
      print(BOX(b=len(bests.rows), r=len(rests.rows),name=name,lo=lo,hi=hi,score=f"{score:3g}"))
      bestrows = [row for row in bests.rows if select(row[at],lo,hi)]
      restrows = [row for row in rests.rows if select(row[at],lo,hi)]
      if len(bestrows) != len(bests.rows) or len(restrows) != len(rests.rows):
        bore(clone(bests, bestrows), clone(rests, restrows), score, stop, B, R)

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
  all = locals()

  def Help():
    "Show help"
    print("./tiny.py --ACTION\n\nACTIONS:")
    [print(f"  --{k}\t: {f.__doc__}") for k,f in EGS.all.items() if k[0].isupper()]

  def Rows():
    "Can we read rows from a csv file?"
    [print(row) for row in csv(the.file)]

  def Data():
    "Can we load a csv file into one of our DATAs?"
    print(DATA(csv(the.file)).cols.x[-1])

  def Stats():
    "Can we summarize the distributions in a DATA?"
    print(stats(DATA(csv(the.file))))

  def Better():
    "Can we sort two rows?"
    d=DATA(csv(the.file))
    rows=ordered(d)
    best = rows[:10]
    rest = random.sample(rows[10:],90)
    print("best", stats(clone(d,best)))
    print("rest", stats(clone(d,rest)))

  def Roots():
    print(valleyBetween( 2.5,5,1,1)) # --> 3.75

  def Bins():
    "Can we sort two rows?"
    d=DATA(csv(the.file))
    rows=ordered(d)
    best = clone(d, rows[:20])
    rest = clone(d,random.sample(rows[20:],60))
    for at,name,lo,hi in bin(best,rest):
      print(at,name,lo,hi)

  def Ranges():
    "Can we sort two rows?"
    d= DATA(csv(the.file))
    rows = ordered(d)
    n = int(len(rows)**the.min)
    bests = clone(d, rows[:n])
    rests = clone(d,random.sample(rows[n:],n*the.rest))
    score,at,name,lo,hi = sorted(selects(bests,rests),reverse=True)[0]
    print(score,at,name,lo,hi)

  def Bore():
    "Can we sort two rows?"
    d    = DATA(csv(the.file))
    rows = ordered(d)
    n    = int(len(rows)**the.min)
    print(n, n*the.rest)
    bore( clone(d, rows[:n]),
          clone(d, random.sample(rows[n:], n*the.rest)))
#--------------------------------------------------------------------------------------
if sys.argv[1:]: 
  random.seed(the.seed)
  EGS.all[sys.argv[1][2:]]()
