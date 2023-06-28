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

-- `SYM`s uses `has` to count symbols seen so far (and the most common symbol is the `mode`).
function SYM.new(i,n,s) 
  return {name=s or "", at=n or 0, n=0, has={}, most=0, mode=nil}  end

-- `NUM`s tracks the smallest and biggest number seen to far (in `lo` and `hi`) 
-- as well as the the mean `mu` and second moment `m2` (used to find standard deviation).
-- Also, `pretty` controls how we report numbers (and this switches to "%g" 
-- if we ever see a float).  Any name ending with `-` is something we want to _minimize_ 
-- (so we give it a negative weight).
function NUM.new(i,n,s) 
  return {name=s or "",  at=n or 0,  n=0, 
          lo=l.big, hi= -l.big, mu=0,  m2=0, 
          pretty="%.0f", w=(s or ""):find"-$" and -1 or 1} end

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

-- ## Demos
eg("bad", function() return 1==2 end)
eg("the", function() oo(the) end)

-- ## Start-up
if   not pcall(debug.getlocal,4,1) 
then the = l.cli(the, help)
     l.run(the) 
else return {NUM=NUM,SYM=SYM} end
