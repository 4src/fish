from collections import Counter

class obj(object):
   def __repr__(i):
      return i.__class__.__name__+"{"+' '.join([f":{k} {v}" for k,v in i.__dict__.items()])+"}"

class COL(obj):
    def __init__(i,at=0,name=""): i.name,i.at=name,at

class NUM(COL):
    def __init__(i,a=[],**d):
        super().__init__(**d);
        a=sorted(a)
        if a: i.lo,i.hi = a[0], a[-1]
class SYM(COL):
    def __init__(i,a,**d):
        super().__init__(**d);
        i.seen=Counter(a)
        print(i.seen)
        i.mode = max(i.seen, key=i.seen.get)

print(SYM("asdasdasddasads",name="fred",at=2))
