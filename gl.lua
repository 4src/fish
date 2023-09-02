local the = {p=2,decimals=2}
-----------------------------------------------------------------------
local objects={}
local function obj(s) local x={}; objects[s]=x; return x end
local Num,Sym = obj"Num", obj"Sym"

local function like(i,...) return i._is.like(i,...) end
local function dist(i,...) return i._is.dist(i,...) end
local function add(i,x)    return i._is.add(i,x) end
local function div(i)      return i._is.div(i) end
local function mid(i)      return i._is.mid(i) end
-----------------------------------------------------------------------
local big = 1E30
local fmt = string.format
local max, min, log = math.max, math.min, math.log

local function entropy(t,    e,n) 
  e,n = 0,0
  for _,m in pairs(t) do n = n + m end
  for _,m in pairs(t) do e = e - (m/n * log(m/n,2) end
  return e end

local function sort(t,fun) table.sort(t,fun); return t end

local function rnd(n,  nPlaces,     mult)
  mult = 10^(nPlaces or the.decimals)
  return math.floor(n * mult + 0.5) / mult end

local function o(x,    t)
  if type(x) == "function" then return "f()" end
  if type(x) == "number"   then return tostring(rnd(x)) end
  if objects[x]            then return objects[x] end
  if type(x) ~= "table"    then return tostring(x) end
  t={}; for k,v in pairs(x) do 
          if not (str(k)):sub(1,1) ~= "_" then 
            t[1+#t] = #x>0 and o(v) or fmt(":%s %s",k,o(v)) end end
  return (o(x._is or "").."("..table.concat(#x>0 and t or sort(t)," ")..")" end
  
local function oo(x) print(o(x)); return x end

local function coerce(s,    _fun)
  function _fun(s1)
    return s1=="true" and true or (s1 ~= "false" and s1) or false end
  return math.tointeger(s) or tonumber(s) or _fun(s:match"^%s*(.-)%s*$") end

local function csv(sFilename,fun,      src,s,cells)
  function cells(s,t)
    for s1 in s:gmatch("([^,]+)") do t[1+#t]=coerce(s1) end; return t end
  src = io.input(sFilename)
  while true do
    s = io.read(); if s then fun(cells(s,{})) else return io.close(src) end end end
-----------------------------------------------------------------------
function Num.new(at,txt)
  return {_is=Num, n=0, at=at or 0, txt=txt or "",
          mu=0, m2=0, lo=big, hi=-big,
          heaven=(txt or ""):find"-$" and 0 or 1} end

function Num.add(i,n,     d)
  if n ~= "?" then
    i.n  = i.n + 1
    d    = n - i.mu
    i.mu = i.mu + d/i.n
    i.m2 = i.m2 + d*(x - i.mu)
    i.lo = min(x, i.lo)
    i.hi = max(x, i.hi) end end 

function Num.mid(i) return i.mu end
function Num.div(i) return (i.m2/(i.n - 1))^.5 end
-----------------------------------------------------------------------
function Sym.new(at,txt)
  return {_is=Sym, n=0, at=at or 0, txt=txt or "",has ={}, most=0, mode=None} end

function Sym.add(i,s,     d)
  if s ~= "?" then
    i.n = i.n + 1
    i.has[s] = (i.has[s] or 0) + 1
    if i.has[s] > i.most: i.most, i.mode = i.has[s],s end end end 
    
function Sym.mid(i) return i.mode end
function Sym.div(i) return entropy(i.has) end
  


 
  

