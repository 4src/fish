function a() return b.c  end
function d() return 1 end

ok,flag=pcall(a)
print("a",ok,err)

if not ok then print(debug.traceback(err)) end

ok,flag=pcall(d)
print("d",ok,err)

function push(t,x) t[1+#t]=x; return x end

local egs={order={}, index={}}
function eg(s,fun)
  tag,doc = s:match"([^:]+):(.*)"
  egs.index[tag] = push(egs.order, {tag=tag,doc=doc,fun=fun}) end

eg("fred:asdas sassdsa", function (asd) return asdas end)
