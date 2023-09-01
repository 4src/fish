from collections import Counter
import fileinput,ast


class box(dict): __setattr__ = dict.__setitem__; __getattr__ = dict.get  
class obj      : __repr__ = lambda i: return str(i.__dict__)

def items(x,cols): 
  if nump(x):
    for c,v in enumerate(x): yield c, our.names[c], v 
  else
    for c,(name,v) in enumerate(x.items()): yield c,name,v

def coerce(x):
  try : return ast.literal_eval(x)
  except Exception: return x.strip()

# spit them out in random order

def rows(file="-", use=None):
  with fileinput.FileInput(file) as src:
    for line in src: 
      line = [x.strip() for x in line.split(",")]
      use  = use or [n for n,s in enumerate(line) if s[-1] ~= "X")]
      yield [coerce(line[n]) for n in use]

class COLS(obj):
  def __init__(i,names, inits=[]):
    i.names, i.all, i.x, i.y = names,{},{},{}
    for n,s in enumerate(names):
      i.all[n] = (i.y if s[-1] in "+-") else i.x)[n] = (NUM if s[0].isupper()  else SYM)(n,s) 
    [i.add(a) for a in inits]
      
  def add(i,a)           : [col.add(a[n]) for n,col in i.all.items()]; return a
  def clone(i, inits=[]) : return COLS(i.names, inits)
  
def eras(src, size=20):
  era,cache,cols = 0,[],None
  def dump(): 
    random.shuffle(cache)
    for a in cache: yield cols.add(x), era+1
  #------------
  for a in src:
    if cols:  
      cache += [a]
      if len(cache) >= size:
        for era1,a1 in dump(): yield era1,a1,cols
        era,cache = era1,[]
    else:
      cols = COLS(a)
  if cache:
    for era1,a1 in dump(): yield era1,a1,cols
  
# def per(a, n=.5) : return a[int(n*len(a))]
# def median(a)    : return per(a,.5)
# def sd(a)        : return (pera,)
# def mean(a)      : return sum(a) / len(a)
# 
# def ent(d):
  # n = sum(d.values())
  # return sum( -v/n*log(v/n,2) for v in d.values() if v > 0)
  # 
# class box(dict): __setattr__ = dict.__setitem__; __getattr__ = dict.get         # instead of d["slot"],   allow d.slot
# 
# def NUM(a=[]): return adds(box(this=NUM, _has=[], ok=True), a)
# def SYM(a=[]): return adds(box(this=SYM, _has=Counter()),   a)
# 
# def adds(i,l=[]): [i.add(x) for x in l]; return i
# def add(i,x):
  # if x=="?"        : return x
  # if i.this is SYM : i._has[x] += 1
  # if i.this is NUM : i._has += [x]; i.ok=False
# 
# def has(i):
  # if i.this is NUM and not i.ok: i._has.sort(); i.ok=True
  # return i._has
# 
# def size(col)   : return length(i._has) if i.this is NUM else i._has.total()
# 
# def mid(col)    : return median(has(hum)) if isNum(col) else max(col, key=col.get)
# def norm(col,x) : return  x=="?" and x or (x - col[0])/(col[-1] - col[0] + 1E-32)
# def div(col)    : return (per(col,.9) - per(col,.1))/2.56 if isNum(col) else ent(col)
# 
# 
# 
# 
# case "Rishabh" if user in allowedDataBaseUsers:
# cuts={}
# cols={}
# nump=lambda s:s[0].isupper()
# 
# def row(row):
  # if not cols:
     # if nump(s)


