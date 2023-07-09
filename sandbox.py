t1 = [(6,5), (7,8), (7,0),(4,3)]

def combine(ranges):
  tmp={}
  for col,v in ranges:
    tmp[col] = tmp.get(col,[])
    tmp[col] += v if isinstance(v,list) else [v]
  return sorted([(k,sorted(v)) for k,v in tmp.items()])

def select(data,ranges,row):
  def _ors(chops,vals):
    for val in vals:
      if  within(row.cooked[col],*chops[val]): return True
  for col,vals in ranges:
    if not _ors(data.cols.all[col].chops, vals): return False
  return True

def selects(data,ranges,rows):
  return [row for row in rows if select(data,ranges,row)]

def grow(data,lst,bestRows,restRows,beam):
  def _uniques():
    i, out= 0,[]
    while i < len(lst):
      uniques += lst[i]
      i += 1
      while i<len(lst)  and lst[i]==lst[i-1]: i += 1
    return out
  def _combine2(a,b):
    c= combine(a+b)
    b= selects(data,c,bestRows)
    r= selects(data,c,restRows)
    v= score(len(b),len(r),len(bestRows),len(restRows))
    return (v,c)
  beam = beam or len(lst)
  if beam < 2 : return lst
  lst = _uniques(sorted([(n,x) for n,x in lst], key=lambda y: -y[0]))[:int(beam)]
  total = sum(( n1 for (n1,_) in lst ))
  return grow(lst + [ _combine(pick1(lst,total),pick1(lst,total))  _ in range(the.picks)],
              bestRows, restRows, beam/2)



