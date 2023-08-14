R=random.random
class SOME(obj):
   def __init__(i): i.n, i.ok, i._all = 0, True, []
   def add(i,x):
      i.n += 1
      s, a = len(i._all), i._all
      if   s < the.some      : i.ok=False; a += [x]
      elif R() < the.some/i.n: i.ok=False; a[int(R()*s)] = x
   @property
   def all(i):
      if not i.ok: i._all.sort()
      i.ok = True
      return i._all


