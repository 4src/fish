#!/usr/bin/env lua
-- <!--- vim : set et sts=2 sw=2 ts=2 : --->
local help = [[
tiny: multi-goal semi-supervised explanation
(c) 2023 Tim Menzies <timm@ieee.org> BSD-2
  
USAGE: ./tiny.lua [OPTIONS] [-g ACTIONS]
  
OPTIONS:
  -f  --file    data file                    = ../etc/data/auto93.csv
  -g  --go      start-up action              = nothing
  -h  --help    show help                    = false
  -s  --seed    random number seed           = 93716221
]]

local l=require"lib"
local the = l.settings(help)
local eg, o, obj, oo = l.eg, l.o, l.obj, l.oo
local SYM,NUM,COLS,DATA = obj"SYM", obj"NUM", obj"COLS", obj"DATA"
local COL
-------------------------------------------------------------------------------
-- ### COLS

-- `COL`umns can be `NUM`eric or `SYM`bolic. Upper case names denote `NUM`s.
-- All `COL`s know their name, their column loc`at`ion, their count `n` of items seen.
function COL(n,s) 
  return s:find"^[A-Z]" and NUM(n,s) or SYM(n,s) end
-------------------------------------------------------------------------------
-- ### SYM

-- `SYM`s uses `has` to count symbols seen so far (and the most common symbol is the `mode`).
function SYM.new(i,n,s) 
  return {name=s or "", at=n or 0, n=0, has={}, most=0, mode=nil}  end

-- Update a `SYM`bol.
function SYM.add(i,x)
  if x=="?" then return end
  i.n      = 1 + i.n
  i.has[x] = 1 + (i.has[x] or 0)
  if i.has[x] > i.most then i.most,i.mode = i.has[x],x end end

-- `mid,div` returns central tendency  and diversity.
function SYM.mid(i) return i.mode end
function SYM.div(i,     e) 
  e = 0
  for _,v in pairs(i.has) do e = e - v/i.n * math.log(v/i.n,2) end
  return e end
-------------------------------------------------------------------------------
-- ### NUM

-- `NUM`s tracks the smallest and biggest number seen to far (in `lo` and `hi`) 
-- as well as the the mean `mu` and second moment `m2` (used to find standard deviation).
-- Also, `pretty` controls how we report numbers (and this switches to "%g" 
-- if we ever see a float).  Any name ending with `-` is something we want to _minimize_ 
-- (so we give it a non-positive weight).
function NUM.new(i,n,s) 
  return {name=s or "",  at=n or 0,  n=0, 
          lo=l.big, hi= -l.big, mu=0,  m2=0, 
          pretty="%.0f", want=(s or ""):find"-$" and 0 or 1} end

-- Update a `NUM`ber.
function NUM.add(i,n,    d)
  if n=="?" then return end
  i.n  = 1 + i.n
  i.lo = math.min(n, i.lo)
  i.hi = math.max(n, i.hi)
  d    = n - i.mu
  i.mu = i.mu + d/i.n
  i.m2 = i.m2 + d*(n - i.mu)
  if math.type(n) == "float" then i.pretty = "%g" end end

-- `mid,div` returns central tendency  and diversity.
function NUM.mid(i,  nPlaces) return i.mu end
function NUM.div(i) return (i.m2/(i.n - 1))^.5 end

-- XXX need to handle rounding
--
-- Return `n` mapped 0..1, min..max.
function NUM.norm(i,n)
  return n=="?" and x or (n - i.lo)/(i.hi - i.lo + 1/l.big) end

local function cross(mu1,mu2,std1,std2)
  local std1,std2,a,b,c,x1,x2
  if mu2 < mu1 then return cross(mu2,mu1,std2,std1) end
  if std1==0 or std2==0 or std1==std2 then return (mu1+mu2)/2 end
  a  = 1/(2*std1^2) - 1/(2*std2^2)
  b  = mu2/(std2^2) - mu1/(std1^2)
  c  = mu1^2 /(2*std1^2) - mu2^2 / (2*std2^2) - math.log(std2/std1)
  x1 = (-b + (b^2 - 4*a*c)^.5)/(2*a)
  x2 = (-b - (b^2 - 4*a*c)^.5)/(2*a)
  return mu1 <= x1 <= mu2 and x1 or x2 end



-------------------------------------------------------------------------------
-- ### COLS

-- `COLS` convert  list of column names (as strings) into `SYM`s or `NUM`s. 
-- Column names ending in a goal symbol (`+-!`) are dependent `y` features 
-- (and the others are independent `x` features). 
function COLS.new(i,ss) 
  i.x, i.y, i.all, i.names = {},{},{},ss
  for n,s in pairs(ss) do
    local col = l.push(i.all, COL(n,s))
    if not s:find"X$" then 
      l.push(s:find"[!+-]$" and i.y or i.x, col)
      if s:find"!$" then i.klass=col end  end end  end

-- Update a `COL` with info from `t`.
function COLS.add(i,t)
  for _,cols in pairs{i.x, i.y} do
    for _,col in pairs(cols) do 
      col:add(t[col.at]) end end 
  return t end

-------------------------------------------------------------------------------
-- ### DATA
function DATA.new(i,rows)
  i.rows,i.cols = {},nil
  for _,row in pairs(rows or {}) do i:add(row) end

function DATA.add(i,t)
  if i.cols then push(i.rows, i.cols:add(t)) else i.cols = COLS(t) end end

function DATA.clone(i,rows,     j)
  j = DATA()
  j:add{i.cols.names}
  for _,row in pairs(rows or {}) do j:add(row) end
  return j end

function DATA.d2h(i,t,    d)
  d = 0
  for _,col in pairs(i.cols.y) do d = d + (col.want - col:norm(t[col.at]))^2 end
  return d^.5 end

function DATA.ordered(i)
  return sort(i.rows, function(t,u) return i:d2h(t) < i:d2h(u) end) end

function DATA.stats(i,fun,cols)
  tmp=map(cols or i.cols.y, function(col) 
 
function DATA:stats(i,  what,cols,nPlaces,     fun,tmp)
  fun=function(k,col) return rnd(getmetatable(col)[what or "mid"](col),nPlaces),col.txt end
  tmp=kap(cols or self.cols.all, fun)
  tmp["N"]=#self.rows
  return tmp end

-------------------------------------------------------------------------------
-- ## Demos
eg("the",  function() oo(the) end)
eg("rnd",  function() return 3.14 == l.rnd(math.pi) end)
eg("rand", function(     num,d) 
  num = NUM()
  for _ = 1,1000 do num:add(l.rand()^2) end
  d = num:div()
  return .3 < d and d < .31  end)

eg("ent", function(     sym,e) 
  sym = SYM()
  for _,x in pairs{"a","a","a","a","b","b","c"} do sym:add(x) end
  e = sym:div()
  return 1.37 < e and e < 1.38 end)

eg("cross", function()
  print(cross(2.5,5,1,1)) end)

eg("cols", function()
  l.map(COLS({"Name", "Age", "Mpg-", "room"}).all, print) end)

-------------------------------------------------------------------------------
-- ## Start-up
if   not pcall(debug.getlocal,4,1) 
then the = l.cli(the, help)
     l.run(the) 
else return {NUM=NUM,SYM=SYM} end
