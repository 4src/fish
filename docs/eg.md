Humans have difficulty accurately assessing complex models. This can
lead to unreliable and sometimes dangerous results (e.g.  
Green[^Green22] warns that incomplete review can mean "the legitimizing of faulty and
controversial (models) without addressing their fundamental issues”.

To reduce the cognitive load of those who review models, they need to look
at less material (measured in terms of number of attributes we explore,
or number of examples reviewed).  Specifically, given  rows of the form

       <x1,x2,x3,x4,x5.....y1,y2...>

(where `x,y` are the independent and dependent variables) often it is
it is cheaper and faster to  find  `x` values than `y` values. For
example, at any car lot, in a few seconds we can glance across 100s of
cars of many different colors, makes and models. But to assess miles
per gallon, we have to spend days driving each car around a large
number Hence to reason about these cars, we need to find a small
number of most representative examples, then explore their most
important attributes.

To that end, this code applies some instance and feature selection
methods, combined with a recursive bi-clustering procedure.  At each
level of the recursion, we map all points to the dimension of greatest
variance2 then divides the data at the median value. The generation of
contrast rules can then be used to report the minimal set differences
that most distinguish desired and current leaf clusters3. Pruning
heuristics, such as a greedy or non-greedy approach4 can be used to
only report the essential differences in the data. I recommend this
approach for model review since it can explore a large multi-objective
space using just a few questions (e.g., for 𝑁 = 10, 000 examples, ask
only 2 log2 (𝑁 ) < 30 questions)

the size of the model should be reduced.  The goal of a PROMISE 2.0
paper would be ``less is more''; that is, achieve faster, simpler,
better results using some simplification of existing technique.

To reduce the cognitive load on humans, large models must be
simplified and summarized into smaller ones.  Data mining has proven
to be an effective tool for finding useful, concise models. Therefore,
the PROMISE community has the necessary skills and experience to
redefine and simplify and improve the relationship between humans and
AI.

### Preliminaries 
To begin, we need some set up (load some libraries, improve printing
of instances, simplify dictionary access.

```python
from math import log,inf,sqrt 
import fileinput,random,time,ast,re

def pretty(x, dec=2): 
  "pretty print functions, floats and other things"
  return x.__name__+'()' if callable(x) else (round(x,dec) if dec and isinstance(x,float) else x)

def prettyd(d, pre="", dec=2): 
  "pretty print dict values, ignore private slots (marked with '_')"
  return pre+'('+' '.join([f":{k} {pretty(d[k],dec)}" for k in d if k[0]=="_"])+')'

class obj(object): 
  "fix Python's weak presentation of instances"
  __repr__ = lambda i:prettyd(i.__dict__, i.__class__.__name__)

class box(dict):
  "simplify dictionary access, improve dictionary printing"
  __repr__    = lambda i:printd(i)
  __getattr__ = dict.get
  __setattr__ = dict.__setitem__
```

Now we can define some constants, to be used later.

```python
the = box(p=2)
```

When we read data, we have to turn csv file cells to 
some Python things.

```python
def line2things(file="-"):
  with fileinput.FileInput(file) as src:
    for line in src:
      line = re.sub(r'([\t\r"\' ]|#.*)', '', line) # delete spaces and comments
      if line: yield [str2thing(x) for x in line.split(",")]

def str2thing(x):
  try : return ast.literal_eval(x)
  except Exception: return x.strip()
```

So now we can read csv files into Python lists, e.g

        ["Clndrs","Volume","HpX","Lbs-","Acc+","Model","origin","Mpg+"]
        [ 8,       304.0,   193,  4732   18.5,  70,     1,       10]
        [ 8,       360,     215,  4615   14,    70,     1,       10]
        [ 8,       307,     200,  4376   15,    70,     1,       10]
        [ 8,       318,     210,  4382   13.5,  70,     1,       10]
        ...

Now we need some place to store a row. My ROWs keep the raw values, as well as their discretized
values.

```python
class ROW(obj):
  def __init__(i,a,base): i.raw,i.discretized,i.base,i.alive = a,a[:],base,True
```

ROWs know how their distances to other rows. 


[^Green22]: Ben Green. 2022. The flaws of policies requiring
human oversight of government algorithms. Computer Law &
Security Review 45 (2022), 10568 """  

