#!/usr/bin/env python3
# <!--- vim: set et sts=3 sw=3 ts=3 : --->
"""
BS: broomstick optimization
(c) 2023 Tim Menzies <timm@ieee.org> BSD-2

USAGE:
  ./bs.py -h [OPTIONS] -e [ACTIONS]

OPTIONS:
  -e --eg       start-up example     =  "nothing"
  -f --file     file of data         = "../data/auto93.csv"
  -h --help     show help            = False
  -m --min      smallest lead        = .5
  -p --p        distance coefficient = 2
  -r --rest     ratio rest:best      = 3
  -s --seed     random seed          = 1234567891 """
#--------------------------------------------------
from ast import literal_eval as thing
from collections import Counter
import fileinput,random,sys,re
from math import log

class obj(object):
   __repr__ = lambda i: showd(i.__dict__,i.__class__.__name__)

class slots(dict):
   "For dictionaries where we access slots via (e.g.) `x.slot`."
   def __repr__(i): return showd(i)
   __getattr__ = dict.get

the= slots(**{m[1]:thing(m[2]) for m in re.finditer(r"\n\s*-\w+\s*--(\w+).*=\s*(\S+)",__doc__)})
#---------------------------------------------------------------
class COL(obj):
   def __init__(i,a=[], name=" ", at=0):
      i.n, i.at, i.name = len(a), at, name
      i.adds(a)
   def adds(i,a=[]): [i.add(x) for x in a]; return i
   def add(i,x):
      if x !="?": i.n += 1; i.add1(x)
      return x
   def dist(i,x,y):
     return 1 if x=="?" and y=="?" else i.dist1(x,y)
#---------------------------------------------------------------
class SYM(COL):
   def __init__(i,*l,**d) : i.has =  Counter(); super().__init__(*l,**d)
   def mid(i)             : return i.has.most_common(1)[0][0]
   def div(i)             : return ent(i.has)
   def dist1(i,x,y)       : return 0 if x==y else 1
   def add1(i,x)          : i.has[x] += 1
#---------------------------------------------------------------
class NUM(COL):
   def __init__(i,*l,**d):
      i.mu, i.m2, i.lo, i.hi = 0,0,big,-big
      super().__init__(*l,**d)
      i.heaven = 0 if i.name[-1] == "-" else 1
   def mid(i)         : return i.mu
   def div(i)         : return (i.m2/(i.n-1))**.5
   def toHeaven(i,row): return abs(i.heaven - i.norm(row.cells[i.at]))
   def norm(i,x)      : return "?" if x=="?" else (x- i.lo)/(i.hi - i.lo + 1/big)
   def dist1(i,x,y):
      x,y = i.norm(x), i.norm(y)
      if x=="?": x= 0 if y > .5 else 1 # for unknowns, assume max distance
      if y=="?": y= 0 if x > .5 else 1
      return abs(x - y)
   def add1(i,x):
      i.lo  = min(x, i.lo)
      i.hi  = max(x, i.hi)
      d     = x - i.mu
      i.mu += d/i.n
      i.m2 += d*(x - i.mu)
#---------------------------------------------------------------
class ROW(obj):
   id=0
   def __init__(i,a):
      ROW.id +=1
      i.oid, i.cells = ROW.id, a
   def toHeaven(i,cols):
      return (sum((col.toHeaven(i)**the.p for col in cols)) / len(cols))**(1/the.p)
#---------------------------------------------------------------
def COLS(a):
   x,y = [],[]
   all = [(NUM if s[0].isupper() else SYM)(at=n,name=s) for n,s in enumerate(a)]
   for col in all:
      if col.name[-1] != "X": (y if col.name[-1] in "+-" else x).append(col)
   return slots(x=x, y=y, names=a, all=all)
#---------------------------------------------------------------
class SHEET(obj):
   def __init__(i, src):
      i.rows, i.cols = [], None
      [i.add(row) for row in src]

   def add(i,row):
      if i.cols:
         [col.add(row.cells[col.at]) for col in i.cols.all]
         i.rows += [row]
      else:
         i.cols = COLS(row.cells)

   def clone(i,rows=[]): return SHEET([ROW(i.cols.names)] + rows)

   def sorted(i):
      return sorted(i.rows,key=lambda row: row.toHeaven(i.cols.y) )

   def stats(i, cols="y", decimals=None, want="mid"):
      return slots(N=len(i.rows), **{c.name:show(c.mid() if want=="mid" else c.div(),decimals)
                                     for c in i.cols[cols]})

   def dist(i,row1,row2):
      return (sum(c.dist(row1.cells[c.at],row2.cells[c.at])**the.p for c in i.cols.x)
              / len(i.cols.x))**(1/the.p)
#-------------------------------------------
def broomstick(sheet,budget=20):
   used={}
   def some(a) : return random.sample(a,k=len(a)//2)
   def D(r1,r2): return sheet.dist(r1,r2)
   def say(x): print(x,end="",flush=True)
   def better(r1,r2):
      used[r1.oid] = used[r2.oid] = True
      return r1.toHeaven(sheet.cols.y) < r2.toHeaven(sheet.cols.y)
   def cosine(r): return (D(r,worst)**2  + c**2 - D(r,best)**2)/ (2*c + 1/big)
   random.shuffle(sheet.rows)
   best,worst = sheet.rows[:2]
   policy = max
   c= None
   for _ in range(budget):
     if better(worst,best):
        best,worst = worst,best
     c  = D(best,worst)
     tmp = policy(some(sheet.rows),  key=cosine)
     if better(tmp,best) : say("+"); best=tmp
     if better(worst,tmp): say("-"); worst=tmp
     policy =  max if policy==min else min
   print(len(used))
   return sorted(sheet.rows, key=cosine, reverse=True)
#-------------------------------------------
big = 1E100
def ent(d):   # measures diversity for symbolic distributions
   n = sum(d.values())
   return -sum(m/n * log(m/n,2) for m in d.values() if m>0)

def prints(*l,**key): print(*[show(x,2) for x in l],sep="\t",**key)

def printd(**ds):
   first = True
   for k,d in ds.items(): 
      if first: prints("",*d.keys())
      first=False
      prints(k,*d.values())

def showd(d,pre=""):
   return pre+"{"+(" ".join([f":{k} {show(v,3)}" for k,v in d.items() if k[0] != "_"]))+"}"

def show(x,decimals=None):
   if decimals and isinstance(x,float): return round(x,decimals)
   return x.__name__ if callable(x) else x

def coerce(x):
   try : return thing(x)
   except Exception: return x.strip()

def csv(file="-",filter=ROW):
   with  fileinput.FileInput(file) as src:
      for line in src:
         line = re.sub(r'([\n\t\r"\' ]|#.*)', '', line)
         if line: yield filter([coerce(x) for x in line.split(",")])

def cli(d):
   for k, v in d.items():
      s = str(v)
      for j, x in enumerate(sys.argv):
         if ("-"+k[0])==x or ("--"+k)==x:
            d[k] = coerce("True" if s=="False" else ("False" if s=="True" else sys.argv[j+1]))
   return d
#-------------------------------------------
def run(settings, funs, pre="eg_", all="all"):
   n    = len(pre)
   todo = settings.eg
   funs = {s:fun for s,fun in funs.items() if s[:n]==pre}
   def one(todo):
      if fun := funs.get(pre+todo, None):
         saved = {k:v for k,v in settings.items()}
         random.seed(the.seed)
         if failed := fun() is False: print("❌ FAIL", todo.upper())
         for k,v in saved.items(): settings[k] = v
         return failed
      else:
         print(f"Unknown; [{todo}]")
   if settings.help:
      print(__doc__+"\n\nACTIONS:\n  -e all\trun all actions")
      [print(f"  -e {s[n:]}\t{fun.__doc__}") for s,fun in funs.items() if fun.__doc__]
   else: 
      sys.exit(sum((one(s[n:]) for s in funs)) if todo==all else one(todo))

def eg_nothing(): ...
def eg_the():
   "show settings"
   print(the)

def eg_csv():
   "show rows"
   print("")
   for n,row in enumerate(csv(the.file)): 
      if n % 32 == 0: prints(*row.cells)

def eg_cols():
   "show columns"
   print("")
   [print(col) for col in SHEET(csv(the.file)).cols.x]

def eg_clone():
   "duplicate a SHEET structure"
   print("")
   s = SHEET(csv(the.file))
   print( s.cols.y[1])
   print( s.clone(s.rows).cols.y[1])

def eg_sheet():
   "print stats on best and other rows"
   print("")
   s    = SHEET(csv(the.file))
   rows = s.sorted()
   n    = int(len(rows)**the.min)
   bests, rests = s.clone(rows[:n]), s.clone(rows[-n*the.rest:])
   printd(all= s.stats(), bests=bests.stats(), rests=rests.stats())

def eg_broomstick():
   "try broomstick optimizer"
   print("")
   s = SHEET(csv(the.file))
   rows = broomstick(s)
   n    = int(len(rows)**the.min)
   bests, rests = s.clone(rows[:n]), s.clone(rows[-n*the.rest:])
   printd(all= s.stats(), bests=bests.stats(), rests=rests.stats())

#-------------------------------------------
run(cli(the),locals())
