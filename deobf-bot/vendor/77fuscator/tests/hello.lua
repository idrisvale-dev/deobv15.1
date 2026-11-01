local message = "hello from the deobfuscator test suite"
local secret = "s3cr3t-p4ssw0rd-12345"
local function greet(name)
    return "welcome, " .. name .. "!"
end
print(message)
print(greet("77fuscator"))
for i = 1, 3 do
    print("iteration number " .. tostring(i))
end
if secret == "s3cr3t-p4ssw0rd-12345" then
    print("secret matched correctly")
end
