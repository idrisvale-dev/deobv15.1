-- closures + upvalues, including shared upvalues between sibling closures
local function counter()
    local n = 0
    return function()
        n = n + 1
        return n
    end
end
local c1, c2 = counter(), counter()
print(c1(), c1(), c1(), c2())
local function make_pair()
    local shared = 0
    local function inc() shared = shared + 1 end
    local function get() return shared end
    return inc, get
end
local inc, get = make_pair()
inc() inc() inc()
print("shared", get())
local fns = {}
for i = 1, 3 do
    local x = i * 10
    fns[i] = function() return x end
end
print(fns[1](), fns[2](), fns[3]())
local outer = 1
local function mid()
    local midv = 2
    return function()
        outer = outer + 10
        return outer + midv
    end
end
local deep = mid()
print(deep(), deep(), outer)
