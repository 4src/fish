from collections import Counter

def isGoal(s)   : return s[-1] in "+-"
def isNum(s)    : return s[0].isupper()
def isIgnores(s): return s[-1] = "X"

class box(dict): __setattr__ = dict.__setitem__; __getattr__ = dict.get  



def items(x,cols): 
  if nump(x):
    for c,v in enumerate(x): yield c, our.names[c], v 
  else
    for c,(name,v) in enumerate(x.items()): yield c,name,v

def using(src, use=None):
  "yields just the columns we are using, coercing values"
  for a in src:
    use = use or [n for n,x in enumerate(a) if not isIgnored(x)]
    yield [coerce(a[n]) for n in use]
       
def rowCols(src, cols=None)
  "yields each row and the cols, after row1. Row1  builds the cols; other rows update cols"
  for n,a in enumerate(using(src)):
    if cols: 
      [col.add(a[n]) for n,col in cols.all.items()]
      yield n-1,a,cols
    else:  
      names,all,x,y = a,{},{},{}
      for n,name in enumerate(names):
         all[n] = (y if isGoal(name) else x)[n] = (NUM if isNum(name) else SYM)(n,name) 
      cols = box(names=names, all=all, x=x, y=y)
  
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


