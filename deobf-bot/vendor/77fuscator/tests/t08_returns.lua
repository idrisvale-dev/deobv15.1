-- multiple returns + tailcalls
local function three()
    return 1, 2, 3
end
print(three())
local a, b, c = three()
print(a, b, c)
local function tail()
    return three()
end
print(tail())
local function wrap(...)
    return (...)
end
print(wrap("only-first"))
local function cond_tail(x)
    if x > 0 then
        return three()
    end
    return -1, -2
end
print(cond_tail(5))
print(cond_tail(-5))
local function depth(n)
    if n == 0 then return 0 end
    return depth(n - 1) -- tailcall recursion
end
print("depth", depth(10000))
local t = {three()}
print(#t)
print((three()))
