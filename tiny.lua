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
local eg, o, obj, oo, rnd = l.eg, l.o, l.obj, l.oo, l.rnd
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
function SYM:new(n,s) 
  return {name=s or "", at=n or 0, n=0, has={}, most=0, mode=nil}  end

-- Update a `SYM`bol.
function SYM:add(x)
  if x=="?" then return end
  self.n      = 1 + self.n
  self.has[x] = 1 + (self.has[x] or 0)
  if self.has[x] > self.most then self.most,self.mode = self.has[x],x end end

-- `mid,div` returns central tendency  and diversity.
function SYM:mid(_) return self.mode end
function SYM:div(  nPlaces,     e) 
  e = 0
  for _,v in pairs(self.has) do e = e - v/self.n * math.log(v/self.n,2) end
  return nPlaces and rnd(e,nPlaces) or e end
-------------------------------------------------------------------------------
-- ### NUM

-- `NUM`s tracks the smallest and biggest number seen to far (in `lo` and `hi`) 
-- as well as the the mean `mu` and second moment `m2` (used to find standard deviation).
-- Also, `pretty` controls how we report numbers (and this switches to "%g" 
-- if we ever see a float).  Any name ending with `-` is something we want to _minimize_ 
-- (so we give it a non-positive weight).
function NUM:new(n,s) 
  return {name=s or "",  at=n or 0,  n=0, 
          lo=l.big, hi= -l.big, mu=0,  m2=0, 
          pretty="%.0f", want=(s or ""):find"-$" and 0 or 1} end

-- Update a `NUM`ber.
function NUM:add(n,    d)
  if n=="?" then return end
  self.n  = 1 + self.n
  self.lo = math.min(n, self.lo)
  self.hi = math.max(n, self.hi)
  d    = n - self.mu
  self.mu = self.mu + d/self.n
  self.m2 = self.m2 + d*(n - self.mu)
  if math.type(n) == "float" then self.pretty = "%g" end end

-- `mid,div` returns central tendency  and diversity.
function NUM:mid(  nPlaces) 
  return nPlaces and rnd(self.mu,nPlaces) or self.mu end
function NUM:div(  nPlaces,      sd)
  sd = (self.m2/(self.n - 1))^.5; return nPlaces and rnd(sd,nPlaces) or sd end

-- Return `n` mapped 0..1, min..max.
function NUM:norm(n)
  return n=="?" and x or (n - self.lo)/(self.hi - self.lo + 1/l.big) end

local function cross(mu1,mu2,sd1,sd2)
  local sd1,sd2,a,b,c,x1,x2
  if mu2 < mu1 then return cross(mu2,mu1,sd2,sd1) end
  if sd1==0 or sd2==0 or sd1==sd2 then return (mu1+mu2)/2 end
  a  = 1/(2*sd1^2) - 1/(2*sd2^2)
  b  = mu2/(sd2^2) - mu1/(sd1^2)
  c  = mu1^2 /(2*sd1^2) - mu2^2 / (2*sd2^2) - math.log(sd2/sd1)
  x1 = (-b + (b^2 - 4*a*c)^.5)/(2*a)
  x2 = (-b - (b^2 - 4*a*c)^.5)/(2*a)
  return mu1 <= x1 <= mu2 and x1 or x2 end
-------------------------------------------------------------------------------
-- ### COLS

-- `COLS` convert  list of column names (as strings) into `SYM`s or `NUM`s. 
-- Column names ending in a goal symbol (`+-!`) are dependent `y` features 
-- (and the others are independent `x` features). 
function COLS:new(ss) 
  self.x, self.y, self.all, self.names = {},{},{},ss
  for n,s in pairs(ss) do
    local col = l.push(self.all, COL(n,s))
    if not s:find"X$" then 
      l.push(s:find"[!+-]$" and self.y or self.x, col)
      if s:find"!$" then self.klass=col end  end end  end

-- Update a `COL` with info from `t`.
function COLS:add(t)
  for _,cols in pairs{self.x, self.y} do
    for _,col in pairs(cols) do 
      col:add(t[col.at]) end end 
  return t end

-------------------------------------------------------------------------------
-- ### DATA
function DATA:new(  ts)
  self.rows,self.cols = {},nil
  for _,t in pairs(ts or {}) do self:add(t) end

function DATA:add(t)
  if self.cols then push(self.rows, self.cols:add(t)) else self.cols = COLS(t) end end

function DATA:clone(  ts,     j)
  data1 = DATA()
  data1:add{self.cols.names}
  for _,t in pairs(ts or {}) do data1:add(t) end
  return data1 end

function DATA:d2h(t,     d)
  d = 0
  for _,col in pairs(self.cols.y) do d = d + (col.want - col:norm(t[col.at]))^2 end
  return d^.5 end

function DATA:ordered()
  return sort(self.rows, function(t1,t2) return self:d2h(t1) < self:d2h(t2) end) end

function DATA:stats(fun,cols)
  tmp=map(cols or self.cols.y, function(col) 
 
function DATA:stats(  what,cols,nPlaces,     t)
  t = {N=#self.rows}
  for _,col in pairs(cols or self.cols.all) do
    t[col.txt] =rnd(getmetatable(col)[what or "mid"](col),nPlaces) end
  return t end

-------------------------------------------------------------------------------
-- ## Demos
eg("the",  function() oo(the) end)
eg("rnd",  function() return 3.14 == rnd(math.pi) end)
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
