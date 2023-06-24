#!/usr/bin/env python3 -B
#vim: set et sts=2 sw=2 ts=2 : 
# https://en.wikipedia.org/wiki/Effect_size#Other_metrics
from fileinput import FileInput as file_or_stdin
import traceback,random,math,sys,re
from termcolor import colored
from functools import cmp_to_key
from ast import literal_eval

#class BAG(object):
class BAG(object): 
  def __init__(i,**d): i.__dict__.update(**d)
  def __repr__(i):
    show= lambda x: x.__name__ if callable(x) else (f"{x:3g}" if isinstance(x,float) else x)
    d = i.__dict__
    return "{"+" ".join([f":{k} {show(d[k])}" for k in d if  k[0] != "_"])+"}"

the=BAG(seed=1234567891, 
        file="../data/auto93.csv")
#----------------------------------------------------------------------------------------
def COL(at=0,name=""):
  return (NUM if name and name[0].isupper() else SYM)(at=at, name=name)

def SYM(at=0,name=""):
  return BAG(this=SYM,name=name,at=at,n=0, has={},most=0,mode=None)

def NUM(at=0,name=""):
  return BAG(this=NUM, name=name,at=at, n=0, mu=0, m2=0,  hi= -1E30, lo=1E30,
              want= 0 if (name and name[-1]) =="-" else 1)

def COLS(names):
  x,y,klass, = [], [], None
  all = [COL(at,name) for at,name in enumerate(names)]
  for col in all:
    z = col.name[-1]
    if z != "X":
      (y if z in "+-!" else x).append(col)
      if z=="!": klass=col
  return BAG(this=COLS, x=x, y=y, names=names, all=all,klass=klass)

def DATA(rows=[], data=None):
  data = data or BAG(this=DATA,rows=[],cols=None)
  [adds(data,lst) for lst in rows]
  return data
#----------------------------------------------------------------------------------------
def adds(data, row):
  def create(): data.cols  = COLS(row)
  def update(): data.rows += [[add(col, row[col.at]) for col in data.cols.all]]
  return update() if data.cols else create()

def d2h(data,row):
  return (sum((col.want - norm(col,row[col.at]))**2 for col in data.cols.y)
          /  len(data.cols.y))*.5

def ordered(data,rows=None):
  return sorted(rows or data.rows, key=lambda r: d2h(data,r))

def stats(data, cols=None, fun=lambda c: mid(c)):
  return BAG(N=len(data.rows), **{col.name: fun(col) for col in (cols or data.cols.y)})

def clone(data,rows=[]):
  return DATA(data=DATA(rows=[data.cols.names]),rows=rows)

def bin(data1,data2):
  for col1,col2 in zip(data1.cols.y, data2.cols.y):
    if col1.this is SYM:
      for k in col1.has | col2.has:
        yield col,k,k
    else:
      if col1.mu > col2.mu: col1,col2 = col2,col1
      m = valleyBetween(col1.mu,div(col1), col2.mu,div(col2))
      if best.want == 0:  # less is best
        lo,mid,hi = -1E30,rest.mu,mid
        half = (hi - mid)/2
      else:
        lo,mid,hi = mid,best.mu, 1E30
        half = (mid - lo)/2
      for  lo,hi in [(lo, hi),
                     (
                     (z, r+rgap/2),
                     (r-rgap,   r+rgap),
                     (r-rgap/2, r+rgap/2),
                     (m,a),
                     (m,b),
                     (m,b+bgap/2)


                     z, r-rgap),


                     ninf, rest.mu),
                     (ninf, rest.mu + rjump/2),
                     (ninf, mid),
                     (rest.mu - rjump, rest.mu + rjump),
                     (rest.mu - rjump/2, rest.mu + rjump/2),
                     (mid,inf)
                     (mid-bjump/2,inf)


a  ac    c   cm      m    mx      x  xz    z
#----------------------------------------------------------------------------------------
def add(col,x):
  def num():
    col.lo = min(x, col.lo)
    col.hi = max(x, col.hi)
    d       = x - col.mu
    col.mu += d/col.n
    col.m2 += d*(x - col.mu)
  def sym():
    tmp = col.has[x] = 1 + col.has.get(x,0)
    if tmp > col.most: col.most, col.mode = tmp, x
  if x != "?":
    col.n += 1
    num() if col.this is NUM  else sym()
  return x

def norm(col,x):
  return x if (x=="?" or col.this is SYM) else (x-col.lo)/(col.hi-col.lo + 1/1E30)

def mid(col):
  return col.mode if col.this is SYM else col.mu

def div(col):
  def entropy(ns): return -sum((n/col.n*math.log(n/col.n,2) for n in ns))
  def stdev()    : return (col.m2/(col.n-1))**.5
  return stdev() if col.this is NUM else entropy(col.has.values()) 

def valleyBetween(m1,m2,std1,std2):
  a = 1/(2*std1**2) - 1/(2*std2**2)
  if a==0: return (m1+m2)/2
  b = m2/(std2**2) - m1/(std1**2)
  c = m1**2 /(2*std1**2) - m2**2 / (2*std2**2) - math.log(std2/std1)
  root1= (-b + (b**2 - 4*a*c)**.5)/(2*a)
  return root1 if  m1 <= root <= m2 else (-b - (b**2 - 4*a*c)**.5)/(2*a)

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

#----------------------------------------------------------------------------------------

if sys.argv[1:]: 
  random.seed(the.seed)
  EGS.all[sys.argv[1][2:]]()
