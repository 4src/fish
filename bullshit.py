#!/usr/bin/env python3 -B
# <!--- vim: set et sts=3 sw=3 ts=3 : --->
"./bullshit.py -h [OPTIONS] -e [ACTIONS]"
from collections import Counter
import fileinput,random,ast,sys,re

class obj(object):
   def __repr__(i): return showd(i.__dict__,i.__class__.__name__)

class slots(dict):
   "For dictionaries where we access slots via (e.g.) `x.slot`."
   def __repr__(i): return showd(i)
   __getattr__ = dict.get

the=slots(eg   = "usage",
          file = "../data/auto93.csv",
          p    = 2,
          seed = 1234567891)
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
   def __init__(i,*l,**d):
      i.most,i.mode, i.has = 0, None, Counter()
      super().__init__(*l,**d)
   def dist1(i,x,y): return 0 if x==y else 1
   def add1(i,x):
      i.has[x] += 1
      if i.has[x] > i.most: i.most,i.mode = i.has[x],x
#---------------------------------------------------------------
class NUM(COL):
   def __init__(i,*l,**d):
      i.mu, i.m2, i.lo, i.hi = 0,0,big,-big
      super().__init__(*l,**d)
      i.heaven = 0 if i.name[-1] == "-" else 1
   def fromHeaven(i,row): return i.heaven - i.norm(row.cells[i.at])
   def norm(i,x): return "?" if x=="?" else (x- i.lo)/(i.hi - i.lo + 1/big)
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
#---------------------------------------------------------------
class ROW(obj):
   id=0
   def __init__(i,a): ROW.id +=1; i.oid = ROW.id; i.cells=a
   def fromHeaven(i,cols):
      return (sum((col.fromHeaven(i)**the.p for col in cols)) / len(cols))**(1/the.p)
#---------------------------------------------------------------
def COLS(a):
   x,y,all = [],[],[(NUM if s[0].isupper() else SYM)(at=n,name=s) for n,s in enumerate(a)]
   for col in all:
      if col.name[-1] != "X": (y if col.name[-1] in "+-" else x).append(col)
   return slots(x=x, y=y, names=a, all=all)
#---------------------------------------------------------------
class SHEET(obj):
   def __init__(i, src):
      i.rows, i.cols = [], None
      [i.add(row) for row in src]

   def add(i,row):
      if not i.cols: i.cols = COLS(row.cells) 
      else:
         [col.add(row.cells[col.at]) for col in i.cols.all]
         i.rows += [row]

   def clone(i,rows=[]): return SHEET([ROW(i.cols.name)] + rows)

   def sorted(i):
      return sorted(i.rows,key=lambda row: row.fromHeaven(i.cols.y) )
#-------------------------------------------
big = 1E100
def prints(*l,**key): print(*[show(x,2) for x in l],sep="\t",**key)

def showd(d,pre=""):
   return pre+"{"+(" ".join([f":{k} {show(v,3)}" for k,v in d.items() if k[0] != "_"]))+"}"

def show(x,decimals=None):
   if decimals and isinstance(x,float): return round(x,decimals)
   return x.__name__ if callable(x) else x

def coerce(x):
   try : return ast.literal_eval(x)
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
         print(todo.upper(), end=": ")
         if failed := fun() is False: 
            print("❌ FAIL", todo.upper())
         for k,v in saved.items(): settings[k] = v
         return failed
   sys.exit(sum((one(s[n:]) for s in funs)) if todo==all else one(todo))

def eg_usage(): print(__doc__)
def eg_the(): print(the)

def eg_cols():
   print("")
   [print(col) for col in SHEET(csv(the.file)).cols.x]

def eg_sheet():
   print("")
   s = SHEET(csv(the.file))
   rows = s.sorted()
   prints(*s.cols.names)
   [prints(*row.cells) for row in rows[:8]]; print("")
   [prints(*row.cells) for row in rows[-8:]]

def eg_csv():
   print("")
   for n,row in enumerate(csv(the.file)): 
      if n % 32 == 0: prints(*row.cells)
#-------------------------------------------
run(cli(the),locals())

