-- table constructors incl. >50 array items (SETLIST batches) and mixed parts
local small = {1, 2, 3}
print(#small, small[1], small[3])
local big = {}
for i = 1, 120 do big[i] = i * 2 end
local lit = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,
             21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,
             41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60}
print(#lit, lit[1], lit[31], lit[60])
local mixed = {10, 20, name = "mix", [100] = "hundred", 30, flag = true}
print(#mixed, mixed[1], mixed[2], mixed[3], mixed.name, mixed[100], mixed.flag)
local nested = {a = {b = {c = {1, 2, 3}}}}
print(nested.a.b.c[2])
local t2 = {[1] = "one", [2] = "two"}
print(#t2, t2[1], t2[2])
table.insert(big, 999)
print(#big, big[#big])
print(select('#', unpack({5, 6, 7})))
