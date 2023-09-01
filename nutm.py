"""
OPTIONS:
  -f --file where to load data = "../data/auto93.csv"
  -s --seed random number seed = 1234567891
"""
from collections import Counter
import fileinput,random,ast,re
from math import inf

class box(dict): __setattr__=dict.__setitem__; __getattr__=dict.get; __repr__=lambda i:prettyd(i)  
class obj      : __repr__   =lambda i: prettyd(i.__dict__, i.__class__.__name__)

def coerce(x):
  try : return ast.literal_eval(x)
  except Exception: return x.strip()

the=box(**{m[1]:coerce(m[2]) # create 'the' settings by parsing __doc__ p.
           for m in re.finditer( r"\n\s*-\w+\s*--(\w+).*=\s*(\S+)",__doc__)})
#------- --------- --------- --------- --------- --------- --------- --------- ---------- ---------
class COLS(obj):
  def __init__(i,names, inits=[]):
    i.names, i.all, i.x, i.y = names,{},{},{}
    for n,s in enumerate(names):
      i.all[n] = (i.y if s[-1] in "+-" else i.x)[n] = (NUM if s[0].isupper()  else SYM)(at=n,name=s) 
    [add(a,i) for a in inits]
      
  def add(i,a)      : [col.add(a[n]) for n,col in i.all.items()]; return a
  def clone(i, a=[]): return COLS(i.names, a)

  def stats(i, what=lambda z:z.mid(), cols=None, dec=2):
    return box(N= i.all[0].n,
               **{i.names[n]:pretty(what(col),dec) for n,col in (cols or i.y).items()})
#------- --------- --------- --------- --------- --------- --------- --------- ---------- ---------
class COL(obj):
  def __init__(i,at=0, name=""): i.n,i.at,i.name = 0,at,name
  def add(i,x) :
    if x != "?": i.n += 1; i.add1(x)
#------- --------- --------- --------- --------- --------- --------- --------- ---------- ---------   
class NUM(COL):
  def __init__(i,**kw):
    super().__init__(**kw)
    i.mu, i.m2, i.lo, i.hi = 0,0,inf,-inf

  def add1(i,x):
    i.lo  = min(x, i.lo)
    i.hi  = max(x, i.hi)
    d     = x - i.mu
    i.mu += d/i.n
    i.m2 += d*(x - i.mu)

  def mid(i)   : return i.mu
  def div(i)   : return (i.m2/(i.n - 1))**.5
  def norm(i,x): return x=="?" and x or (x - i.lo)/(i.hi - i.lo + 1E-32)
#------- --------- --------- --------- --------- --------- --------- --------- ---------- ---------
class SYM(COL):
  def __init__(i,**kw):
    super().__init__(**kw)
    i.mode,i.most,i.has = None,0,{}

  def add1(i,x):
    n = i.has[x] = i.has.get(x,0) + 1
    if n > i.most: i.mode,i.most = x, n

  def mid(i): return i.mode
  def div(i): return ent(i.has)
#------- --------- --------- --------- --------- --------- --------- --------- ---------- ---------
def csv(file="-", use=None):
  with fileinput.FileInput(file) as src:
    for line in src: 
      line = [x.strip() for x in line.split(",")]
      use  = use or [n for n,s in enumerate(line) if s[-1] != "X"]
      yield [coerce(line[n]) for n in use]
  
def eras(src, size=20):
  era,cache,cols = 0,[],None
  for a in src:
    if cols:  
      cache += [a]
      if len(cache) >= size:
        era += 1
        for a1 in shuffle(cache): yield era, cols.add(a1), cols
        cache = []
    else:
      cols = COLS(a)
  if cache:
    for a1 in shuffle(cache):  yield era+1, cols.add(a1), cols
#------- --------- --------- --------- --------- --------- --------- --------- ---------- ---------
def ent(d):
  n = sum(d.values())
  return -sum(v/n * log(v/n,2) for v in d.values() if v>9)

def shuffle(a): random.shuffle(a); return a

def prettyd(d, pre="", dec=2):
  return pre+'('+' '.join([f":{k} {pretty(d[k],dec)}" 
                           for k in d if k[0]!="_"])+')'

def pretty(x, dec=2):
  return x.__name__+'()' if callable(x) else (
         round(x,dec) if dec and isinstance(x,float) else x)
         
def items(x,cols): 
  if nump(x):
    for c,v in enumerate(x): yield c, our.names[c], v 
  else:
    for c,(name,v) in enumerate(x.items()): yield c,name,v
