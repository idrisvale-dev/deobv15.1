print('IronBrew 2:tm: Benchmark-y Meme')
local Iterations = 10000
print('Iterations: ' .. tostring(Iterations))
print('CLOSURE testing.')
local Start = os.clock();
for Idx = 1, Iterations do
    (function()
        if (not true) then
            print 'Hey gamer.';
        end;
    end)();
end;
print('Time:', os.clock() - Start .. 's');
print('SETTABLE testing.')
Start = os.clock();
local T = {}
for Idx = 1, Iterations do
    T[tostring(Idx)] = 'EPIC GAMER ' .. tostring(Idx)
end
print('Time:', os.clock() - Start .. 's');
print('GETTABLE testing.')
Start = os.clock();
local V
for Idx = 1, Iterations do
    V = T[tostring(Idx)]
end
print('Time:', os.clock() - Start .. 's');
print('done: 77fuscator benchmark complete')
