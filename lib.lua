#!/usr/bin/env lua
-- <!--- vim : set et sts=2 sw=2 ts=2 : --->
-- In this cade, in function argument lists, two spaces denotes
-- "start of optional args" and four spaces denotes "start of local
-- variables". Also:
--
-- | `i.`   | = reference to self |
-- |-------:|---------------------|
-- | `t`    | = table | 
-- | `u`    | = another table (often generated from `t`) |
-- | `n`    | = number |  
-- | `s`    | = string |
-- | `x`    | = anything |
-- | `k,v`  | = key,value |
-- | `fun`  | = function |
-- | `_fun` | = a local function inside the current function |
-- | `Xs`   | = list of X  (so `ss` is a list of strings) |
-- | `X1`   | = an example of X (so `s1` is a string) |
-- | `abc`  | = (if upper case `ABC` is a constructor), an instance of class `ABC` |

local l={}

-- ### Linting the code
local b4={}; for k,_ in pairs(_ENV) do b4[k] = k end
function l.rogues()
  for k,_ in pairs(_ENV) do if not b4[k] then 
    io.stderr:write("-- warning: rogue local [",k,"]\n") end end end

-- ### Short-cuts   

-- A big number 
l.big = 1E30
-- emulate C's printf
l.fmt = string.format

-- ### Maths

-- Rounds `n` to `nPlaces` (default=2)
function l.rnd(n,  nPlaces)
  local mult = 10^(nPlaces or 2)
  return math.floor(n * mult + 0.5) / mult end

-- Generate random numbers.
local Seed = 937162211
-- Returns random integers `nlo` to `nhi`.
function l.rint(nlo,nhi)  return math.floor(0.5 + l.rand(nlo,nhi)) end
-- Returns random floats `nlo` to `nhi` (defaults 0 to 1)
function l.rand(nlo,nhi) 
  nlo, nhi = nlo or 0, nhi or 1
  Seed = (16807 * Seed) % 2147483647
  return nlo + (nhi-nlo) * Seed / 2147483647 end

-- ### Meta

-- Returns a copy of `t` with all items filtered via `fun2` (where `fun2`
-- accepts an item's index _and_ the item). If `fun2` returns two values,
-- use the second as the key for the new list (else just number the items 
-- numerically).
function l.kap(t, fun2) 
  local u={}; for k,v in pairs(t or {}) do v,k=fun2(k,v); u[k or (1+#u)]=v; end; return u end
-- Returns a copy of `t` with all items filtered via `fun`.
function l.map(t, fun) return l.kap(t, function(_,x) return fun(x) end) end

-- ### Lists

-- Sorts `t` using `fun`, returns `t`.
function l.sort(t,fun) table.sort(t,fun); return t end
-- Returns the  keys of list `t`, sorted.
function l.keys(t) return l.sort(l.kap(t,function(k,_) return k end)) end
-- Returns `x` after pushing onto `t`
function l.push(t,x) t[#t+1]=x; return x end

-- ### Strings

-- Convert `s` into an integer, a float, a bool, or a string (as appropriate). Return the result.
function l.coerce(s)
  local function _fun(s1)
    return s1=="true" and true or (s1 ~= "false" and s1) or false end
  return math.tointeger(s) or tonumber(s) or _fun(s:match"^%s*(.-)%s*$") end

-- Return a string  showing `t`'s contents (recursively), sorting on the keys.
function l.o(t) 
  if type(t)~="table" then return tostring(t) end
  local _fun = function(k,v) return l.fmt(":%s %s",k,l.o(v)) end 
  pre = t.a or ""
  return pre.."{"..table.concat(#t>0  and l.map(t,l.o) or l.sort(l.kap(t,_fun))," ").."}" end

-- Print `t` (recursively) then return it.
function l.oo(t) print(l.o(t)); return t end

-- If the command line mentions key `k` then change `s` to a new value.
-- If the old value is a boolean, just flip the old. If not found, return nil.
function l.cli(k,s)
  for n,x in ipairs(arg) do
    if x=="-"..(k:sub(1,1)) or x=="--"..k then
      return s=="false" and "true" or s=="true" and "false" or arg[n+1] end end end

-- Parse `help` text to extract settings.
function l.settings(d,s,  prep)
  s:gsub("\n[%s]+[-][%S][%s]+[-][-]([%S]+)[^\n]+= ([%S]+)",
         function(k,v) d[k] = l.coerce(prep and prep(k,v) or v) end) 
  return d end

-- ### Klasses

-- Create a klass and a constructor and a print method
function l.obj(s,    t) 
  t={__tostring=function(s) return l.o(s) end}; t.__index = t
  return setmetatable(t, {__tostring=l.o, __call=function(_,...) 
    local i=setmetatable({a=s},t); return setmetatable(t.new(i,...) or i,t) end}) end

-- ### Test Engine

local egs={}
-- `eg("fred",function() return 1==2 end)` creates a test
-- called _fred_ which can be called from the command-line using
-- `-g fred`.
function l.eg(s,fun) egs[1+#egs] = {name=s, fun=fun} end

-- Show the help (if asked to).
-- Run one test, or if the test is `all`, then run all (printing
-- "FAIL" or "PASS" as you go). 
-- Check for stray globals.  Return to the operating system the number
-- of failures (so zero means "everything is ok").
function l.main(help,settings)
  if settings.help then os.exit(print("\n"..help)) end
  local fails,saved=0,{}
  for k,v in pairs(settings) do saved[k]=v end
  for _,sfun in pairs(egs) do
    local s, fun = sfun.name, sfun.fun
    if settings.go == s or settings.go == "all" then
      local failed, also = l.failure(saved,settings,fun)
      if   failed 
      then fails = fails + 1
           print(l.fmt("❌ FAIL %s %s",s,also)) 
      else print(l.fmt("✅ PASS %s",s)) end end end
  print(l.fmt("🔆 failure(s) = %s",fails)) 
  l.rogues()
  os.exit(fails) end

-- Return `true,message` if `fun` fails. Before running,
-- reset `settings` to the saved values. Reset random number
-- generators. Print a stacktrace of there is a failure.
function l.failure(saved,settings,fun)
  for k,v in pairs(saved) do settings[k]=v end 
  Seed = settings.seed
  math.randomseed(l.Seed)
  local ok,val = pcall(fun)
  if not ok then print(debug.traceback()); return true, val
  elseif val==false then return true, "test returned false"
  else return false, "all good" end end

return l
