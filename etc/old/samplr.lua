#!/usr/bin/env lua
--<!--- vim: set et sts=3 sw=3 ts=3 : --->
lib = dofile("lib.lua")
local the,help={},[[
samplr: a little smart sampling goes a long way
(multi- objective, semi- supervised, explanations)
(c) Tim Menzies <timm@ieee.org>, BSD-2 license

OPTIONS:
  -b --bins   initial number of bins     = 16
  -c --cohen  small delta = cohen*stdev  = .35
  -f --file   where to read data         = ../data/auto93.csv
  -g --go     start up action            = help
  -h --help   show help                  = false
  -s --seed   random number seed         = 1234567890
  -m --min    minuimum size              = .5
  -r --rest   |rest| = |best|*rest       = 3
  -w --want   plan|xplore|monitor|doubt  = plan
]]
local o,oo = lib.o,lib.oo
return {lib=lib}
