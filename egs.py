#!/usr/bin/env python3 -B
from eg import *
import traceback,sys,eg,re
#--------------------------------------------------------------------------------------------------
def cli(d):
  "Update a dictionary from command line. Bools get flipped, others get read after flag"
  for k, v in d.items():
    s = str(v)
    for j, x in enumerate(sys.argv):
      if x == ("-"+k[0]) or x == ("--"+k):
        d[k] = coerce("True" if s=="False" else ("False" if s=="True" else sys.argv[j+1]))
  return d

def showHelp(funs):
  "print help and the actions"
  print(re.sub("(\n[A-Z][A-Z]+:)", r"\033[93m\1\033[00m",
           re.sub("(-[-]?[\S]+)", r"\033[96m\1\033[00m",
              eg.__doc__+"\nACTIONS:")))
  [print(f"  {k:8}  {v.__doc__}") for k,v in funs.items()]

def run(name,fun):
  "reset seed beforehand, reset settings afterwards"
  saved = {k:v for k,v in the.items()}
  random.seed(the.seed)
  try                   : out = fun()
  except Exception as e : out = False; print(traceback.format_exc())
  if out==False: print("❌ FAIL", name)
  for k,v in saved.items(): the[k]=v
  return out
#--------------------------------------------------------------------------------------------------
def eg_all(): 
  "run all actions"
  sys.exit(sum(run(s,fun)==False for s,fun in todo.items() if s!="all"))

def eg_settings(): 
  "show settings"
  print(the)
  
def eg_crash(): 
  "can an action  crash and we keep going?"
  return a[1]
  
def eg_fail(): 
  "what happens when an action fails?"
  return 1 > 2

def eg_cols(): 
  "can I make and categorize cols?"
  c = COLS(["name", "Age", "Weight-"])
  c.y[2] += [100]
  print(box(x=c.x, y=c.y, all=c.all, names=c.names))
  return c.y[2] == c.all[2] 

def eg_sym():
  "can i find mode and entropy?"
  d = dict(a=1,c=2,d=4)
  return "d" == mid(d) and 1.3 < div(d) < 1.4

def eg_num():
  "can i find median and stdev?"
  a=[]
  for _ in range(1000): a += [random.gauss(10,2)]
  a=sorted(a)
  return 9.9 < mid(a) < 10.1 and 1.9 < div(a) < 2.1

the = cli(the)
todo = {k[3:]:fun for k,fun in locals().items() if k[:3]=="eg_"} 
if the.help: showHelp(todo)
else       : [run(x, todo[x]) for x in sys.argv if x in todo]
