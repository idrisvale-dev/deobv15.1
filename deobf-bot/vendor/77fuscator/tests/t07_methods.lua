-- method definitions and calls (SELF opcode), chained and inherited-ish
local Account = {}
Account.__index = Account
function Account.new(balance)
    return setmetatable({balance = balance}, Account)
end
function Account:deposit(v)
    self.balance = self.balance + v
    return self
end
function Account:get()
    return self.balance
end
local acc = Account.new(100)
acc:deposit(50):deposit(25)
print(acc:get())
local obj = {name = "obj"}
function obj:greet(who)
    return self.name .. " says hi to " .. who
end
print(obj:greet("lua"))
local s = "hello world"
print(s:upper(), s:sub(1, 5), s:len())
print(("x"):rep(5))
