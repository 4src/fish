t1 = [(6,5), (7,8), (7,0),(4,3)]

# cant assume lists
def combine(ranges):
  tmp={}
  for col,v in ranges:
    tmp[col] = tmp.get(col,[])
    tmp[col] += v if isinstance(v,list) else [v]
  return sorted([(k,tuple(sorted(v))) for k,v in tmp.items()]))

def select(data,ranges,row):
  def _ors(chops,vals):
    for val in vals:
      if  within(row.cooked[col],*chops[val]): return True
  for col,vals in ranges:
    if not _ors(data.cols.all[col].chops, vals): return False
  return True

def selects(data,ranges,rows):
  return [row for row in rows if select(data,ranges,row)]

def merger(data,bestRows,RestRows):
  def _fun(a,b):
    c= combine(a+b)
    b= selects(data,c,bestRows)
    r= selects(data,c,restRows)
    v= score(len(b),len(r),len(bestRows),len(restRows))
    return (v,c)
  return _fun

def grow(pairs,merge,peeks=32,top=5,beam=None):
  beam = beam or len(pairs)
  pairs = sorted(set(pairs),         # discard duplicates
                 key=lambda y: -y[0] # sort, descending, on first part of pair
                 )[:int(beam)]       # only use the top ones
  if len(pairs) <= top: return pairs
  total = sum((score  for (score,_) in pairs))
  new   = [merge(pick(pairs,total),pick(pairs,total))  _ in range(peeks)]
  return grow(pairs + new, combiner, peeks, top, beam/2)



