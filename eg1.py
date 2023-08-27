#!/usr/bin/env python3 -B
#vim: set et sts=2 sw=2 ts=2 : 
"""
<img src="https://online.stat.psu.edu/stat555/sites/onlinecourses.science.psu.edu.stat555/files/classification/recursive_part_process/index.png" align=right width=500>

# Recrusive Bi-Clustering (why,how)
Humans have difficulty accurately assessing complex models. This can
lead to unreliable and sometimes dangerous results (e.g.  
Green[^Green22] warns that incomplete review can mean "the legitimizing of faulty and
controversial (models) without addressing their fundamental issues”.

To reduce the cognitive load of those who review models, they need to look
at less material (measured in terms of number of attributes we explore,
or number of examples reviewed).  Specifically, given  rows of the form

       <x1,x2,x3,x4,x5.....y1,y2...>

(where `x,y` are the independent and dependent variables) often it is
it is cheaper and faster to  find  `x` values than `y` values. For
example, at any car lot, in a few seconds we can glance across 100s of
cars of many different colors, makes and models. But to assess miles
per gallon, we have to spend days driving each car around a large
number Hence to reason about these cars, we need to find a small
number of most representative examples, then explore their most
important attributes.

To that end, this code applies some instance and feature selection
methods, combined with a recursive bi-clustering procedure.  At each
level of the recursion, we map all points to the dimension of greatest
variance2 then divides the data at the median value. The generation of
contrast rules can then be used to report the minimal set differences
that most distinguish desired and current leaf clusters3. Pruning
heuristics, such as a greedy or non-greedy approach4 can be used to
only report the essential differences in the data. I recommend this
approach for model review since it can explore a large multi-objective
space using just a few questions (e.g., for 𝑁 = 10, 000 examples, ask
only 2 log2 (𝑁 ) < 30 questions)

the size of the model should be reduced.  The goal of a PROMISE 2.0
paper would be ``less is more''; that is, achieve faster, simpler,
better results using some simplification of existing technique.

To reduce the cognitive load on humans, large models must be
simplified and summarized into smaller ones.  Data mining has proven
to be an effective tool for finding useful, concise models. Therefore,
the PROMISE community has the necessary skills and experience to
redefine and simplify and improve the relationship between humans and
AI.

### Preliminaries 
To begin, we need some set up (load some libraries, improve printing
of instances, simplify dictionary access."""

from math import log,inf,sqrt 
import fileinput,random,time,ast,re

def pretty(x, dec=2): 
  "pretty print functions, floats and other things"
  return x.__name__+'()' if callable(x) else (round(x,dec) if dec and isinstance(x,float) else x)

def prettyd(d, pre="", dec=2): 
  "pretty print dict values, skipping private slots (those marked with '_')"
  return pre+'('+' '.join([f":{k} {pretty(d[k],dec)}" for k in d if k[0]=="_"])+')'

class obj(object): 
  "improve Python's presentation of instances"
  def __repr__(i): return prettyd(i.__dict__, i.__class__.__name__)

class box(dict):
  "simplify dictionary access, improve dictionary printing"
  def __repr__(i): return printd(i)
  __setattr__ = dict.__setitem__ # instead of d["slot"]=1, allow d.slot=1
  __getattr__ = dict.get         # instead of d["slot"],   allow d.slot  

"""Now we can define some constants, to be used later."""

the = box(p     =  2,  # coeffecient on distance calculation 
          cohen = .35) # "difference" means more than .35*std 

"""When we read data, we have to turn csv file cells to 
some Python things."""

def csv(file="-", filter=lambda a:ROW(a)):
  with fileinput.FileInput(file) as src:
    for line in src:
      line = re.sub(r'([\t\r"\' ]|#.*)', '', line) # delete spaces and comments
      if line: yield filter([str2thing(x) for x in line.split(",")])

def str2thing(x):
  try : return ast.literal_eval(x)
  except Exception: return x.strip()

"""So now we can read csv files into Python lists, e.g

        ["Clndrs","Volume","HpX","Lbs-","Acc+","Model","origin","Mpg+"]
        [ 8,       304.0,   193,  4732   18.5,  70,     1,       10]
        [ 8,       360,     215,  4615   14,    70,     1,       10]
        [ 8,       307,     200,  4376   15,    70,     1,       10]
        [ 8,       318,     210,  4382   13.5,  70,     1,       10]
        ...

"""

class ROW(obj):
  def __init__(i,a,base): 
      i.raw         = a    # raw values
      i.discretized = a[:] # discretized values, to be found late
      i.base        = base # source table
      i.alive       = True

def isNums(x)   : return isinstance(x,list)
def isNum(s)    : return s[0].isupper()
def isGoal(s)   : return s[-1] in "+-"
def isIgnored(s): return s[-1] == "X"

def mid(a): 
  return per(a,.5) if isNums(a) else max(a,key=a.get)

def div(a): 
  return ent(a) if isNums(a) else (per(a.9) - per(a,.1))/2.56

def ent(a):
  n = sum(a.values())
  return - sum(v/n*log(v/n,2) for v in a.values() if v > 0)

class COLS(a):
  def __init__(i,a):
    i.names,i.x,i.y,i.all = a,{},{},{}
    for n,s in enumerate(a):
      col = i.all[n] = [] if isNum(s) else {}
      if isIgnored(s): continue
      (i.y if isGoal(s) else i.x)[n] = x

  def add(i,a):
    def inc(col,x):
      if x!="?":
        if isNums(col): col += [x]
        else: col[x] = 1 + col.get(x,0)
    [inc(col, a[n]) for n,col in i.all.items()]
    return row

  def ready(i):
    [col.sort() for _,col in i.cols.all if isNums(col)]


class DATA(ob):
  def __init__(i,src=[]): 
    i.rows, i.cols = [],None
    [i.add(row) for row in src]
    i.cols.ready()
    
  def add(i,row):
    if    i.cols: i.cols.add(row.cells); i.rows += [row]
    else: i.cols = COLS(row.cells)

def per(a, p=.5) return a[int(p*len(a))]

"""ROWs know how their distances to other rows. 


[^Green22]: Ben Green. 2022. The flaws of policies requiring
human oversight of government algorithms. Computer Law &
Security Review 45 (2022), 10568 """  
