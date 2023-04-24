# vim: set ts=2 sw=2 et:
from fishn import __doc__ as help
from fishn import *

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
  sys.exit(main(help,cli(the),Egs))
