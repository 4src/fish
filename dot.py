#!/usr/bin/env python3 -B
# <!--- vim: set et sts=2 sw=2 ts=2 : --->
import fileinput, ast, re
from collections import Counter, defaultdict

big = 1E30
class obj(dict): __getattr__ = dict.get

the=obj(bins=5, cohen=.35, min=.5, rest=3)
#-------------------------------------------------------------------------------
def ROW(a): return obj(cells=a, cooked=a[:])

def DATA(src):
  rows,cols = [],None
  for row in src:
    if cols:
      [cols[c].append(x) for c,x in enumerate(row.cells) if x != "?"]
      rows += [row]
    else:
      names= row.cells
      cols = {c:[] for c,_ in enumerate(names)}
  return obj(names=names, rows=rows, cuts={}, cols={c:sorted(cols[c]) for c in cols})

def clone(data,rows=[]):
  return DATA( [ROW(data.names)] + rows)

def isNum(s): return s[0].isupper()
def isGoal(s): return s[-1] in "+-"

def norm(a,x):
  return x if x=="?" else (x- a[0])/(a[-1] - a[0] + 1/big)

def mid(name,a,decimals=None):
  return rnd(median(a),decimals) if isNum(name) else mode(Counter(a))

def div(name,a,decimals=None):
  return rnd(stdev(a) if isNum(name) else ent(Counter(a)), decimals)

def median(a):
  return a[int(.5*len(a))]

def stdev(a):
  return (a[int(.9*len(a))] - a[int(.1*len(a))])/ 2.56

def mode(d):
  return max(d, key=d.get)

def ent(d)
  n = sum(d.values())
  return - sum(( m/n * math.log(m/n, 2) for m in d.values() ))

def sortedRows(data):
  w = {c:(0 if s[0]=="-" else 1) for c,s in enumerate(data.names) if isGoal(s)}
  def _distance2heaven(row):
    return sum(( (w[c] - norm(data.cols[c], row.cells[c]))**2 for c in w ))**.5
  return sorted(data.rows, key=_distance2heaven)

def stats(data, cols=None, decimals=None, fun=mid):
  cols = cols or [c for c in data.cols if isGoal(data.names[c])]
  return obj(N=len(data.rows),**{data.names[c]: fun(data.names[c],a,decimals) for c,a in cols})
#-------------------------------------------------------------------------------
def discretize(data, bests,rests):
  def _num(c):
    out, tmp = {}, cuts(data.cols[c])
    for y,rows in [("best",bests), ("rest", rests)]:
      for row in rows:
        x=row.cells[c]
        if x != "?"
          k = cut(x, tmp)
          z = out[k] = out.get(k,None) or obj(lo=x,hi=x,n=obj(best=0, rest=0))
          z.lo = min(z.lo, x)
          z.hi = max(z.hi, x)
          z.n[y] += 1
    return [z.lo for z in merges(sorted(out.values(), key=lambda z:z.lo))]
  #-----------------------------------
  for c,name in enumerate(data.names):
    if not isGoal(name):
      data.cuts[c] = _num(c) if isNum(name) else sorted(set(data.cols[c]))
      for row in data.rows:
        row.cooked[c] = cut(row.cooked[c], data.cuts[c])
  return data

def cuts(a):
  n = inc = int(len(a)/the.bins)
  b4, small = a[0],  the.cohen*stdev(a)
  out = []
  while n < len(a) -1 :
    x = a[n]
    if x==a[n+1] or x - b4 < small: n += 1
    else: n += inc; out += [x]; b4=x
  out += [big]
  return out

def cut(x,cuts):
  if x=="?": return x
  for n,v in enumerate(cuts):
    if x < v: return n/(len(cuts)-1)

def merges(ins):
  def _merged(z1,z2)
    z3 = obj(lo=z1.lo, hi=z2.hi, n=obj(best= z1.n.best + z2.n.best,
                                       rest= z1.n.rest + z2.n.rest))
    n1,n2 = z1.n.best + z1.n.rest, z2.n.best + z2.n.rest
    if ent(z3.n) <= (ent(z1.n)*n1 + ent(z2.n)*n2) / (n1+n2):
      return z3
  #--------------
  outs, n = [], 0
  while n < len(ins):
    one = ins[n]
    if n < len(ins)-1:
      if merged := _merged(one, ins[n+1])
        one = merged
        n += 1
    outs += [one]
    n += 1
 return ins if len(ins)==len(outs) else merges(outs)

#---------------------------------------------
def rnd(x,decimals=None)
  return round(x,decimals) if decimals != None  else x

def coerce(x):
  try : return ast.literal_eval(x)
  except : return x.strip()

def csv(file="-", filter=ROW)
  with fileinput.FileInput(None if file == "-" else file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r"\' ]|#.*)', '', line)
      if line:
        yield filter([coerce(x) for x in line.split(",")])
#---------------------------------------------

data = DATA(csv())
data = discretize(data)
tmp = sortedRows(data)
print(*data.names,sep="\t")
[print(*row.cells,sep="\t") for row in tmp[:10]]; print("")
[print(*row.cells,sep="\t") for row in tmp[-10:]]
