function a() return b.c  end
function d() return 1 end

ok,flag=pcall(a)
print("a",ok,err)

if not ok then print(debug.traceback(err)) end

ok,flag=pcall(d)
print("d",ok,err)
