-- all six comparisons + and/or/not + loadbool patterns
local function cmp(a, b)
    print(a < b, a <= b, a > b, a >= b, a == b, a ~= b)
end
cmp(1, 2)
cmp(2, 2)
cmp(3, 2)
cmp("a", "b")
print(1 < 2 and 2 < 3, 1 > 2 or 3 > 2, not nil, not 0, not "")
local x = 1 < 2
local y = 3 > 4
print(x, y, x and y, x or y)
local v = nil
print(v and "yes" or "no")
local w = false or nil
print(w)
local z = 5 and 10
print(z)
print(1 == 1 and "eq", "a" ~= "b" and "ne")
local p = 10
if p > 5 and p < 20 then print("range") end
if not (p == 9) then print("noteq") end
