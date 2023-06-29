#!/usr/bin/env lua
-- <!--- vim : set et sts=2 sw=2 ts=2 : --->
local l=require"lib"
local eg, o, obj, oo = l.eg, l.o, l.obj, l.oo
local the,help = l.settings[[
  
tiny: multi-goal semi-supervised explanation
(c) 2023 Tim Menzies <timm@ieee.org> BSD-2
  
USAGE: ./tiny.lua [OPTIONS] [-g ACTIONS]
  
OPTIONS:
  -f  --file    data file                    = ../etc/data/auto93.csv
  -g  --go      start-up action              = nothing
  -h  --help    show help                    = false
  -s  --seed    random number seed           = 93716221
]]

-- `COL`umns can be `NUM`eric or `SYM`bolic. Upper case names denote `NUM`s.
-- All `COL`s know their name, their column loc`at`ion, their count `n` of items seen.
local SYM, NUM, COLS = obj"SYM", obj"NUM", obj"COLS"
local COL
function COL(n,s) 
  return s:find"^[A-Z]" and NUM(n,s) or SYM(n,s) end

-- ### SYM

-- `SYM`s uses `has` to count symbols seen so far (and the most common symbol is the `mode`).
function SYM.new(i,n,s) 
  return {name=s or "", at=n or 0, n=0, has={}, most=0, mode=nil}  end

-- Update a `SYM`bol.
function SYM.add(i,x)
  if x=="?" then return end
  i.n += 1
  i.has[x] = 1 + (i.has.get[x] or 0)
  if i.has[x] > i.most then i.mode=i.has[x],x end end

-- `mid,div` returns central tendency  and diversity.
function SYM.mid(i) return i.mode end
function SYM.div(i,     e) 
  e = 0
  for _,v in pairs(i.has) do e = e - v/i.n * math.log(v/i.n,2) end
  return e end

-- ### NUM

-- `NUM`s tracks the smallest and biggest number seen to far (in `lo` and `hi`) 
-- as well as the the mean `mu` and second moment `m2` (used to find standard deviation).
-- Also, `pretty` controls how we report numbers (and this switches to "%g" 
-- if we ever see a float).  Any name ending with `-` is something we want to _minimize_ 
-- (so we give it a negative weight).
function NUM.new(i,n,s) 
  return {name=s or "",  at=n or 0,  n=0, 
          lo=l.big, hi= -l.big, mu=0,  m2=0, 
          pretty="%.0f", w=(s or ""):find"-$" and -1 or 1} end

-- Update a `NUM`ber.
function NUM.add(i,n,    d)
  if m=="?" then return end
  i.n  = 1
  i.lo = math.min(n, i.lo)
  i.hi = math.max(n, i.hi)
  d    = n - i.mu
  i.mu = i.mu + d/i.n
  i.m2 = i.m2 + d*(n - i.mu)
  if math.type(n) == "float" then i.pretty = "%g" end end

-- `mid,div` returns central tendency  and diversity.
function NUM.mid(i) return i.mu end
function NUM.div(i) return (i.m2/(i.n - 1))^.5 end

-- Return `n` mapped 0..1, min..max.
function NUM.norm(i,n)
  return n=="?" and x or (n - i.lo)/(i.hi - i.lo + 1/l.big) end

-- ### COLS

-- `COLS` convert  list of column names (as strings) into `SYM`s or `NUM`s. 
-- Column names ending in a goal symbol (`+-!`) are dependent `y` features 
-- (and the others are independent `x` features). 
function COLS.new(i,ss) 
  i.x, i.y, i.all = {},{},{}
  for n,s in pairs(ss) do
    local col = l.push(i.all, COL(n,s))
    if not s:find"X$" then 
      l.push(s:find"[!+-]$" and i.y or i.x, col)
      if s:find"!$" then i.klass=col end  end end  end

-- Update a `COL` with info from `t`.
function COLS.add(i,t)
  for _,cols in pairs{i.x, i.y} do
    for _,col in pairs(cols) do 
      col:add(t[col.at]) end end end

-- ## Demos
eg("the",  function() oo(the) end)
eg("rnd",  function() return 3.14 == l.rnd(math.pi) end)
eg("rand", function(     num) 
   num=NUM()
   for _=1,1000 do l.push(t, l.rnd(l.rand(1,20))) end
   oo(l.sort(t)) end) 

-- ## Start-up
if   not pcall(debug.getlocal,4,1) 
then the = l.cli(the, help)
     l.run(the) 
else return {NUM=NUM,SYM=SYM} end
