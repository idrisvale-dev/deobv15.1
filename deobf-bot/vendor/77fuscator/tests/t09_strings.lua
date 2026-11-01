-- string ops + concat chains
local parts = {}
for i = 1, 5 do parts[#parts + 1] = "item" .. i end
print(table.concat(parts, "|"))
local s = "a" .. "b" .. "c" .. "d"
print(s, #s)
print(("fmt"):format())
print(string.format("%d-%s-%.2f", 42, "str", 1.5))
print(("hello"):find("ll"))
print(("hello"):gsub("l", "L"))
print(("one two three"):match("(%w+) (%w+)"))
local long = ("ab"):rep(10)
print(#long, long:sub(5, 8))
print("x" .. 1 .. "y" .. 2.5)
print(tostring(nil), tostring(true), tostring(12))
