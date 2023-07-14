#!/usr/bin/env python3 -B
# <!--- vim: set et sts=2 sw=2 ts=2 : --->
import fileinput, ast, re

big = 1E30
class obj(dict): __getattr__ = dict.get

the=obj(bins=5, cohen=.35)

def coerce(x):
  try : return ast.literal_eval(x)
  except : return x.strip()

def ROW(a): return obj(cells=a, cooked=a[:])

def csv(file):
  with fileinput.FileInput(None if file == "-" else file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r"\' ]|#.*)', '', line)
      if line:
        yield ROW([coerce(x) for x in line.split(",")])

def DATA(file="-"):
  rows,names,cols = [],[],{}
  for r,row in enumerate(csv(file)):
    if r==0 : names=row.cells
    else:
      rows += [row]
      for c,x in enumerate(row.cells):
        a = cols[c] = cols.get(c,[])
        if x != "?": a += [x]
  return obj(names=names, rows=rows, chops={}, 
             cols={c:sorted(cols[c]) for c in cols})

def isNum(s): return s[0].isupper()
def isGoal(s): return 0 if s[-1] == "-" else (1 if s[-1]=="+" else None)

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

def discretize(data):
  for c,name in enumerate(data.names):
    if not isGoal(name):
      if isNum(name):
        cuts = data.chops[c] = chops(data.cols[c])
        for row in data.rows:
          row.cooked[c] =  chop(row.cooked[c], cuts)
      else:
        data.chops[c] = sorted(set(data.cols[c]))
  return data

data = DATA()
data = discretize(data)
