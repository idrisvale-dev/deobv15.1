-- varargs: ..., select('#'), select(n), pack/unpack roundtrip
local function count(...)
    return select('#', ...)
end
print(count(), count(1), count(nil, nil), count(1, nil, 3))
local function nth(n, ...)
    return select(n, ...)
end
print(nth(2, "a", "b", "c"))
local function pack(...)
    return {n = select('#', ...), ...}
end
local p = pack(10, 20, 30)
print(p.n, p[1], p[2], p[3])
local function sum(...)
    local s = 0
    for _, v in ipairs({...}) do s = s + v end
    return s
end
print(sum(1, 2, 3, 4, 5))
local function passthru(...)
    return ...
end
print(passthru("x", "y", "z"))
local function tail_all(...)
    return count(...)
end
print(tail_all(9, 8, 7, 6))
print((...))
