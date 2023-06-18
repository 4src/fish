#!/usr/bin/env python3 -B
#vim: set et sts=2 sw=2 ts=2 : 
"""
  -h  --help    show help             = False  
less: look around just a little, guess where to search.  
(c) 2023 Tim Menzies <timm@ieee.org>, BSD-2  

USAGE: 
  ./fish.py -f csvfile [OPTIONS]   
  cat csvfile | ./fish.py [OPTIONS]

OPTIONS:  
  -b  --bins    max number of bins    = 16  
  -c  --cohen   size significant separation = .35  
  -f  --file    data csv file         = "../data/auto93.csv"  
  -g  --go      start-up action       = "nothing"
  -h  --help    show help             = False  
  -l  --lazy    lazy mode             = False  
  -m  --min     min size              = .5  
  -p  --p       distance coeffecient  = 2    
  -r  --rest    ratio best:rest       = 4  
  -s  --seed    random number seed    = 1234567891  
  -t  --top     explore top  ranges   = 8  
  -w  --want    goal                  = "mitigate"  
"""
from fileinput import FileInput as file_or_stdin
import traceback,random,math,sys,re
from termcolor import colored
from functools import cmp_to_key
from ast import literal_eval
#---------------------------------------------
class pretty(object):
  "Objects support pretty print, hiding privates slots (those starting with `_`)"
  def __repr__(i):
    return i.__class__.__name__+str({k:v for k,v in i.__dict__.items() if k[0] != "_"})
#---------------------------------------------
class ROW(pretty):
  "Place to store cells and meta-knowledge about those cells."
  def __init__(i, cells=[]): i.cells,i.klass = cells,None
  def at(i,col): return i.cells[col.at]
#---------------------------------------------
class COL(pretty):
  "COLumns know the name, position and the count of rows seen."
  def __init__(i, txt="",at=0): i.n,i.at,i.txt = 0,at,txt
  def add(i,x):
    "Ignoring empty cells, increment `n` then do the adding."
    if x != "?":
      i.n += 1
      i.add1(x)
    return x
#---------------------------------------------
class NUM(COL):
  "Summarize stream of numbers. Knows the mean and standard deviation."
  def __init__(i, txt="",at=0):
    COL.__init__(i,txt=txt,at=at)
    i.w = -1 if len(i.txt) > 0 and i.txt[-1] == "-" else 1
    i.mu = i.m2 = 0
    i.lo, i.hi = big, -big 
  def add1(i,x):
    "Update `lo,hi` and the variables needed to calculate stdev."
    i.lo = min(x, i.lo)
    i.hi = max(x, i.hi)
    delta = x - i.mu
    i.mu += delta/i.n
    i.m2 += delta*(x - i.mu)
  def div(i, decimals=None):
    "Return diversity around the central tendency."
    return rnd((i.m2/(i.n - 1))**.5 if i.m2>0 and i.n > 1 else 0, decimals)
  def mid(i, decimals=None):
    "Return central tendency."
    return rnd(i.mu, decimals)
  def norm(i,x):
    "May `x` to 0..1 for `lo` to `hi`."
    return x if x=="?" else  (x-i.lo)/(i.hi - i.lo + 1/big)
#---------------------------------------------
class SYM(COL):
  "Summary a stream of symbols. Knows mode and entropy."
  def __init__(i,txt="",at=0):
    COL.__init__(i,txt=txt,at=at)
    i.counts,i.mode, i.most = {},None,0
  def add1(i,x):
    "Increment counts and mode."
    now = i.counts[x] = 1 + i.counts.get(x,0)
    if now > i.most: i.most, i.mode = now, x
  def div(i, decimals=None):
    "Return diversity around the central tendency."
    a = i.counts
    return rnd( - sum(a[k]/i.n * math.log(a[k]/i.n,2) for k in a if a[k] > 0), decimals)
  def mid(i,decimals=None):
    "Return central tendency."
    return i.mode
  def sub(i,x):
    "Decrements counts."
    i.n -= 1
    i.counts[x] -= 1
    assert 0 <= i.counts[x]
    return x
#---------------------------------------------
class COLS(pretty):
  "Convert a list of names into NUMs and SYMs (kept different binds of cols in different lists)."
  def __init__(i,names):
    i.x, i.y, i.names = [],[],names
    i.all = [(NUM if s[0].isupper() else SYM)(at=n,txt=s) for n,s in enumerate(names)]
    for col in i.all:
      z = col.txt[-1]
      if z != "X":
        if z=="!": i.klass= col
        (i.y if z in "-+!" else i.x).append(col)
  def add(i,row):
    "Add a row's data to all the non-skipped columns."
    for cols in [i.x, i.y]:
      for col in cols: col.add(row.at(col))
    return row
#---------------------------------------------
class DATA(pretty):
  "Keep `rows` of data, summarized into col`umns."
  def __init__(i,src=[]):
    i.cols, i.rows = None,[]
    [i.add(row) for row in src]
  def add(i,row):
    "For first row, build the `cols`. Otherwise, update summaries and the rows."
    if i.cols: i.rows += [i.cols.add(row)]
    else:      i.cols = COLS(row.cells)
  def clone(i,rows=[]):
    "Replicate structure of self."
    return DATA([ROW(i.cols.names)] + rows)
  def sort2(i,row1,row2):
    "Return True if `row1` better than `row2`."
    s1, s2, n = 0, 0, len(i.cols.y)
    for col in i.cols.y:
      a, b = col.norm(row1.at(col)), col.norm(row2.at(col))
      s1  -= math.exp(col.w * (a - b) / n)
      s2  -= math.exp(col.w * (b - a) / n)
    return s1 / n < s2 / n
  def sorted(i,rows=[]):
    "Sort all `rows`."
    return sorted(rows or i.rows, key=cmp_to_key(lambda a,b: i.sort2(a,b)))
  def stats(i,cols=None, fun="mid", decimals=2):
    "Report statistics on a set of `col`umns (defaults to `i.cols.y`."
    cols = cols or i.cols.y
    def what(col): return col.mid(decimals) if fun=="mid" else col.div(decimals)
    return dict(mid=BAG(N=cols[1].n, **{col.txt:what(col) for col in cols}))
#---------------------------------------------
# operators, used in trees
ops = {">"  : lambda x,y: x=="?" and y=="?" or x>y,
       "<=" : lambda x,y: x=="?" and y=="?" or x<=y,
       "==" : lambda x,y: x=="?" and y=="?" or x==y,
       "!=" : lambda x,y: x=="?" and y=="?" or x!=y}
"""Operators used in decision tree."""

negate = { ">"  :  "<=",
           "<=" :  ">",
           "==" :  "!=",
           "!=" :  "==" }
"""Negation of operators."""
#---------------------------------------------
# tree generation
class TREE(object):
  "Recursively split on the cut (that most distinguishes different klasses)."
  def __init__(i,data):
    lst   = data.sorted()
    n     = int(len(lst)**the.min)
    bests = lst[-n:]
    rests = lst[:n*the.rest]
    for row in bests: row.klass = True
    for row in rests: row.klass = False
    i.data = data
    i.root =  i.grow(bests + rests, 2*(n**the.min), BAG(here=data, at=None))

  def grow(i,rows, stop, t):
    t.left,t.right = None,None
    if len(rows) >= stop:
      _,at,op,cut,s = i.cut(i.data, i.data.cols.x, rows)
      if cut:
        left,right = [],[]
        print(BAG(at=at,op=op,cut=cut,s=s))
        [(left if ops[op](row.cells[at], cut) else right).append(row) for row in rows]
        if len(left) != len(rows) and len(right) != len(rows):
          t.left = i.grow(left, stop, BAG(here=i.data.clone(left),  at=at,cut=cut,txt=s,op=op))
          t.right= i.grow(right,stop, BAG(here=i.data.clone(right), at=at,cut=cut,txt=s,op=negate[op]))
    return t

  def cut(i,data,cols,rows):
    "Return best `div,at,op,cut,txt` that most divides the klasses in `rows`."
    def sym(col):
      "For syms, just return the one with least diversity of klasses."
      d = {}
      for row in rows:
        x = row.at(col)
        if x !=  "?":
          d[x] = d.get(x, None) or SYM()
          d[x].cut = x
          d[x].add(row.klass)
      best = sorted(d.values(), key=lambda s:s.div())[0]
      return best.div(), col.at,"==",best.cut,col.txt
    #-----------
    def num(col):
      "For nums, just return the cut that most reduces expected diversity."
      X     = lambda row: row.at(col)
      eps   = col.div()*the.cohen
      small = len(rows)**the.min
      all   = sorted([row for row in rows if X(row) != "?"], key=X)
      d1,d2,a,z = SYM(), SYM(), X(all[0]), X(all[-1])
      [d2.add(row.klass) for row in all]
      cut,n2,lo = None,len(all),col.div()
      if lo > 0 :
        for n1,row in enumerate(all):
          n2, x, y = n2-1, X(row), row.klass
          d2.sub( d1.add(y) )
          if n1 > small and n2 > small and x != X(all[n1+1]) and x-a > eps and z-x > eps:
            xpect = (d1.div()*n1 + d2.div()*n2)/(n1+n2)
            if xpect < lo:
              cut,lo = x,xpect
      return lo,col.at,"<=",cut,col.txt
    #------------------------------------
    return sorted([(num(col) if isa(col,NUM) else sym(col)) for col in cols])[0]

  def showTree(i,t, lvl="",above=None):
    if t:
      meta = "" if t.at==None else t.here.stats()
      ie print(lvl + b4,str(len(t.here.rows)))
      pre= f"if {t.txt} {t.op.__doc__} {t.val}" if t.left or t.right else ""
      showTree(t.left,  lvl+"|.. ", pre)
      showTree(t.right, lvl+"|.. ", "else")
#---------------------------------------------
R   = random.random      # short cut to random number generator
isa = isinstance         # short cut for checking types

big = 1E30
"""large numbers"""

class BAG(dict):
  "Dictionaries that can be accessed via `x[\"slot\"]` or `x.slot`."
  __getattr__ = dict.get

class SETTINGS(BAG):
  "Parse settings from string."
  def __init__(i,s):
    for m in re.finditer(r"\n\s*-\w+\s*--(\w+)[^=]*=\s*(\S+)",s): i[m[1]] = coerce(m[2])
  def cli(i):
    """For k,v in i, update `v` if there is a command-line flag `-k[0]` or `--k`. Note
    that bookean values need no argument (since we will just negate `v`)."""
    for k,v in i.items():
      v = str(v)
      for j,x in enumerate(sys.argv):
        if ("-"+k[0]) == x or ("--"+k) == x:
          v = "True" if v=="False" else ("False" if v=="True" else sys.argv[j+1])
      i[k] = coerce(v)

def coerce(x):
  try: return literal_eval(x)
  except: return x

def csv(file, filter=lambda x:x):
  "Returns an iterator that returns lists from standard input (-) or a file."
  if file=="-": file=None
  with file_or_stdin(file) as src:
    for line in src:
      line = re.sub(r'([\n\t\r"\' ]|#.*)', '', line)
      if line:
        yield filter([coerce(s.strip()) for s in line.split(",")])

def rnd(x,decimals=2):
  return x if x==None else round(x,decimals)

def rows(file):
  "Returns an iterator that returns ROWS"
  return csv(file, ROW)

def yell(s,c):
  "Print string `s`, colored by `c`."
  print(colored(s,"light_"+c,attrs=["bold"]),end="")
#----------------------------------------------------
class Egs:
  "Place to store the examples."
  all = locals()

  def ok():
    "Run everything (except ok,h). Return how often something fails."
    fails, saved = 0, {k:v for k,v in the.items()}
    for what,fun in Egs.all.items():
      if what[0].isupper():
        yell(what + " ","yellow")
        fail = Egs.failure(saved,fun)
        yell(" FAIL\n","red") if fail else yell(" PASS\n","green")
        fails += fail
    yell(f"TOTAL FAILURE(s) = {fails}\n", "red" if fails > 0 else "cyan")
    sys.exit(fails)

  def failure(saved,fun):
    """Called by `Egs.ok`. `Fun` fails if it returns `False` or if it crashes.
    If it crashes, print the stack dump but then continue on
    Before running it, reset the system to  initial conditions."""
    for k,v in saved.items(): the[k] = v
    random.seed(the.seed)
    fail = True
    try:    fail = fun() != False  # here, fail might be reset to True
    except: traceback.print_exc()
    return fail

  def The():
    "print the settings"
    print(the)

  def Rnd():
    "rnd to 2 decimals"
    return 3.14 == rnd(math.pi,2)

  def Num(txt=""):
    "test NUMs"
    n = NUM(txt)
    for x in range(10**4):  n.add(R()**.5)
    return .66 < n.mid() < .67 and .23 <  n.div() < .24 and n

  def Sym(txt=""):
    "test SYMs"
    s=SYM(txt)
    [s.add(x) for x in "aaaabbc"]
    return "a"==s.mid() and 1.37 <= s.div() < 1.38 and s

  def Rows():
    "Check we can load rows from file."
    print(the.file)
    for row in list(rows(the.file))[:5]: print(row) #[:5]: print(row)

  def Col():
    "Check we can convert names to NUMs and SYMs."
    [print(x) for x in COLS(["name","Age","Weight-"]).all]

  def Data():
    "Can we load data and get its stats?"
    DATA(rows(the.file)).stats()

  def Clone():
    "Can we replicate a DATA's structure?"
    d1 = DATA(rows(the.file))
    d2= d1.clone(d1.rows)
    print(d1.cols.y[1])
    print(d2.cols.y[1])

  def Sorts():
    "Can we sort rows into `best` and `rest`?"
    d = DATA(rows(the.file))
    lst = d.sorted()
    m   = int(len(lst)**.5)
    best= d.clone(lst[-m:]);         print("all ",d.stats())
    best= d.clone(lst[-m:]);         print("best",best.stats())
    rest= d.clone(lst[:m*the.rest]); print("rest",rest.stats())

  def Tree():
    d=DATA(rows(the.file))
    TREE(d)
    print(d.cols.names)
#---------------------------------------------


the = SETTINGS(__doc__)
"""Config options, parsed from `__doc__`"""
random.seed(the.seed)    # set random number seed

if __name__ == "__main__":
  the.cli()
  if the.help: print(__doc__)
  elif the.go in Egs.all: Egs.all[the.go]()
