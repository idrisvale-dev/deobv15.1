-- mixed stress: strings, nested functions, coroutines, metatables, loops
local function fib(n)
    if n < 2 then return n end
    return fib(n - 1) + fib(n - 2)
end
print("fib(20)", fib(20))
local co = coroutine.create(function(a, b)
    local x = coroutine.yield(a + b)
    return x * 2
end)
local _, v = coroutine.resume(co, 3, 4)
local _, w = coroutine.resume(co, 10)
print("coroutine", v, w, coroutine.status(co))
local words = {}
for i = 1, 60 do words[i] = "w" .. i end
table.sort(words, function(a, b) return #a > #b or (#a == #b and a < b) end)
print(words[1], words[60], #words)
local mt = {
    __add = function(a, b) return a.v + b.v end,
    __tostring = function(s) return "V(" .. s.v .. ")" end,
}
local function V(x) return setmetatable({v = x}, mt) end
local v1, v2 = V(10), V(32)
print(v1 + v2, tostring(v1))
local s = 0
for i = 1, 100 do
    if i % 3 == 0 then s = s + i
    elseif i % 5 == 0 then s = s - 1
    else s = s + 2 end
end
print("accum", s)
local function outer()
    local t = {}
    for i = 1, 3 do
        t[i] = function() return i * i end
    end
    return t
end
local fns = outer()
print(fns[1](), fns[2](), fns[3]())
local ok, err = pcall(function() error("boom", 0) end)
print(ok, err)
print(string.format("%q", "simple"))
print(string.format("%5.2f|%-4d|", 3.14159, 7))
