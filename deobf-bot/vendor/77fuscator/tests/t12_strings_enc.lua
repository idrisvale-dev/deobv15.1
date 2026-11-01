-- many string literals, exercising string encryption recovery
local canary = "CANARY-literal-7f3a9b-wee"
local greetings = {"hello", "hi", "hey", "howdy", "greetings", "salutations"}
local function banner(name)
    return "===[" .. name .. "]===" .. " " .. greetings[1] .. " " .. greetings[6]
end
print(banner("deobfuscator"))
print(canary)
local phrases = {}
for i = 1, 30 do
    phrases[i] = "phrase-number-" .. i .. "-suffix"
end
print(phrases[1], phrases[15], phrases[30], #phrases)
local mixed = {
    key1 = "value1",
    key2 = "value2",
    ["literal key"] = "literal value",
    "positional",
}
print(mixed.key1, mixed.key2, mixed["literal key"], mixed[1])
local long = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
print(#long, long .. "!")
local s = "The quick brown fox jumps over the lazy dog"
print(s:upper():sub(1, 20))
print(("x,y,z"):gsub(",", ";"))
