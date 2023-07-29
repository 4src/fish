#!/usr/bin/env python3 -B
# <!--- vim: set et sts=3 sw=3 ts=3 : --->
"""
litr:  little light deling
(c) Tim Menzies <timm@ieee.org>, BSD-2 license

OPTIONS:
  -c --cuts   initial number of cuts  = 16
  -C --Cohen  small if C*std         = .5
  -e --eg     start up example       = helps
  -f --file   csv data file          = ../data/auto93.csv
  -m --min    min size               = .5
  -p --p      distance coefficient   = 2
  -s --seed   random number seed     = 1234567891
  -r --rest   the rest               = 4
  -w --want   plan|avoid|doubt|xplor = plan
"""
from collections import defaultdict,Counter
from math import pi, log, cos, sin, sqrt, inf
import fileinput, random, time,ast, sys, re
#---------------------------------------------------------------
class obj(object):
   __repr__    = lambda i: showd(i.__dict__,i.__class__.__name__)

class slots(dict): 
   __getattr__ = dict.get
   __repr__ = lambda i:showd(i)

big  = 1E100

want = dict(plan  = lambda b,r : b**2/(b+r),
            avoid = lambda b,r: r**2/(b+r),
            doubt = lambda b,r: (b+r)/(abs(b-r) + 1/big),
            xplor = lambda b,r: 1/(b+r + 1/big))
#---------------------------------------------------------------
def cuts2Rule(cuts):
   d = defaultdict(list)
   [d[cut[0]].append(cut) for cut in cuts]
   return tuple(sorted([tuple(sorted(set(x))) for x in d.values()]))

def score(rule, d):
   got = selects(rule,d)
   b = len(got["best"]) / (len(d["best"]) + 1/big)
   r = len(got["rest"]) / (len(d["rest"]) + 1/big)
   return want[the.want](b,r)

def selects(rule, d)  : return {k: select(rule,rows) for k,rows in d.items()}
def select(rule, rows): return [row for row in rows if ands(rule,row)]

def ands(rule,row):
   for cuts in rule:
      if not ors(row[cuts[0][0]], cuts): return False
   return True

def ors(x, cuts):
   for cut in cuts:
      if true(x, cut): return cut

def true(x, cut): return x=="?" or cut[1]==cut[2]==x or x > cut[1] and x <= cut[2]
#---------------------------------------------------------------
class COL(obj):
   def __init__(i,a=[], name=" ", at=0):
      i.n, i.at, i.name = len(a), at, name
      i.adds(a)
   def adds(i,a=[]): [i.add(x) for x in a]; return i
   def add(i,x):
      if x !="?": i.n += 1; i.add1(x)
      return x
#---------------------------------------------------------------
class SYM(COL):
   def __init__(i,*l,**d):
      i.most,i.mode, i.has = 0, None, {}
      super().__init__(*l,**d)
   def mid(i): return mode(i.has)
   def div(i): return ent(i.has)
   def add1(i,x):
      new= i.has[x] = i.has.get(x,0) + 1
      if new > i.most: i.most,i.mode = new,x
   def cuts(i,_):
      for k in i.has: yield (i.at, k, k)
#---------------------------------------------------------------
class NUM(COL):
   def __init__(i,*l,**d):
      i.mu, i.m2, i.lo, i.hi = 0,0,big,-big
      super().__init__(*l,**d)
      i.heaven = 0 if i.name[-1] == "-" else 1
   def mid(i): return i.mu
   def div(i): return (i.m2/(i.n-1))**.5
   def distance2heaven(i,row): return i.heaven - i.norm(row[i.at])
   def norm(i,x): return "?" if x=="?" else (x- i.lo)/(i.hi - i.lo + 1/big)
   def add1(i,x):
      i.lo  = min(x, i.lo)
      i.hi  = max(x, i.hi)
      d     = x - i.mu
      i.mu += d/i.n
      i.m2 += d*(x - i.mu)
   def cuts(i,d):
      xys   = sorted([(row[i.at],y) for y,rows in d.items() for row in rows if row[i.at] != "?"])
      nmin  = len(xys)/(the.cuts - 1)
      xmin  = the.Cohen * i.div()
      now,b4= Counter(), Counter()
      out,lo= [], xys[0][0]
      for n,(x,y) in enumerate(xys):
         now[y] += 1
         if n < len(xys) - nmin and x != xys[n+1][0] and sum(now.values()) >= nmin and x-lo >= xmin:
            both = now + b4
            if out and ent(both) <= (ent(now)*now.total() + ent(b4)*b4.total()) / both.total():
               b4 = both
               out[-1][2] = x
            else:
               b4 = now
               out += [[i.at, lo, x]]
            lo  = x
            now = Counter()
      out = out or [[i.at,None,None]]
      out[ 0][1] = -inf
      out[-1][2] = inf
      for cut in out:
         yield tuple(cut)
#---------------------------------------------------------------
class SHEET(obj):
   def __init__(i, src):
     i.rows, i.names, i.cols = [], None, None
     [i.add(row) for row in src]

   def add(i,row):
      if i.cols:
         i.rows += [col.add(row[col.at]) for col in i.cols.all]
      else:
         i.cols  = i._cols(row)

   def _cols(i,row):
      x,y, all = [],[], [(NUM if s[0].isupper() else SYM)(at=n,name=s) for n,s in enumerate(row)]
      for col in all:
        if col.name[-1] != "X": 
           (y if col.name[-1] in "+-!" else x).append(col)
      return slots(x=x, y=y, names=row, all=all)

   def stats(i, cols="y", decimals=None, want="mid"):
      return slots(N=len(i.rows), **{c.name:show(c.div() if want=="div" else c.mid(),decimals) 
                                   for c in i.cols[cols]})

   def distance2heaven(i,row):
      return (sum((col.distance2heaven(row)**the.p for col in i.cols.y))
              / len(i.cols.y))**(1/the.p)

   def sorted(i): return sorted(i.rows, key=lambda row: i.distance2heaven(row))

   def clone(i, a=[]): return SHEET( [i.names] + a)
#---------------------------------------------------------------
def rules(sheet):
   rows = sheet.sorted()
   n = int(len(rows)**the.min)
   d= dict(best=rows[:n], rest=random.sample(rows[n:], n*the.rest))
   for col in sheet.cols.x:
      for cut in col.cuts(d):
         print(score(cuts2Rule([cut]),d),cut)
#---------------------------------------------------------------
def ent(d):   # measures diversity for symbolic distributions
   n = sum(d.values())
   return -sum(m/n * log(m/n,2) for m in d.values() if m>0)

def showd(d,pre=""):
   s = " ".join([f":{k} {show(v,3)}" for k,v in d.items() if k[0] != "_"])
   return pre + "{" + s + "}"

def show(x,decimals=None):
  if callable(x): return x.__name__
  if decimals is None or not isinstance(x,float): return x
  return round(x,decimals)
#---------------------------------------------------------------
def coerce(x):
   try : return ast.literal_eval(x)
   except Exception: return x.strip()

def csv(file="-"):
   with  fileinput.FileInput(file) as src:
      for line in src:
         line = re.sub(r'([\n\t\r"\' ]|#.*)', '', line)
         if line: yield [coerce(x) for x in line.split(",")]

def settings(s):
  return slots(**{m[1]:coerce(m[2])
                  for m in re.finditer( r"\n\s*-\w+\s*--(\w+).*=\s*(\S+)",s)})

def cli(d):
   for k, v in d.items():
      s = str(v)
      for j, x in enumerate(sys.argv):
         if ("-"+k[0])==x or ("--"+k)==x:
            d[k] = coerce("True" if s=="False" else ("False" if s=="True" else sys.argv[j+1]))
   return d
#---------------------------------------------------------------
funs=slots()

def fun(f):  funs[f.__name__] = f; return f

def run(fun):
   global the
   saved = {k:v for k,v in the.items()}
   random.seed(the.seed)
   if failed := fun() is False:
      print("❌ FAIL", fun.__name__)
   for k,v in saved.items(): the[k] = v
   return failed

@fun
def helps():
   "show help"
   print(__doc__,"\nACTIONS:")
   [print(f"  -e  {fun.__name__:7} {fun.__doc__}") for fun in funs.values()]

@fun
def alls():
   "run all"
   sys.exit(sum(map(run,[fun for s,fun in funs.items() if s != "alls"])))

@fun
def syms():
   "test sym"
   s=SYM(a="aaaabbc")
   print(s,s.div())

@fun
def thes(): 
   "print settings"
   print(the)

@fun
def csvs(): 
   "print a csv file"
   [print(row) for row in csv(the.file)]

@fun
def sheets(): 
   "load a csv file"
   s=SHEET(csv(the.file))
   print(s.stats())

@fun
def rulings():
   rules(SHEET(csv(the.file)))
#---------------------------------------------------------------
the=settings(__doc__)
if __name__ == "__main__":
   the=cli(the)
   helps() if the.help else run(funs.get(the.eg,helps))
