#!/usr/bin/env python3 -B
# <!--- vim: set et sts=2 sw=2 ts=2 : --->
import fileinput, ast, re
from collections import Counter

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
  return x if x=="?"  else (x-a[0])/(a[-1] - a[0] + 1/big)

def mid(name,a,decimals=None):
  return rnd(median(a),decimals) if isNum(name) else  mode(Counter(a))

def div(name,a,decimals=None):
  return rnd(stdev(a) if isNum(name) else ent(Counter(a)), decimals)

def median(a):  return a[len(a)//2]

def stdev(a):
  per = lambda p: a[p*len(a)//100]
  return (per(90) - per(10))/ 2.56

def mode(d):  return sorted(a.items(),key=lambda z:z[1])[-1][1]

def ent(d)
  N = sum(d.values())
  return - sum(( n/N * math.log(n/N, 2) for n in d.values() if n > 0 ))

def sortedRows(data):
  w = {c:(0 if s[0]=="-" else 1) for c,s in enumerate(data.names) if isGoal(s)}
  def _distance2heaven(row):
    return sum(( (w[c] - norm(data.cols[c], row.cells[c]))**2 for c in w ))**.5
  return sorted(data.rows, key=_distance2heaven)

def stats(data, cols=None,decimals=None,fun=mid):
  cols = cols or [c for c in data.cols if isGoal(data.names[c])]
  return obj(N=len(data.rows),**{data.names[c]: fun(data.names[c],a,decimals) for c,a in cols})
#-------------------------------------------------------------------------------
def discretize(data, bests,rests):
  def _update(lohi,x,y):
     lohi.lo = min(lohi.lo,x)
     lohi.hi = max(lohi.hi,x)
     lohi.n[y] += 1
  #-----------------
  def _num(c):
    out, chops = {}, cuts(data.cols[c])
    for y,rows in dict(best=bests, rest=rests).items():
      for row in rows:
        x=row.cells[c]
        if x != "?"
          k = cut(x,chops)
          if k not in out: out[k] = obj(lo=x,hi=x,n=obj(best=0, rest=0))
          _update(out[k],x,y)
    return merges(sorted(out.values(), key=lambda z:z.lo))
  #-----------------------------------
  for c,name in enumerate(data.names):
    if not isGoal(name):
      data.cuts[c] = tuple(_num(c) if isNum(name) else sorted(set(data.cols[c])))
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
        outs += [merged]
        n += 2
        continue
    outs += [one]
    n += 1
 return merges(out) if len(outs) < len(ins) else [z.lo for z in ins]+[big]

#---------------------------------------------
def rnd(x,decimals=None)
  return round(x,decimals) if decimals else x

def coerce(x):
  try : return ast.literal_eval(x)
  except : return x.strip()

def csv(file):
  with fileinput.FileInput(None if file == "-" else file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r"\' ]|#.*)', '', line)
      if line:
        yield ROW([coerce(x) for x in line.split(",")])
#---------------------------------------------

data = DATA()
data = discretize(data)
tmp = sortedRows(data)
print(*data.names,sep="\t")
[print(*row.cells,sep="\t") for row in tmp[:10]]; print("")
[print(*row.cells,sep="\t") for row in tmp[-10:]]
