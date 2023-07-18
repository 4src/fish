import random
class SYM:
  def __init__(i,s,syms): i.name=s; i.syms=syms
  def one(i) : return random.choice(i.syms)
  def dist(i, a, b):
    return 0 if a==b else 1

class NUM:
  def __init__(i,s,lo,hi): i.name=s; i.lo=lo;i.hi=hi
  def one(i): return random.randrange(i.lo,i.hi)
  def norm(i,x):
    return x if x=="?" else (x - i.lo)/(i.hi - i.lo)

  def dist(i,a,b):
    a,b = i.norm(a), i.norm(b)
    a = a if a != "?" else (1 if b < .5 else 0)
    b = b if b != "?" else (1 if a < .5 else 0)
    return abs(a-b)

def dist(row1,row2,cols):
    def _dist(col):
      a,b= row1[col.at], row2[col.at]
      if a=="?" and b=="?": return 1
      return (NUM.dist if cols[col.at].name[0].isupper() else SYM.dist)(col,a,b)
    return sum((_dist(col)**2 for col in cols))**1/2 /  len(cols)**1/2

class DATA:
  def __init__(i):
    random.seed(1)
    i.cols = [SYM("age","fish"),NUM("Aarm",1,10),NUM("Leg",4,100), NUM("Nome",1,2),NUM("Toe",4,5)]
    for n,col in enumerate(i.cols): col.at = n
    i.rows = [[col.one() for col in i.cols] for _ in range(1000)]
    for  j,row in enumerate(i.rows):
        for k in  range(j+1, len(i.rows)):
           dist(row,i.rows[k],i.cols)

print(DATA())
