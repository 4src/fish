#!/usr/bin/env python3 -B
#<!-- vim: set ts=2 sw=2 et: -->
from fish import __doc__ as help
from fish import *

def cli(d):
  for k,v in d.__dict__.items():
    v = str(v)
    for j,x in enumerate(sys.argv):
      if ("-"+k[0]) == x or ("--"+k) == x:
        v= "False" if v=="True" else ("True" if v=="False" else sys.argv[j+1])
        d.__dict__[k] = coerce(v)
  return d

def main(help,the,egs):
  if the.help: return yell("cyan",help.split("\nNOTES:")[0])
  return sum([eg(name,the,egs) for name in dir(egs)
             if name[0] !="_" and (the.go=="." or the.go==name)])

def eg(name, the,egs):
  b4 = {k:v for k,v in the.__dict__.items()}
  f  = getattr(egs,name," ")
  yell("yellow","# ",name," ")
  random.seed(the.seed)
  tmp = f()
  yell("red"," FAIL\n") if tmp==False else yell("green", " PASS\n")
  for k in b4: the.__dict__[k] = b4[k]
  return 1 if tmp==False else 0

def yell(c,*s): print(colored(''.join(s),"light_"+c,attrs=["bold"]),end="")
#-------------------------------------------------------------------------------
class Egs:
  def they(): print(str(the)[:30],"...",end=" ")

  def num():
    num = NUM().adds(random.random() for _ in range(10**3))
    print(num)
    return .28 < num.div() < .3 and .49 < num.mid() < .51

  def sym():
    sym = SYM().adds("aaaabbc")
    return 1.37 < sym.div() < 1.39 and sym.mid()=='a'

  def read():
    prin(DATA().read(the.file).stats())

  def betters():
    data = DATA().read(the.file)
    best,rest = data.betters()
    print(data.stats())
    print(best.stats())
    prin(rest.stats())

  def contrast():
    data = DATA().read(the.file)
    best,rest = data.betters()
    b4 = None
    for bin in contrasts(best,rest):
      if bin.at != b4:
        print("")
        print(bin.at, bin.txt)
      b4 = bin.at
      print("\t", bin.lo, bin.hi, showd(bin.ys), round(bin.score,3))

  def rules():
    data = DATA().read(the.file)
    best,rest = data.betters()
    bins = sorted((bin for bin in contrasts(best,rest)), key=lambda x:x.score)[-10:]
    print([bin.score for bin in bins])

if __name__ == "__main__": 
  sys.exit(
    main(help,cli(the),Egs))
