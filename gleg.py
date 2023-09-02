#!/usr/bin/env python3 -B
from gl import *
from eg import *

def test_the(the,_): 
  "show settings"
  print(the)
  
def test_crash(*_): 
  "can an action  crash and we keep going?"
  return a[1]
  
def test_fail(*_):  
  "what happens when an action fails?"
  return 1 > 2

def test_cols(*_): 
  "can I make and categorize cols?"
  c = COLS(["name", "Age", "Weight-"])
  c.y[2] += [100]
  print(box(x=c.x, y=c.y, all=c.all, names=c.names))
  return c.y[2] == c.all[2] 

def test_sym(*_):
  "can i find mode and entropy?"
  d = dict(a=1,c=2,d=4)
  return "d" == mid(d) and 1.3 < div(d) < 1.4

def test_num(*_):
  "can i find median and stdev?"
  a=[]
  for _ in range(1000): a += [random.gauss(10,2)]
  a=sorted(a)
  return 9.9 < mid(a) < 10.1 and 1.9 < div(a) < 2.1

def test_csv(*_):
  "can i read a csv and coerce fields to right things?"
  n=0
  for a in csv(the.file): n += len(a)
  return n == 3192 and isinstance(a[0],int) 

def test_data(*_):
  "can i read a csv and coerce fields to right things?"
  printd(DATA(the.file).stats())

def test_bestRest(*_):
  "asd"
  d=DATA(the.file)
  rows=sorted(d.rows) 
  n = int(len(rows)**the.min)
  print("base", d.stats()  )
  print("best", d.clone(rows[:n]).stats()  )
  print("rest", d.clone(rows[-n:]).stats() )

def test_dist(*_):
  d=DATA(the.file)
  one=d.rows[0]
  for j,row in enumerate(d.rows):
    if not j%30:
      print(f"{row-one:<4.2}  : ", row.raw)

def test_tree(*_):
  d=DATA(the.file)
  showTree(tree(d.rows,True))

def test_unsuper(*_):
   print(cuts(0, dict(all=[[random.random()**2] for _ in range(100)])))
    
if __name__ == "__main__":
  the = cli(the)
  todo = {k[5:]:fun for k,fun in locals().items() if k[:5]=="test_"} 
  showHelp(todo) if the.help else [run(x, the, todo,todo[x]) for x in sys.argv if x in todo]
