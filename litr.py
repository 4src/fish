#!/usr/bin/env python3 -B
# <!--- vim: set et sts=3 sw=3 ts=3 : --->
"""
litr:  little light deling
(c) Tim Menzies <timm@ieee.org>, BSD-2 license

OPTIONS:
  -e --eg     start up example       = helps
  -f --file   csv data file          = ../data/auto93.csv
  -m --min    min size               = .5
  -p --p      distance coefficient   = 2
  -s --seed   random number seed     = 1234567891
  -r --rest   the rest               = 3
  -w --want   plan|avoid|doubt|xplor = plan
"""
from collections import defaultdict
from math import pi, log, cos, sin, sqrt, inf
import fileinput, random, time,ast, sys, re
#---------------------------------------------------------------
big=1E100

want = dict(plan  = lambda b,r : b**2/(b+r),
            avoid = lambda b,r: r**2/(b+r),
            doubt = lambda b,r: (b+r)/(abs(b-r) + 1/big),
            xplor = lambda b,r: 1/(b+r + 1/big))

class slots(dict): 
   __getattr__ = dict.get
   __repr__ = lambda i:showd(i)

class obj(object):
   __repr__    = lambda i: showd(i.__dict__,i.__class__.__name__)

funs=slots()
def fun(f):  funs[f.__name__] = f; return f
#---------------------------------------------------------------
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
def cuts2Rule(cuts):
   d = defaultdict(list)
   [d[cut[0]].append(cut) for cut in cuts]
   return tuple(sorted([tuple(sorted(set(x))) for x in d.values()]))

def score(rule, d):
   got = selects(rule,d)
   b = got["best"] / (len(d["best"]) + 1/big)
   r = got["rest"] / (len(d["rest"]) + 1/big)
   return want[the.want](b,r)

def selects(rule, d)  : return {k: select(rule,rows) for k,rows in d}
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
   def __init__(i,a=[],name=" ",at=0):
      i.n, i.at, i.name = len(a), at, name
      i.adds(a)
   def adds(i,a=[]): [i.add(x) for x in a]; return i
   def add(i,x): 
      if x!="?": i.n += 1; i.add1(x)
      return x

class SYM(COL):
   def __init__(i,a=[],name=" ",at=0):
      i.most,i.mode, i.has = 0, None, {}
      super().__init__(a=a,name=name,at=at)
   def mid(i): return mode(i.has)
   def div(i): return -sum(n/i.n*log(n/i.n,2) for n in i.has.values() if n > 0)
   def add1(i,x): 
      new= i.has[x] = i.has.get(x,0) + 1
      if new > i.most: i.most,i.mode = new,x
   def cuts(i,j):
      for k,v1 in i.has.items():
        v2 = j.has.get(k,0)
        v1,v2 = v1/i.n, v2/j.n
        if v1 > v2: return (i.at, k, k)

@fun
def syms():
   "test sym"
   s=SYM(a="aaaabbc")
   print(s)

class NUM(COL):
   def __init__(i,a=[],name=" ",at=0):
      super().__init__(a=a,name=name,at=at)
      i.heaven = 0 if i.name[-1] == "-" else 1
      i.mu, i.m2, i.lo, i.hi = 0,0,big,-big
   def mid(i): return i.mu
   def div(i): return (i.m2/(i.n-1))**.5
   def add1(i,x):
      i.lo  = min(x, i.lo)
      i.hi  = max(x, i.hi)
      d     = x - i.mu
      i.mu += d/i.n
      i.m2 += d*(x - i.mu)
   def cuts(i,j):
      x1 = _cross(i,j)
      x2 = (i.mu+x1)/2
      x3 = abs(i.mu - x1)
      x4 = abs(i.mu - x2)
      cuts1= [(i.mu-x3, i.mu+x3), (i.mu-x4, i.mu+x4)]
      cuts2= [(x1, inf), (x2, inf)] if i.mu > j.mu else [(-inf, x1), (-inf, x2)]
      for lo,hi in cuts1+cuts2: yield (i.at, lo, hi)
   def distance2heaven(i,row): return i.heaven - i.norm(row[i.at])
   def norm(i,x): return "?" if x=="?" else (x- i.lo)/(i.hi - i.lo + 1/big)



def _cross(num1,num2):
   mu1, sd1 = num1.mid(), num1.div()
   mu2, sd2 = num2.mid(), num2.div()
   if mu2 < mu1: return _cross(num2, num1)
   if sd1==0 or sd2==0 or sd1==sd2: return (mu1+mu2)/2
   a  = 1/(2*sd1**2) - 1/(2*sd2**2)
   b  = mu2/(sd2**2) - mu1/(sd1**2)
   c  = mu1**2 /(2*sd1**2) - mu2**2 / (2*sd2**2) - log(sd2/sd1)
   x1 = (-b + (b**2 - 4*a*c)**.5)/(2*a)
   x2 = (-b - (b**2 - 4*a*c)**.5)/(2*a)
   return x1 if mu1 <= x1 <= mu2 else x2
#---------------------------------------------------------------
ako = slots(num  = lambda s: s[0].isupper(),
          goal = lambda s: s[-1] in "+-",
          skip = lambda s: s[-1] == "X",
          x    = lambda s: not ako.goal(s),
          xnum = lambda s: ako.x(s) and ako.num(s),
          xsym = lambda s: ako.x(s) and not ako.num(s))

class SHEET(obj):
   def __init__(i, src):
     i.rows, i.names, i.cols = [], None, None
     [i.add(row) for row in src]

   def add(i,row):
      if i.cols:
         i.rows += [[col.add(row[col.at]) for col in i.cols.all]]
      else:
         i.names = row
         i.cols= slots(all= [(NUM if ako.num(s) else SYM)(at=n,name=s) for n,s in enumerate(i.names)])
         for k,fun in ako.items():
            i.cols[k] = [col for col in i.cols.all if not ako.skip(col.name) and fun(col.name)]

   def stats(i, cols="goal", decimals=None, want="mid"):
      return slots(N=len(i.rows), **{c.name:show(c.div() if want=="div" else c.mid(),decimals) 
                                   for c in i.cols[cols]})

   def distance2heaven(i,row):
      return (sum((col.distance2heaven(row)**the.p for col in i.cols.goal))
              / len(i.cols.goal))**(1/the.p)

   def sorted(i): return sorted(i.rows, key=lambda row: i.distance2heaven(row))

   def clone(i, a=[]): return SHEET( [i.names] + a)
#---------------------------------------------------------------
def rules(sheet):
   rows = sheet.sorted()
   n = int(len(rows)**the.min)
   bests,rests =  rows[:n], random.sample(rows[n:], n*the.rest)
   bests,rests = sheet.clone(bests), sheet.clone(rests)
   print(sheet.stats())
   print(bests.stats())
   print(rests.stats())
   for best,rest in zip(bests.cols.x,rests.cols.x):
      for cut in best.cuts(rest):
         print(cut)

#---------------------------------------------------------------
def run(fun):
   global the
   saved = {k:v for k,v in the.items()}
   random.seed(the.seed)
   failed = fun() is False
   print("❌ FAIL" if failed else "✅ OK", fun.__name__)
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
