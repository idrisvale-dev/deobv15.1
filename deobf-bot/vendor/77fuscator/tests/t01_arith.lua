-- arithmetic + RK constant operands in all positions
local a = 7
local b = 3
print(a + b, a - b, a * b, a / b, a % b, a ^ b)
print(10 + a, a + 10, 10 - a, a - 10, 2 * a, a * 2)
print(100 / a, a / 2, a % 6, a % 100, 2 ^ a, a ^ 2)
print(1 + 2 * 3 ^ 2, (1 + 2) * 3, 2 ^ 3 ^ 2)
print(-a, -(-a), a + -b)
local big = 2
for i = 1, 5 do big = big * big end
print(big)
print(7.5 % 2, 7 % 3, 17 % 5)
local m = -7
local n = 3
print(m % n, n % m, m % 3, m % 5.5)
print(1/3, 10/4, 2^0.5)
