import traceback,random,sys,re
#--------------------------------------------------------------------------------------------------
def cli(dict):
  """Update dict slot xxx from the -x or  --xxx flag on the command line. 
  Bools get flipped, others get read after flag."""
  for k, v in dict.items():
    s = str(v)
    for j, x in enumerate(sys.argv):
      if x == ("-"+k[0]) or x == ("--"+k):
        dict[k] = coerce("True"  if s=="False" else (
                         "False" if s=="True"  else sys.argv[j+1]))
  return dict

def showHelp(funs):
  "pretty print help and the actions"
  print(re.sub("(\n[A-Z][A-Z]+:)", r"\033[93m\1\033[00m", # yellow for headings
          re.sub("(-[-]?[\S]+)",   r"\033[96m\1\033[00m", # show dashed in cyan (light blue)
            eg.__doc__+"\nACTIONS:")))
  [print(f"  {k:8}  {v.__doc__}") for k,v in funs.items()]

def run(name,the,todo,fun):
  "reset seed beforehand, reset settings afterwards"
  saved = {k:v for k,v in the.items()}
  random.seed(the.seed)
  try: 
    out = fun(the,todo)
  except Exception as e : 
    out = False
    print(traceback.format_exc())
  if out==False: print("❌ FAIL", name)
  for k,v in saved.items(): the[k]=v
  return out
#--------------------------------------------------------------------------------------------------
def test_all(the,todo): 
  "run all actions"
  def one(s): print(f"▶️  {s}-ing..."); return run(s,the,todo,todo[s])
  n = sum(one(s)==False for s in todo if s!="all")
  print(f"📌  {n} failure(s) of {len(todo)}")
  sys.exit(n - 2) # cause i have two deliberate errors in tests
  
