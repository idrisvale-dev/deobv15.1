-- if/elseif/else + while + repeat + break
local function classify(n)
    if n < 0 then
        return "neg"
    elseif n == 0 then
        return "zero"
    elseif n < 10 then
        return "small"
    elseif n < 100 then
        return "medium"
    else
        return "big"
    end
end
for _, n in ipairs({-5, 0, 4, 42, 300}) do print(n, classify(n)) end
local i = 0
while i < 5 do
    i = i + 1
    if i == 3 then break end
    print("while", i)
end
local j = 10
repeat
    j = j - 3
    print("repeat", j)
until j <= 1
local k = 0
while true do
    k = k + 1
    if k >= 3 then break end
end
print("done", k)
