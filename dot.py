#!/usr/bin/env python3 -B
# <!--- vim: set et sts=2 sw=2 ts=2 : --->
import fileinput, ast, re

big = 1E30
class obj(dict): __getattr__ = dict.get

the=obj(bins=5, cohen=.35, min=.5, rest=3)

def ROW(a): return obj(cells=a, cooked=a[:])

def DATA(file="-"):
  rows,names,cols = [],[],{}
  for r,row in enumerate(csv(file)):
    if r==0 : 
      names=row.cells
    else:
      rows += [row]
      for c,x in enumerate(row.cells):
        a = cols[c] = cols.get(c,[])
        if x != "?": a += [x]
  return obj(names=names, rows=rows, chops={}, 
             cols={c:sorted(cols[c]) for c in cols})

def isNum(s): return s[0].isupper()
def isGoal(s): return s[-1] in "+-"

def chop(x,chops):
  if x=="?": return x
  for n,v in enumerate(chops):
    if x < v: return n/(len(chops)-1)

def chops(a):
  n = inc = int(len(a)/the.bins)
  stdev = (a[int(.9*len(a))] - a[int(.1*len(a))])/2.56
  b4, out, small = a[0], [], the.cohen*stdev
  while n < len(a) -1 :
    x = a[n]
    if x==a[n+1] or x - b4 < small: n += 1
    else: n += inc; out += [x]; b4=x
  out += [big]
  return out

def unsuperd(data):
  for c,name in enumerate(data.names):
    if not isGoal(name):
      if isNum(name):
        cuts = data.chops[c] = chops(data.cols[c])
        for row in data.rows:
          row.cooked[c] =  chop(row.cooked[c], cuts)
      else:
        data.chops[c] = sorted(set(data.cols[c]))
  return data

def sortedRows(data):
  w = {c:(0 if s[0]=="-" else 1) for c,s in enumerate(data.names) if isGoal(s)}
  def _distance2heaven(row):
    return sum((  (w[c] - row.cells[c])**2 for c in w )) 
  return sorted(data.rows, key=_distance2heaven)

# can i get the chops in first here?  so data.chops[c] only gets set once?
def superd(data):
  rows = sortedRows(data)
  n = int(len(rows)**the.min)
  bests = rows[:n]
  rests = random.sample(rows[n:], n*the.rest)
  for c in data.chops:
    if isNum(data.names[c]):
      tmp = {cut: obj(lo=cut, hi=cut,best=0,rest=0) for cut in data.chops[c]}
      for y,row in dict(best=bests, rest=rests).items():
        x = row.cooked[c]
        tmp[x][y] += (0 if x == "?" else 1)
      data.chops[c] = merges(sorted(tmp.values()), key=lambda z:z.lo)
      for row in data.rows:
        row.cooked[c] = chop(row.cells[c], data.chopx[c])
  return data

def merges(ins):
  outs, i = [], 0
  while i < len(ins):
    a = ins[i]
    if i < len(ins)-1:
      if c := merged(a,ins[i+1])
        outs += [c]
        i += 2
        continue
    outs += [a]
    i += 1
  return tuple([z.lo for z in ins]+[big]) if len(ins) == len(outs) else merges(outs)

def merge(z1,z2)
  def _ent(d):
    N = sum(d.values())
    return - sum(( n/N * math.log(n/N, 2) for n in d.values() if n > 0 ))
  z3 = obj(lo=z1.lo, hi=2.hi, n=obj(best=0,rest=0))
  n1,n2 = z1.n.best + z1.n.rest, z2.n.best + z2.n.rest
  z3.n.best = z1.n.best+z2.n.best
  z3.n.rest = z1.n.rest+z2.n.rest
  if _ent(z3.n) <= (_ent(z1.n)*n1 + _ent(z2.n)*n2) / (n1+n2): 
    return z3


#---------------------------------------------
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
