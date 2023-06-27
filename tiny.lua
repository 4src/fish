local l
local the = {seed=1234567891, min= .5, rest=3, 
             beam=10, file="../data/auto93.csv"}

-- Create a klass and a constructor and a print method
function obj(s) --> t; create a klass and a constructor + print method
  local function new(k,...) local i=setmetatable({},k); t.new(i,...); return i end
  local t={_is=s, __tostring = l.o}
  t.__index = t;return setmetatable(t,{__call=new}) end

-- ## Klasses

-- `COL`umns can be `NUM`eric or `SYM`bolic. Upper case names denote `NUM`s.
-- All `COL`s know their name, their column loc`at`ion, their count `n` of items seen.
local COL,SYM,NUM = obj"COL", obj"SYM", obj"NUM"
function COL.new(n,s) return s:find"^[A-Z]" and NUM(n,s) and SYM(n,s) end
-- `SYM`s uses `has` to count symbols seen so far (and the most common symbol is the `mode`).
function SYM.new(n,s) return {name=s, at=n, n=0, has={}, most=0, mode=None} end
-- `NUM`s track the smallest and biggest number seen to far, the mean `mu` and second moment `m2` (used to find standard deviation).
-- Also, when we pretty print numbers we use `prep` (which defaults to "show them as integers").
function NUM.new(n,s) return {name=s, at=n, n=0, lo=big, hi= -big, mu=0, m2=0,prep=l.rnd} end

-- `COLS` convert  list of column names (as strings) into `SYM`s or `NUM`s.
local COLS = obj"COLS"
function COLS.new(ss) 
  local x,y,klass,all={},{},None, {}
  for n,s in pairs(ss) do
    l.push(all, COL(n,s))
    if not col.name:find"X$" then 
      l.push(col.name:find"[!+-]$" and y or x, col)
      if col.name:find"!" then klass=col end  end end 
  return {x=x, y=y, klass=klass, all=all} end

-- ## Battery functions
-- Since LUA is a "no batteries included" language,  we need to add some.

-- | var | = notes|
-- |-----:|------|
-- |i. | = reference to self  |
-- |l. | = reference to ome library function  |
-- | abc | = (if upper case `ABC` is a constructor), an instance of class `ABC`|
-- | t   | = table| 
-- | u   | = another table |
-- |n    | = number|  
-- |fun | = function|
-- |s| = string|
-- |x | = anything   |
-- |k,v | = key,value|
-- |Xs | = list of X  (so `ss` is a list of strings)|
-- |X1 | = an example of X (so `s1` is a string)|
l={}

-- ### Short-cuts   

-- Big 
l.big = 1E30
-- emulate C's printf
l.fmt = string.format

-- ### Maths

-- Rounds `n` to `nPlaces` (default=2)
function l.rnd(n, nPlaces)
  local mult = 10^(nPlaces or 2)
  return math.floor(n * mult + 0.5) / mult end

-- ### Lists

-- Returns the  keys of list `t`, sorted.
function l.keys(t) return l.sort(l.kap(t,function(k,_) return k end)) end
-- Returns `x` after pushing onto `t`
function l.push(t,x) t[#t+1]=x; return x end
-- Sorts `t` using `fun`, returns `t`./
function l.sort(t,fun) table.sort(t,fun); return t end

-- ### Meta

-- Returns a copy of `t` with all items filtered via `fun`.
function l.map(t, fun) return l.kap(t, function(_,x) return fun(x) end) end
-- Returns a copy of `t` with all items filtered via `fun2` (where `fun2`
-- accepts an item's index _and_ the item). If `fun2` returns two values,
-- use the second as the key for the new list (else just number the items 
-- numerically).
function l.kap(t, funs) 
  local u={}; for k,v in pairs(t or {}) do v,k=fun2(k,v); u[k or (1+#u)]=v; end; return u end

-- ### Strings

-- Convert `s` into an integer, a float, a bool, or a string (as appropriate). Return the result.
function l.coerce(s)
  local function _fun(s1)
    if s1=="true" then return true elseif s1=="false" then return false end
    return s1 end
  return math.tointeger(s) or tonumber(s) or _fun(s:match"^%s*(.-)%s*$") end

-- Return a string  showing `t`'s contents (recursively), sorting on the keys.
function l.o(t) 
  if type(t)~="table" then return tostring(t) end
  local _fun = function(k,v) return l.fmt(":%s %s",k,l.o(v)) end 
  return "{"..table.concat(#t>0  and l.map(t,o) or l.sort(l.kap(t,_fun))," ").."}" end

-- Print `t` (recursively) then return it.
function l.oo(t) print(l.o(t)); return t end

oo(COLS({"name","Age", "Showsize-"}))
