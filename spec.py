# vim : ts=2 sw=2 et :
from __future__ import annotations
from collections import Counter
from copy import deepcopy

class Spec(object):
  def __init__(i,k=None): 
    i.__dict__.update({k:deepcopy(v) for k,v in i.__class__._spec.items()})
  def __repr__(i): 
    return i.__class__.__name__+"{"+(' '.join([f":{k} {v}" for k,v in i.__dict__.items()]))+"}"
  @classmethod
  def __init_subclass__(cls): 
    cls._spec = {k:v for c in reversed(cls.__mro__) for k,v in c.__dict__.items() if k[0] != "_"}

def posint20(x=None): within(x,lo=0,hi=20)

def within(x=None, lo=0, hi=1000):
  if x==None: return random.choce(lo,hi)
  assert lo <= x <= hi,"out of range"
  return x

class Col(Spec): at:posint20=0; name:str=" "; n:int=0
class Num(Col) : mu:float=0; mu2:float=0; heaven:int=0
class Sym(Col) : has=Counter()

class Row(Spec):
  use = True
  x:[float | int | str | bool | "?"]=[]
  y:[float | int]=[]

class Cols(Spec): x:[Col]=[]; y:[Col]=[]

class Node(Spec):
  depth=0 # for root of tree
  use=True  # if false, then ignore
  rows:  [Row] = []
  left:   Row  = None
  right:  Row  = None
  lefts:  Node  = None
  rights: Node = None

print(Row())
r1=Row()
r2=Row()
r1.x += [1]
print(r1,r2)
print(Num())
# -------------------------------------------------------
#col = Cols() # define a palce to store our columns
#descretize all x columns (equal frequency, bins=5)

def loop(nodes,rows, stop):
    E={}
    rows1 = [row for row in rows in row.use]
    if len(rows1) < stop: return rows1
    for col in cols.x: E[col.at] = ent() #being the entropy of each column x in rows1

    def score(parent):
       mid1, mid2 = mid(parent.lefts), mid(parent.rights); # andre uses ant
       diffs = [col for col in cols.x if mid1.cell[col.at] != mid2.cell[col.at]]
       return sum((E[col.at]/(1+parent.depth) for col in diffs)) / len(diffs)
 
    def isCandidate(node):
       return node.use and node.lefts and node.lefts.use \
                         and i.rights   and i.rights.use 
 
    def dont_use(node):
       if node:
         node.use=False
         for row in node.rows: row.use= False
         dont_use(node.lefts)
         dont_use(node.rigthts)
 
    if candidates := [node for node in nodes if isCandidate(node)]:
        most = max(candidates, key=score)
        dont_use(most.rights) if better(most.left, most.right) else dont_use(most.lefts)
