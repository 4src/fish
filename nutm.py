from collections import Counter

def isNum(x): return isinstance(x,list)
def goalp(s): return s[-1] in "+-"
def nump(s):  return s[0].isupper()

def slots(x): 
  if isNum(x):
    for n,v in enumerate(x): yield meta(n),v 
  else
    for name,v in x.items(x): yield meta4(name),v

def cols(x, fun=lambda _:True):
  for k,v in slots(x): 
      if fun(k): yield k,v 
    
for k,v in cols(dict(Aa=1,b=2)): print(k,v)

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


