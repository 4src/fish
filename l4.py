#!/usr/bin/env python3 -B
# <!--- vim: set et sts=3 sw=3 ts=3 : --->
"""
l4: a little light learning laboratory
(c) Tim Menzies <timm@ieee.org>, BSD-2 license

OPTIONS:
  -B --Bootstraps  number of bootstraps   = 256
  -b --bins        initial number of bins = 16
  -c --cliffs      Cliff's delta          = 0.147
  -C --Cohen       small if C*std         = .35
  -e --eg          start up example       = nothing
  -f --file        csv data file          = ../data/auto93.csv
  -F --Far         how far to look        = .85
  -h --help        show help              = False
  -H --Halves      where to find for far  = 512
  -m --min         min size               = .5
  -p --p           distance coefficient   = 2
  -s --seed        random number seed     = 1234567891
  -r --rest        the rest               = 3
  -t --top         only explore top cuts  = 8
  -w --want        plan|avoid|doubt|xplor = plan
"""
from collections import defaultdict,Counter
from termcolor import colored
from math import pi, log, cos, sin, sqrt, inf
from math import e as euler
import fileinput, random, time,ast, sys, re
#---------------------------------------------------------------
class slots(dict): __getattr__ =dict.get; __repr__ =lambda i:showd(i)
class obj(object):                        __repr__ =lambda i:showd(i.__dict__, i.__class__.__name__)

big  = 1E100
want = dict(plan  = lambda b,r : b**2  / (b + r    + 1/big),
            avoid = lambda b,r : r**2  / (b + r    + 1/big),
            doubt = lambda b,r : (b+r) / (abs(b-r) + 1/big),
            xplor = lambda b,r : 1     / (b+r      + 1/big))
#---------------------------------------G------------------------
def dull(cut): return cut[1] == -inf and cut[2] == inf

def cuts2Rule(cuts):
   d0 = defaultdict(set)
   [d0[cut[0]].add(cut) for cut in cuts]
   return tuple(sorted([tuple(sorted(x)) for x in d0.values()]))
   # d = {}
   # for k,v0 in d0.items():
   #    if v := canonicalCuts(v0): d[k]= v
   # if d:
   #    return tuple(sorted([tuple(sorted(x)) for x in d.values()]))

def canonicalCuts(cuts):
   out=[]
   for at,lo,hi in sorted(cuts):
      #print(at,lo,hi)
      if out and out[-1][-1] == lo: out[-1][-1] == hi
      else: out +=  [[at,lo,hi]]
   #print(at,out, dull(out[0]))
   if not dull(out[0]): return out

def score(rule, d):
   got = selects(rule,d)
   b = len(got["best"]) / (len(d["best"]) + 1/big)
   r = len(got["rest"]) / (len(d["rest"]) + 1/big)
   return want[the.want](b,r)

def selects(rule, d)  : return {k: select(rule,rows) for k,rows in d.items()}
def select(rule, rows): return [row for row in rows if ands(rule,row)]

def ands(rule,row):
   for cuts in rule:
      if not ors(row.cells[cuts[0][0]], cuts): return False
   return True

def ors(x, cuts):
   for cut in cuts:
      if true(x, cut): return cut

def true(x, cut): return x=="?" or cut[1]==cut[2]==x or x > cut[1] and x <= cut[2]

def showRule(names,rule):
   def show(a,b): return f"{a}" if a==b else f"({a} .. {b}]"
   str = lambda cuts: ' or '.join([show(cut[1],cut[2]) for cut in cuts])
   return ' and '.join([f"{names[cuts[0][0]]}: ({str(cuts)})" for cuts in rule])

def combineRules(rules):
   return cuts2Rule((cut for rule in rules for cuts in rule for cut in cuts))
#---------------------------------------------------------------
class COL(obj):
   def __init__(i,a=[], name=" ", at=0):
      i.n, i.at, i.name = 0, at, name
      i.adds(a)
   def adds(i,a=[]): [i.add(x) for x in a]; return i
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
   def cuts(i,_,supervised=None):
      for k in i.has: yield (i.at, k, k)
   def diff(i,j,x,y):
      return False if (x=="?" or y=="?") else x!=y
#---------------------------------------------------------------
class NUM(COL):
   def __init__(i,*l,**d):
      i.mu, i.m2, i.lo, i.hi = 0,0,big,-big
      super().__init__(*l,**d)
      i.heaven = 0 if i.name[-1] == "-" else 1
   def mid(i): return i.mu
   def div(i): return (i.m2/(i.n-1))**.5
   def distance2heaven(i,row): return abs(i.heaven - i.norm(row.cells[i.at]))
   def norm(i,x): return "?" if x=="?" else (x- i.lo)/(i.hi - i.lo + 1/big)
   def diff(i,j,x,y):
      if (x=="?" or y=="?"): return False
      return  abs(x-y)/i.pooled(j) > the.Cohen
   def dist1(i,x,y):
      x,y = i.norm(x), i.norm(y)
      if x=="?": x= 0 if y > .5 else 1
      if y=="?": y= 0 if x > .5 else 1
      return abs(x - y)
   def add1(i,x):
      i.lo = min(x, i.lo)
      i.hi = max(x, i.hi)
      d    = x - i.mu
      i.mu += d/i.n
      i.m2 += d*(x - i.mu)
   def pooled(i,j):
      return sqrt(((i.n-1)*i.div()**2 + (j.n-1)*j.div()**2)/(i.n + j.n - 2))
   def cuts(i,d,supervised=True):
      xys   = sorted([(row.cells[i.at],y) for y,rows in d.items()
                      for row in rows if row.cells[i.at] != "?"])
      nmin  = len(xys)/(the.bins - 1)
      xmin  = the.Cohen * i.div()
      now,b4= Counter(), Counter()
      out,lo= [], xys[0][0]
      for n,(x,y) in enumerate(xys):
         now[y] += 1
         if n < len(xys) - nmin and x != xys[n+1][0] and sum(now.values()) >= nmin and x-lo >= xmin:
            both = now + b4
            if supervised and out:
               if ent(both) <= (ent(now)*now.total() + ent(b4)*b4.total()) / both.total():
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
class ROW(obj):
   id = 0
   def __init__(i,a): 
      ROW.id += 1
      i.oid, i.cells = ROW.id, a
   def __hash__(i): return i.oid

def COLS(a):
   all = [(NUM if s[0].isupper() else SYM)(at=n,name=s) for n,s in enumerate(a)]
   x,y = [],[]
   for col in all:
      if col.name[-1] != "X":
        (y if col.name[-1] in "+-!" else x).append(col)
   return slots(x=x, y=y, names=a, all=all)

class SHEET(obj):
   def __init__(i, src):
     i.rows, i.cols = [],  None
     [i.add(row) for row in src]

   def add(i,row):
      if    i.cols:
              i.rows += [row]
              [col.add(row.cells[col.at]) for col in i.cols.all]
      else: i.cols = COLS(row.cells)

   def stats(i, cols="y", decimals=None, want="mid"):
      return slots(N=len(i.rows),
                   **{c.name:show(c.div() if want=="div" else c.mid(),decimals)
                      for c in i.cols[cols]})

   def distance2heaven(i,row):
      return (sum((abs(col.distance2heaven(row))**the.p for col in i.cols.y))
              / len(i.cols.y))**(1/the.p)

   def sorted(i): return sorted(i.rows, key=lambda row: i.distance2heaven(row))

   def clone(i, a=[]): return SHEET([ROW(i.cols.names)] + a)

   def dist(i,row1,row2):
      return (sum(c.dist(row1.cells[c.at],row2.cells[c.at])**the.p 
                  for c in i.cols.x )/len(i.cols.x))**(1/the.p)

   def mode(i,cols=None):
      return ROW([col.mid() for col in cols or i.cols.all])

   def cohen(rx0,rx): # k is based
      nums = lambda col,x: [row.cells[col.at] 
                            for row in x.rows if row.cells[col.at] != "?"]
      def report(col0,col):
         n0 = nums(col0,rx0)
         n = nums(col0,rx)
         mu0 = NUM(n0).mu
         mu = NUM(n).mu
         sd  = col0.pooled(col)
         return   ((mu0 - mu) if col.heaven == 0 else (mu - mu0))/sd
      return slots(N = len(rx0.rows)+len(rx.rows), 
                   **{col0.name: show(report(col0,col),2)
                      for col0,col in zip(rx0.cols.y,rx.cols.y)})

   def different(rx0,rx): # k is based
      nums = lambda col,x: [row.cells[col.at] for row in x.rows if row.cells[col.at] != "?"]
      def report(col0,col):
         n0 = nums(col0,rx0)
         n = nums(col0,rx)
         return different(n0,n)
      return slots(N = len(rx0.rows)+len(rx.rows), 
                   **{col0.name: report(col0,col)
                      for col0,col in zip(rx0.cols.y,rx.cols.y)})

#---------------------------------------------------------------
def top(a,**d): return sorted(a,reverse=True,**d)[:the.top]

def rules(sheet,every=True):
   balance = lambda cuts: val(cuts)
   #balance = lambda cuts: ((0-val(cuts))**2 + (1-len(cuts)/len(some))**2)**.5
   n    = int(len(sheet.rows)**the.min)
   if every:
      rows = sheet.sorted()
      d = dict(best=rows[:n], rest=random.sample(rows[n:], n*the.rest))
   else:
      best,rest,evals = TREE(sheet).branch()
      #d  = dict(best=best.rows, rest=rest.rows) #random.sample(rest.rows, n*the.rest))
      d  = dict(best=best.rows, rest=random.sample(rest.rows, n*the.rest))
   def val(cuts): return score(cuts2Rule(cuts),d)
   #  if rule := cuts2Rule(cuts): return score(rule, d)
   #  else: return 0
   all  = [cut for col in sheet.cols.x for cut in col.cuts(d)]
   some = top(all, key=lambda c: val([c]))
   return top((cuts for cuts in powerset(some)), key=lambda z: balance(z))
#---------------------------------------------
class TREE:
   def __init__(i, sheet):
      i.sheet = sheet
      i.stop  = int(len(sheet.rows)**the.min)
      i.lefts = i.rights = None

   def _far(i,rows,row1):
      _dist = lambda row2: i.sheet.dist(row1,row2)
      return sorted(rows, key=_dist)[int(len(rows)*the.Far)]

   def _halve(i,rows,assess=False):
      some = rows if len(rows) <= the.Halves else random.sample(rows,k=the.Halves)
      D    = lambda row1,row2: i.sheet.dist(row1,row2)
      anywhere = random.choice(some)
      a = i._far(some, random.choice(some))
      b = i._far(some, a)
      C = D(a,b)
      half1, half2 = [],[]
      if  assess and i.sheet.distance2heaven(b) < i.sheet.distance2heaven(a):
        a,b=b,a
      rows = sorted(rows, key=lambda r: (D(r,a)**2 + C**2 - D(r,b)**2)/(2*C))
      mid  = len(rows)//2
      return a,b,rows[:mid],rows[mid:]

   def tree(i,verbose=False,assess=False):
      def _grow(rows):
         here = i.sheet.clone(rows)
         here.lefts, here.rights = None,None
         if len(rows) >= 2*i.stop:
            _,__,lefts,rights = i._halve(rows,assess=True)
            here.lefts  = _grow(lefts)
            here.rights = _grow(rights)
         return here
      return _grow(i.sheet.rows)

   def branch(i):
      used,rest = {},[]
      def _grow(rows):
         if len(rows) >= 2*i.stop:
            left,right,lefts,rights = i._halve(rows,assess=True)
            used[left.oid] = used[right.oid] = True
            if len(lefts)  != len(rows):
               while rights: rest.append( rights.pop())
               return _grow(lefts)
         return i.sheet.clone(rows), i.sheet.clone(rest), used
      return _grow(i.sheet.rows)

   def showTree(i, here, lvl=0):
      if not here: return
      s = here.stats()
      if lvl==0: prints(' '*23,*s.keys())
      print(f"{'|.. '*lvl:24}",end="")
      if lvl==0: prints(*s.values(),end="")
      if not here.lefts and not here.rights:
         prints(*s.values())
      else:
         print("")
         i.showTree(here.lefts, lvl+1)
         i.showTree(here.rights,lvl+1)

   def nodes(i,here,depth=1):
      if here:
         yield here,depth
         for  t1 in [here.lefts,here.rights]:
            for here1,depth1 in i.nodes(t1, depth+1):
               yield here1,depth1

#---------------------------------------------------------------
def different(x,y):
  if len(x) > 1000: x = random.choices(x, k=1000)
  if len(y) > 1000: y = random.choices(y, k=1000)
  return cliffsDelta(x,y) and bootstrap(x,y)

def cliffsDelta(x,y):
   if len(x) > 10*len(y) : return cliffsDelta(random.choices(x,k=10*len(y)),y)
   if len(y) > 10*len(x) : return cliffsDelta(x, random.choices(y,k=10*len(x)))
   n,lt,gt = 0,0,0
   for x1 in x:
      for y1 in y:
         n = n + 1
         if x1 > y1: gt = gt + 1
         if x1 < y1: lt = lt + 1
   return abs(lt - gt)/n > the.cliffs # true if different

def bootstrap(y0,z0,conf=.05):
   obs= lambda x,y: abs(x.mid()-y.mid()) / ((x.div()**2/x.n + y.div()**2/y.n)**.5 + 1/big)
   x, y, z = NUM(y0+z0), NUM(y0), NUM(z0)
   d = obs(y,z)
   yhat = [y1 - y.mid() + x.mid() for y1 in y0]
   zhat = [z1 - z.mid() + x.mid() for z1 in z0]
   n      = 0
   for _ in range(the.Bootstraps):
      ynum = NUM(random.choices(yhat,k=len(yhat)))
      znum = NUM(random.choices(zhat,k=len(zhat)))
      if obs(ynum, znum) > d:
         n += 1
   return n / the.Bootstraps < conf # true if different
#---------------------------------------------------------------
R=random.random
def printd(*d,**key):
   prints(*list(d[0].keys()),**key)
   [prints(*d1.values(),**key) for d1 in d]

def prints(*l,**key): print(*[show(x,2) for x in l],sep="\t",**key)

def powerset(s):
  x = len(s)
  for i in range(1 << x):
     if tmp :=  [s[j] for j in range(x) if (i & (1 << j))]: yield tmp

def ent(d):   # measures diversity for symbolic distributions
   n = sum(d.values())
   return -sum(m/n * log(m/n,2) for m in d.values() if m>0)

def showd(d,pre=""):
   bold = lambda **d: colored(list(d.values())[0],list(d.keys())[0],attrs=['bold'])
   pre  = bold(white=pre)
   s = " ".join([f"{bold(red=':'+str(k))} {show(v,3)}" for k,v in d.items() if k[0] != "_"])
   return pre + bold(red="{") + s + bold(red="}")

def show(x,decimals=None):
  if callable(x): return x.__name__
  if decimals is None or not isinstance(x,float): return x
  return round(x,decimals)
#---------------------------------------------------------------
def coerce(x):
   try : return ast.literal_eval(x)
   except Exception: return x.strip()

def csv(file="-", filter=ROW):
   with  fileinput.FileInput(file) as src:
      for line in src:
         line = re.sub(r'([\n\t\r"\' ]|#.*)', '', line)
         if line: yield filter([coerce(x) for x in line.split(",")])

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
def egs(the,doc,funs):
   funs = {k[3:]: fun for k,fun in funs.items() if callable(fun) and k[:3] == "eg_"}
   if   the.help                     : eg_Help(doc,funs)
   elif the.eg == "nothing"          : ...
   elif the.eg == "All"              : sys.exit(eg_All(funs))
   elif fun := funs.get(the.eg,None) : sys.exit(eg(the.eg, fun))
   else                              : print(f"❌ FAIL : [{the.eg}] unknown action")

def eg(name,fun):
   saved = {k:v for k,v in the.items()}
   random.seed(the.seed)
   if failed := fun() is False: print("❌ FAIL", name)
   for k,v in saved.items(): the[k] = v
   return failed

def eg_All(funs): 
   "run all"
   return sum([eg(s,f) for s,f in funs.items() if s[0].islower()])

def eg_Help(doc,funs):
   print(doc,"\nACTIONS:")
   [print(f"  -e  {fun.__name__[3:]:12} {fun.__doc__}") for fun in funs.values()]

def eg_syms():
   "test sym"
   s=SYM(a="aaaabbc")
   print(s,s.div())

def eg_nums1():
   "test nums"
   n = NUM([2,1,3,2,4])
   return  (2.35 < n.mu < 2.45 and 1.14 < n.div() < 1.15)

def eg_nums2():
   "test nums"
   normal = lambda mu,sd: mu+sd*sqrt(-2*log(R())) * cos(2*pi*R())
   n = NUM([normal(10,2) for _ in range(1000)])
   return 9.9 <= n.mu <= 10.1 and 1.9 <= n.div() <= 2.1

def eg_thes():
   "print settings"
   print(the)

def eg_boots():
   normal= lambda mu,sd: mu+sd*sqrt(-2*log(R())) * cos(2*pi*R())
   yn    = lambda x: "y" if x else "."
   mu,sd = 10,1
   a = [normal(mu,sd) for _ in range(64)]
   numa=NUM(a)
   seed=the.seed
   r = 0
   prints("r","a.mu","b.mu","cliffs","boot","c+b","cohen(.35)")
   while r <= 3:
      b = [normal(mu+r,3*sd) for _ in range(64)]
      numb=NUM(b)
      prints(r,mu,f"{mu+r}", yn(cliffsDelta(a,b)),yn(bootstrap(a,b)),
                           yn(different(a,b)),
                           yn(abs(numb.mu - numa.mu)/numb.pooled(numa) > .35))
      r += .25
   print(seed)

def eg_csvs():
   "print a csv file"
   [print(row) for row in csv(the.file)]

def eg_sheets():
   "load a csv file"
   s=SHEET(csv(the.file))
   print(s.stats())
   rows = s.sorted()
   for i in range(1,len(rows),10): print(rows[i])

def eg_rulings(): 
   s= SHEET(csv(the.file))
   stats=s.stats()
   prints(*stats.keys())
   prints(*stats.values())
   for n,cuts in enumerate(rules(s)):
      rule = cuts2Rule(cuts)
      prints(*s.clone(select(rule,s.rows)).stats().values(),showRule(s.cols.names,rule))

def eg_treeings(): 
   s= SHEET(csv(the.file))
   stats=s.stats()
   prints(*stats.keys())
   prints(*stats.values())
   for n,cuts in enumerate(rules(s,every=True)):
      rule = cuts2Rule(cuts)
      prints(*s.clone(select(rule,s.rows)).stats().values(),
             showRule(s.cols.names,rule))

def eg_Bests():
   print("\n",the.file)
   s_base = SHEET(csv(the.file))
   stats_base = s_base.stats()
   prints("",*stats_base.keys())
   prints("a=base",*stats_base.values())
   rows     = s_base.sorted()
   n        = int(len(rows)**the.min)
   with_raw = rows[:n]
   s_raw    = s_base.clone(with_raw)
   prints("b=raw",*s_raw.stats().values(),end="")
   with_all=[]
   with_some=[]
   with_any=[]
   for i in range(20):
     with_any += random.sample(s_base.rows,k=n)
     with_all += _egbests(i,True)     # instance based
     with_some += _egbests(i,False) # rilebased
   print("")
   s_all = s_base.clone(with_all)
   s_any  = s_base.clone(with_any)
   s_some = s_base.clone(with_some)
   prints("c=all",  *s_all.stats().values())
   prints("d=any",  *s_any.stats().values())
   prints("e=some", *s_some.stats().values())
   prints("(b-a)/s",*s_base.cohen(s_raw).values())
   prints("(c-a)/s",*s_base.cohen(s_all).values())
   prints("(d-a)/s",*s_base.cohen(s_any).values())
   prints("(e-a)/s",*s_base.cohen(s_some).values())
   prints("(e-c)/s",*s_some.cohen(s_all).values())
   prints("e!=c?",  *s_some.different(s_all).values())

def _egbests(i,every=True):
   print(str(chr(97+i)), end="",flush=True)
   s = SHEET(csv(the.file))
   return select( cuts2Rule(rules(s,every)[0]), s.rows)

def eg_dists():
   "check distances between random cols in random rows"
   sheet= SHEET(csv(the.file))
   rows=sheet.rows
   c= random.choice
   a=[]
   for _ in range(30):
       col = c(sheet.cols.x + sheet.cols.y)
       z1  = c(rows).cells[col.at]
       z2  = c(rows).cells[col.at]
       a  += [(show(col.dist(z1, z2),3), z1,z2,col.name)]
   prints("dist","x1","x2","what")
   [prints(*x) for x in sorted(a)]

def eg_trees():
   "can we divide the data into best and rest?"
   sheet= SHEET(csv(the.file))
   rows = sheet.rows
   t = TREE(sheet)
   t.showTree(t.tree())

def eg_branches():
   "can we divide the data into best and rest?"
   sheet= SHEET(csv(the.file))
   best,rest,evals = TREE(sheet).branch()
   printd(sheet.stats(),
          best.stats(),
          rest.stats())

def eg_ents():
  s = SHEET(csv(the.file))
  e = 0
  for col in s.cols.x:
     cuts = list(col.cuts(slots(all=s.rows),supervised=False))
     seen = Counter()
     for row in s.rows:
       x = row.cells[col.at]
       if x != "?": seen[ ors(x, cuts) ] += 1
     e += ent(seen)
  print(e)

def eg_treewalk():
   sheet = SHEET(csv(the.file))
   ents(sheet)
   t = TREE(sheet)
   for a,b in t.nodes(t.tree()):
      if a.lefts and a.rights:
         print(b)
         for col0,col1,col2 in zip(a.cols.x, a.lefts.cols.x, a.rights.cols.x):
            mid1, mid2 = col1.mid(), col2.mid()
            if col1.diff(col2, mid1, mid2):
               print("\t",col0.at)

def ents(sheet):
  for col in sheet.cols.x:
     if isinstance(col,SYM):
       a = Counter()
       for row in sheet.rows:
         x = row.cells[col.at]
         if x != "?": a[x] += 1
       e = ent(a)
     else:
       a = []
       for row in sheet.rows:
         x = row.cells[col.at]
         if x != "?": a += [x]
       a.sort()
       t  = len(a)//10
       sd = 1/big+(a[int(t*.9)] - a[int(t)])/2.56
       print(sd)
       e =  .5*log(6.28*sd*sd, euler) +.5 
     print(col.at,e)

#---------------------------------------------------------------
the=settings(__doc__)
#---------------------------------------------------------------
if __name__ == "__main__":
   egs( cli(the), __doc__, locals())

"""
todo:
run over all nodes: for all with  kids depth
v(x) of all rows
delete rows subset from rowss
mode of each cluster
any difference
dead,alive
depth

goal = num,(0|1)
y = list[goal]
x = list[num|sym]
row = [xs,ys]
rows = [row]+

for c in  cols.c  E[c] = entropy(select column c from rows)

tree = recursive bi-culstering of rows on cols.c
tree has  node1,node2...
for  nodes node0 with kids node1,  node2




"""
