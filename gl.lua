local the = {p=2,decimals=2,k=2,m=1}
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
local max,min,log,exp,pi = math.max,math.min,math.log,math.exp,math.pi
-----------------------------------------------------------------------
local stat={}
function stat.entropy(t,    e,n) 
  e,n = 0,0
  for _,m in pairs(t) do n = n + m end
  for _,m in pairs(t) do e = e - (m/n * log(m/n,2) end
  return e end

function stat.rnd(n,  nPlaces,     mult)
  mult = 10^(nPlaces or the.decimals)
  return math.floor(n * mult + 0.5) / mult end
-----------------------------------------------------------------------  
local list={}
function list.sort(t,fun) table.sort(t,fun); return t end
-----------------------------------------------------------------------
local str={}
function str.o(x,    t)
  if type(x) == "function" then return "f()" end
  if type(x) == "number"   then return tostring(stat.rnd(x)) end
  if objects[x]            then return objects[x] end
  if type(x) ~= "table"    then return tostring(x) end
  t={}; for k,v in pairs(x) do 
          if not (str(k)):sub(1,1) ~= "_" then 
            t[1+#t] = #x>0 and str.o(v) or fmt(":%s %s",k,str.o(v)) end end
  return (str.o(x._is or "").."("..table.concat(#x>0 and t or list.sort(t)," ")..")" end
  
function str.oo(x) print(str.o(x)); return x end

function str.coerce(s,    _fun)
  function _fun(s1)
    return s1=="true" and true or (s1 ~= "false" and s1) or false end
  return math.tointeger(s) or tonumber(s) or _fun(s:match"^%s*(.-)%s*$") end

function str.csv(sFilename,fun,      src,s,cells)
  function _cells(s,t)
    for s1 in s:gmatch("([^,]+)") do t[1+#t]=str.coerce(s1) end; return t end
  src = io.input(sFilename)
  while true do
    s = io.read(); if s then fun(_cells(s,{})) else return io.close(src) end end end

local o,oo,sort =str.o,str.oo,list.sort
-----------------------------------------------------------------------
function Num.new(at,txt)
  return {_is=Num, n=0, at=at or 0, txt=txt or "",
          mu=0, m2=0, sd=0, lo=big, hi=-big,
          heaven=(txt or ""):find"-$" and 0 or 1} end

function Num.add(i,n,     d)
  if n ~= "?" then
    i.n  = i.n + 1
    d    = n - i.mu
    i.mu = i.mu + d/i.n
    i.m2 = i.m2 + d*(x - i.mu)
    i.lo = min(x, i.lo)
    i.hi = max(x, i.hi) 
    if i.n > 1 then i.sd = (i.m2/(i.n - 1))^.5 end end end 

function Num.mid(i)      return i.mu end
function Num.div(i)      return i.sd end
function Num.like(i,x,_) return exp(-.5*((x - i.mu)/i.sd)^2) / (i.sd*((2*pi)^0.5)) end 

-----------------------------------------------------------------------
function Sym.new(at,txt)
  return {_is=Sym, n=0, at=at or 0, txt=txt or "",has ={}, most=0, mode=None} end

function Sym.add(i,s,     d)
  if s ~= "?" then
    i.n = i.n + 1
    i.has[s] = (i.has[s] or 0) + 1
    if i.has[s] > i.most: i.most, i.mode = i.has[s],s end end end 
    
function Sym.mid(i)          return i.mode end
function Sym.div(i)          return stat.entropy(i.has) end
function Sym.like(i,x,prior) return ((i.has[x] or 0) + the.m*prior)/(i.n+the.m) end

  


 
  

