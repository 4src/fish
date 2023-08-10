#!/usr/bin/env lua
-- vim: set et sts=2 sw=2 ts=2 :
local b4={}; for k,v in pairs(_ENV) do b4[k]=k end
local l,eg,the,help = {},{},{},[[

xai: multi-goal semi-supervised explanation
(c) 2023 Tim Menzies <timm@ieee.org> BSD-2

USAGE: lua xai.lua [OPTIONS] [-g ACTIONS]

OPTIONS:
  -b  --bins    initial number of bins       = 16
  -c  --cliffs  cliff's delta threshold      = .147
  -d  --d       different is over sd*d       = .35
  -f  --file    data file                    = ../etc/data/auto93.csv
  -F  --Far     distance to distant          = .95
  -g  --go      start-up action              = nothing
  -h  --help    show help                    = false
  -H  --Halves  search space for clustering  = 512
  -m  --min     size of smallest cluster     = .5
  -M  --Max     numbers                      = 512
  -p  --p       dist coefficient             = 2
  -r  --rest    how many of rest to sample   = 4
  -R  --Reuse   child splits reuse a parent pole = true
  -s  --seed    random number seed           = 937162211
]]

function l.obj(s,    t) 
  t = {__tostring=l.o}
  t.__index = t
  return setmetatable(t, {__call=function(_,...) 
    local self=setmetatable({a=s},t); 
    return setmetatable(t.new(self,...) or self,t) end}) end

local COL,NUM,SYM,ROW,SHEET
local oo

COL=l.obj"COL"
function COL:new(nat,sname)  self.at,self.name = nat,sname end
function COL:fred() return self.at - 100 end
---------
l.big=1E30
l.fmt=string.format

function l.same(x) return x end

function l.lt(x) return function(t1,t2) return t1[x] < t2[x] end end
function l.sort(t,fun) 
  if #t==0 then t = l.list(t) end
  if #t==0 then return {} end
  table.sort(t,fun)
  return t end

function l.list(t) return l.map(t,l.same) end

function l.map(t,fun) return l.kap(t, function(_,x) return fun(x) end) end
function l.kap(t1,fun2,     t2) 
  t2={}; for k,v in pairs(t1 or {}) do v,k=fun2(k,v); t2[k or (1+#t2)]=v; end; return t2 end

l.Seed = 937162211
function l.rint(nlo,nhi)  return math.floor(0.5 + l.rand(nlo,nhi)) end
function l.rand(nlo,nhi) 
  nlo, nhi = nlo or 0, nhi or 1
  l.Seed = (16807 * l.Seed) % 2147483647
  return nlo + (nhi-nlo) * l.Seed / 2147483647 end

function l.oo(t) print(l.o(t)); return t end
function l.o(t,     _fun,pre) 
  if type(t) ~= "table" then return tostring(t) end
  _fun = function(k,v) return l.fmt(":%s %s",k,l.o(v)) end 
  t = #t>0 and l.map(t,l.o) or l.sort(l.kap(t,_fun))
  return (t.a or "").."{"..table.concat(t," ").."}" end

oo=l.oo

function l.coerce(s,    _fun)
  function _fun(s1)
    return s1=="true" and true or (s1 ~= "false" and s1) or false end
  return math.tointeger(s) or tonumber(s) or _fun(s:match"^%s*(.-)%s*$") end

function l.cells(s,    t)
  t={}; for s1 in s:gmatch("([^,]+)") do t[1+#t] = l.coerce(s1) end; return t end

function l.csv(sFilename,fun,      src,s) 
  src = io.input(sFilename)
  while true do
    s = io.read(); if s then fun(l.cells(s)) else return io.close(src) end end end

function l.cli(t,help)
  for k,v in pairs(t) do
    v = tostring(v)
    for n,x in ipairs(arg) do
      if x=="-"..(k:sub(1,1)) or x=="--"..k then
        v = v=="false" and "true" or v=="true" and "false" or arg[n+1] end end 
    t[k] = l.coerce(v) end
  return t end

function l.settings(s,       t)
  t={}
  s:gsub("\n[%s]+[-][%S][%s]+[-][-]([%S]+)[^\n]+= ([%S]+)",function(k,v) t[k]=l.coerce(v) end)
  return t end

function l.rogues()
  for k,_ in pairs(_ENV) do if not b4[k] then 
    io.stderr:write("-- warning: rogue local [",k,"]\n") end end end
-----------
function eg(s,fun) esg[1+#egs] = {name=s, fun=fun} end

eg{asdas = "as asd as das as asd ",function()  three() return 4 end)

function eg.one() return 3 end
function eg.two() return 4 end

for k,v in pairs(eg) do print(k,v) end
the = l.settings(help)

l.rogues()

