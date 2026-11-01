-- numeric for (all step forms) + generic for pairs/ipairs
for i = 1, 5 do io.write(i, " ") end print()
for i = 10, 1, -2 do io.write(i, " ") end print()
for i = 1.5, 3.5, 0.5 do io.write(i, " ") end print()
for i = 5, 1 do io.write("never") end
local t = {"a", "b", "c", "d"}
for i, v in ipairs(t) do print(i, v) end
local m = {x = 1, y = 2, z = 3}
local keys = {}
for k, v in pairs(m) do keys[#keys + 1] = k .. "=" .. v end
table.sort(keys)
print(table.concat(keys, ","))
local sum = 0
for i = 1, 100 do sum = sum + i end
print("sum", sum)
