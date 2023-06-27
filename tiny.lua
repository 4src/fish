local the = {seed=1234567891, min= .5, rest=3, 
             beam=10, file="../data/auto93.csv"}

local big,coerce, fmt,kap,keys,map,o,oo,push,rnd,sort 
-------------------------------------------------------
local COL,COLS,DATA,NUM<SYM
function COL(n,s) return s:find"^[A-Z]" and NUM(n,s) and SYM(n,s) end

function SYM(n,s) return {name=s, at=n, n=0, has={}, most=0, mode=None} end

function NUM(n,s) return {name=s, at=n, n=0, lo=big, hi= -big, mu=0, m2=0,prep=rnd} end

function COLS(ss) 
  local x,y,klass,all={},{},None, kap(ss,COL)
  for _,col in pairs(all) do
    if not col.name:find"X$" then 
      push(col.name:find"[!+-]$" and y or x, col)
      if col.name:find"!" then klass=col end  end end 
  return {x=x, y=y, klass=klass, all=all} end
-------------------------------------------------------
big = 1E30
fmt = string.format

-- ### Maths
function rnd(n, nPlaces) 
  local mult = 10^(nPlaces or 2)
  return math.floor(n * mult + 0.5) / mult end

-- ### Lists
function keys(t) return sort(kap(t,function(k,_) return k end)) end
function push(t,x) t[#t+1]=x; return x end
function sort(t,f) table.sort(t,f); return t end

-- ### Meta
function kap(t, fun) 
  local u={}; for k,v in pairs(t or {}) do v,k=fun(k,v); u[k or (1+#u)]=v; end; return u end

function map(t, fun) return kap(t, function(_,v) return fun(v) end) end

-- ### Strings
function coerce(s,    fun) 
  function fun(s1)
    if s1=="true" then return true elseif s1=="false" then return false end
    return s1 end
  return math.tointeger(s) or tonumber(s) or fun(s:match"^%s*(.-)%s*$") end

function o(t) 
  if type(t)~="table"    then return tostring(t) end
  local fun = function(k,v) return fmt(":%s %s",k,o(v)) end 
  return "{"..table.concat(#t>0  and map(t,o) or sort(kap(t,fun))," ").."}" end

function oo(t) print(o(t)); return t end

oo(COLS({"name","Age", "Showsize-"}))
