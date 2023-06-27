local b4={}; for k,_ in pairs(_ENV) do b4[k] = k end
local the = {seed=1234567891, min= .5, rest=3, 
             beam=10, file="../data/auto93.csv"}

-- ## Conventions

-- | `i.` | = reference to self  |
-- |-----:|------|
-- | `t`   | = table| 
-- | `u`   | = another table (often generated from `t`) |
-- |`n`    | = number|  
-- |`fun` | = function|
-- |`_fun` | = a local function inside the current function |
-- |`s`| = string|
-- |`x` | = anything   |
-- |`k,v` | = key,value|
-- |`Xs` | = list of X  (so `ss` is a list of strings)|
-- |`X1` | = an example of X (so `s1` is a string)|
-- | `abc` | = (if upper case `ABC` is a constructor), an instance of class `ABC`|

-- ## Misc stuff

-- ### Short-cuts   

-- A big number 
local big = 1E30
-- emulate C's printf
local fmt = string.format

-- ### Maths

-- Rounds `n` to `nPlaces` (default=2)
local function rnd(n, nPlaces)
  local mult = 10^(nPlaces or 2)
  return math.floor(n * mult + 0.5) / mult end

-- ### Meta

-- Returns a copy of `t` with all items filtered via `fun2` (where `fun2`
-- accepts an item's index _and_ the item). If `fun2` returns two values,
-- use the second as the key for the new list (else just number the items 
-- numerically).
local function kap(t, fun2) 
  local u={}; for k,v in pairs(t or {}) do v,k=fun2(k,v); u[k or (1+#u)]=v; end; return u end
-- Returns a copy of `t` with all items filtered via `fun`.
local function map(t, fun) return kap(t, function(_,x) return fun(x) end) end

-- ### Lists

-- Sorts `t` using `fun`, returns `t`./
local function sort(t,fun) table.sort(t,fun); return t end
-- Returns the  keys of list `t`, sorted.
local function keys(t) return sort(kap(t,function(k,_) return k end)) end
-- Returns `x` after pushing onto `t`
local function push(t,x) t[#t+1]=x; return x end

-- ### Strings

-- Convert `s` into an integer, a float, a bool, or a string (as appropriate). Return the result.
local function coerce(s)
  local function _fun(s1)
    return s1=="true" and true or (s1 ~= "false" and s1) or false
  return math.tointeger(s) or tonumber(s) or _fun(s:match"^%s*(.-)%s*$") end

-- Return a string  showing `t`'s contents (recursively), sorting on the keys.
local function o(t) 
  if type(t)~="table" then return tostring(t) end
  local _fun = function(k,v) return fmt(":%s %s",k,o(v)) end 
  pre = t._is or ""
  return pre.."{"..table.concat(#t>0  and map(t,o) or sort(kap(t,_fun))," ").."}" end

-- Print `t` (recursively) then return it.
local function oo(t) print(o(t)); return t end

-- ## Klasses

-- Create a klass and a constructor and a print method
local function obj(s) 
  local function new(k,...) local i=setmetatable({},k); t.new(i,...); return i end
  local t={_is=s, __tostring = l.o}
  t.__index = t;return setmetatable(t,{__call=new}) end


-- `COL`umns can be `NUM`eric or `SYM`bolic. Upper case names denote `NUM`s.
-- All `COL`s know their name, their column loc`at`ion, their count `n` of items seen.
local SYM,NUM,COL =  obj"SYM", obj"NUM"
function COL(n,s) 
  return s:find"^[A-Z]" and NUM(n,s) or SYM(n,s) end
-- `SYM`s uses `has` to count symbols seen so far (and the most common symbol is the `mode`).
function SYM.new(i,n,s) 
  i.name=s or ""; i.at=n or 0; i.n=0, i.has={}; i.most=0; i.mode=None end
-- `NUM`s tracks the smallest and biggest number seen to far (in `lo` and `hi`) as well as the the mean `mu` and second moment `m2` (used to find standard deviation).
-- Also, `pretty` controls how we report numbers (and this switches to "%g" if we ever see a float).
-- Any name ending with `-` is
-- something we want to _minimize_ (so we give it a negative weight).
function NUM.new(i,n,s) 
  i.name=s or ""; i.at=n or 0; i.n=0; i.lo=big; i.hi= -big; i.mu=0; i.m2=0; 
  i.pretty = "%.0f"
  i.w = i.name:find"-$" and -1 or 1  end

-- `COLS` convert  list of column names (as strings) into `SYM`s or `NUM`s. Column names ending in a goal symbol
-- (`+-!`) are dependent `y` features (and the others are independent `x` features). 
local COLS = obj"COLS"
function COLS.new(i,ss) 
  i.x, i.y, i.all = {},{},{}
  for n,s in pairs(ss) do
    local col = l.push(i.all, COL(n,s))
    if not s:find"X$" then 
      l.push(s:find"[!+-]$" and i.y or i.x, col)
      if s:find"!$" then i.klass=col end  end end  end

