--[[ MAXIMAL recovery: centuration8th.lua
   Family: Centurion v6.1, 162529 bytes. Status: decode stops at composition;
   everything below is recovered verbatim; stubs are EMPTY
   tables standing in for game/remote content (Pilgrammed).
   Readable target met; runnable target needs that content. ]]

-- ---- Part 1: behavior prefix (init + probes, in order) ----
local Lighting = game:GetService("Lighting")
local MarketplaceService = game:GetService("MarketplaceService")
local Camera = Instance.new("Camera")
Camera:Destroy()
Camera:Destroy()
local ScreenGui = Instance.new("ScreenGui")
local Path2D = Instance.new("Path2D")
Path2D.Parent = ScreenGui
Path2D:SetControlPoints({ Path2DControlPoint.new(UDim2.fromOffset(99, 0)), Path2DControlPoint.new(UDim2.fromOffset(256, 0)) })
Path2D:InsertControlPoint(1, Path2DControlPoint.new(UDim2.fromOffset(181, 0)))
Path2D:GetControlPoints()
Path2D:Destroy()
ScreenGui:Destroy()
-- loadstring() of 14 bytes: "return 'aurnj'"

-- ---- Part 2: decoded string pool (23 entries) ----
local __POOL = {
  [12] = "GetTiltSpeed",
  [12] = "getmetatable",
  [12] = "setmetatable",
  [13] = "ZoomToExtents",
  [14] = "ColorShift_Top",
  [15] = "GetRenderCFrame",
  [15] = "getrawmetatable",
  [16] = "GetControlPoints",
  [16] = "ScreenPointToRay",
  [16] = "SetCameraPanMode",
  [16] = "SetControlPoints",
  [18] = "InsertControlPoint",
  [18] = "MarketplaceService",
  [18] = "Path2DControlPoint",
  [18] = "PointToObjectSpace",
  [18] = "ViewportPointToRay",
  [18] = "WorldToScreenPoint",
  [20] = "WorldToViewportPoint",
  [23] = "GetPartsObscuringTarget",
  [24] = "GetLargestCutoffDistance",
  [28] = "PromptBundlePurchaseFinished",
  [85] = "This environment is not supported. Verify that the debug library is fully accessible.",
  [89] = "This environment is not supported. Verify that the coroutine library is fully accessible.",
}

-- ---- Part 3: composition stubs (EMPTY -- content lives in-game) ----
-- The VM died here: script error: Script:1: attempt to index nil with number
local QS, S, I, D, T = {}, {}, {}, {}, {}  -- register file, stacks, upvalues, consts, temps
-- TODO(game): populate from Pilgrammed remote/content tables.
return { pool = __POOL, registers = { QS = QS, S = S, I = I, D = D, T = T } }
