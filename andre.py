#!/usr/bin/env python3
from collections import Counter
from math import log,inf
import fileinput,random,time,ast,re

class obj(object):
   __repr__ = lambda i:printd(i.__dict__, i.__class__.__name__)

class box(dict):
   __getattr__ = dict.get
   __setattr__ = dict.__setitem__
   __repr__    = lambda i : printd(i)

the=box(cohen=.35,bins=5,file="../data/auto93.csv",p=2)

class ROW(obj):
   def __init__(i,a)   : i.cells=a; i.reset()
   def reset(i)        : i.use, i.evaled = True, False
   def better(i,j,cols): return i.d2h(cols) < j.d2h(cols)
   def d2h(i,cols):
      i.evaled = True
      denom = len(cols)**(1/the.p)
      return sum((col.d2h(row))**the.p for col in cols)**(1/the.p) / denom

#---------------------------------------------------------------
class COL(obj):
   def __init__(i,a=[], name=" ", at=0):
      i.n, i.at, i.name = 0, at, name
      [i.add(x) for x in a]
   def add(i,x):
      if x !="?": i.n += 1; i.add1(x)
   def dist(i,x,y):
     return 1 if x=="?" and y=="?" else i.dist1(x,y)
#---------------------------------------------------------------
class SYM(COL):
   def __init__(i,*l,**d): 
      i.has =  Counter()
      super().__init__(*l,**d)
   def mid(i)       : return max(i.has, key=i.has.get)
   def div(i)       : return ent(i.has)
   def dist1(i,x,y) : return 0 if x==y else 1
   def add1(i,x)    : i.has[x] += 1
   def cuts(i,_)    : return [(i.at, k, k) for k in i.has]
#---------------------------------------------------------------
class NUM(COL):
   def __init__(i,*l,**d):
      i.mu, i.m2, i.lo, i.hi = 0,0,big,-big
      super().__init__(*l,**d)
      i.heaven = 0 if i.name[-1] == "-" else 1
   def mid(i): return i.mu
   def div(i): return (i.m2/(i.n-1))**.5
   def norm(i,x): return "?" if x=="?" else (x- i.lo)/(i.hi - i.lo + 1/big)
   def d2h(i,row): return abs(i.heaven - i.norm(row.cells[i.at]))
   def dist1(i,x,y):
      x,y = i.norm(x), i.norm(y)
      if x=="?": x= 0 if y > .5 else 1
      if y=="?": y= 0 if x > .5 else 1
      return abs(x - y)
   def add1(i,x):
      i.lo  = min(x, i.lo)
      i.hi  = max(x, i.hi)
      d     = x - i.mu
      i.mu += d/i.n
      i.m2 += d*(x - i.mu)
   def cuts(i,rows):
      xs   = sorted([row.cells[i.at] for row in rows if row.cells[i.at] != "?"])
      nmin = len(xs)/(the.bins - 1)
      xmin = the.cohen * i.div()
      lo   = xs[0]
      tmp  = [[i.at,lo,lo]]
      ns   = 0
      for n,x in enumerate(xs):
         if n < len(xs) - nmin and x != xs[n+1] and ns >= nmin and x-lo >= xmin:
            tmp += [[i.at,hi,x]]
            lo  = x
            ns  = 0
         hi  = x
         ns += 1
         tmp[-1][-1] = x
      tmp[-1][-1] = inf
      tmp[ 0][ 1] = -inf
      return [tuple(x) for x in tmp]

def COLS(a):
   all = [(NUM if s[0].isupper() else SYM)(at=n,name=s) for n,s in enumerate(a)]
   x,y = [],[]
   for col in all:
      if col.name[-1] != "X":
         (y if col.name[-1] in "+-!" else x).append(col)
   return box(x=x, y=y, names=a, all=all)

class SHEET(obj):
   def __init__(i, src):
     i.rows, i.cols = [],[]
     [i.add(row) for row in src]
   def add(i,row):
      if i.cols:
            i.rows += [row]
            [col.add(row.cells[col.at]) for col in i.cols.all]
      else: i.cols = COLS(row.cells)
   def dist(i,r1,r2):
      cs = i.cols.x
      return (sum(c.dist(r1.cells[c.at],r2.cells[c.at])**the.p for c in cs)/len(cs))**(1/the.p)
   def mode(i,cols=None):
      return ROW([col.mid() for col in cols or i.cols.all])
   def stats(i, cols="y", decs=None, want="mid"):
      return box(N=len(i.rows),
                 **{c.name:prin(c.div() if want=="div" else c.mid(),decs) for c in i.cols[cols]})

class SNEAK(obj):
   def __init__(i,sheet):
     sheet.use  = True
     sheet.dept = 1
     sheet.lefts = sheet.rights = None;
     for row in sheet.rows: row.reset()
     cuts = {col.at:col.cuts(i.rows) for  col in i.cols.x} 

   def ents(i,rows):
      "only for the use-able rows"
      def counts(at):
         cuts1 = i.cuts[at]
         count= Counter()
         for row in rows:
            if row.use:
               x = row.cells[at]
               if x != "?":
                  count[cut(x,cuts1)] += 1
         return count
      return {at:ent(counts(at)) for at in i.cuts}

    def isCandidate(i,sheet):
       return sheet.use and sheet.lefts  and sheet.lefts.use \
                        and sheet.rights and sheet.rights.use

   def dontUse(i,sheet=None):
      if sheet:
          sheet.use = False
          for row in sheet.rows: row.use=False
          i.dontUse(i,sheet.lefts)
          i.dontUse(i,sheet.rights)
   #
   # def loop(i,root,stop=None):
   #    rows = [row for row in i.rows if row.use]
   #    row  = root.rows
   #    stop = len(rows)**the.min
   #    while len(rows) > stop:
   #       if candidates :=  [sheet for  root.nodes() if i.isCandidate(sheet)]:
   #          most = max(canidatates,key=i.score)
   #          i.dontUse(most.rights) if better(most.left, most.right) else i.dontUse(most.lefts)


#-------------------------------------------------------------
def cut(x, cuts)-> int | None :
      for cut1 in cuts:
         if true(x, cut1): return cut1

def true(x, cut): return x=="?" or cut[1]==cut[-1]==x or x > cut[1] and x <= cut[-1]

def ent(d):
  n = sum(d.values())
  return - sum(m/n*log(m/n,2) for m in d.values() if m > 0)
#-------------------------------------------------------------
big=1E30
def prin(x,decs=None):
  return x.__name__ if callable(x) else (round(x,decs) if decs and isinstance(x,float) else x)

def prints(*lst): print(*[prin(x,2) for x in lst],sep="\t")

def printds(*ds):
    prints(*ds[0].keys())
    for d in ds: prints(*d.values())

def printd(d,b4=""):
   return b4+"{" + " ".join([f":{k} {prin(v,3)}" for k,v in d.items() if k[0] != "_"]) + "}"
#-------------------------------------------------------------
def coerce(x):
   try : return ast.literal_eval(x)
   except Exception: return x.strip()

def csv(file="-", filter=ROW):
   with  fileinput.FileInput(file) as src:
      for line in src:
         line = re.sub(r'([\n\t\r"\' ]|#.*)', '', line)
         if line: yield filter([coerce(x) for x in line.split(",")])

random.seed(int(time.time() % 1 *1E9))
s= SHEET(csv(the.file))
[print(col) for col in s.cols.x]
printds(s.stats())
s.reset()
[print(x) for x in s.cuts.items()]
printds(s.ents())
