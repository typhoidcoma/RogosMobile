import unreal
EAL=unreal.EditorAssetLibrary
# delete in dependency order: gamemode -> controller -> input context -> actions -> character -> cursors
DELETE=[
  "/Game/TopDown/Blueprints/BP_TopDownGameMode",
  "/Game/TopDown/Blueprints/BP_TopDownController",
  "/Game/TopDown/Input/IMC_Default",
  "/Game/TopDown/Input/Actions/IA_SetDestination_Click",
  "/Game/TopDown/Input/Actions/IA_SetDestination_Touch",
  "/Game/TopDown/Blueprints/BP_TopDownCharacter",
  "/Game/TopDown/Cursor/FX_Cursor_Failure",
  "/Game/TopDown/Cursor/FX_Cursor_Success",
  "/Game/TopDown/Cursor/MI_Cursor_Red",
  "/Game/TopDown/Cursor/M_Cursor",
  "/Game/TopDown/Cursor/SM_CursorMesh",
  "/Game/TopDown/Cursor/SM_CursorMesh_Red",
  "/Game/TopDown/Cursor/T_Arrow",
]
todel=set(DELETE)
print("=== referencer check (external refs = NOT in the delete set) ===")
for p in DELETE:
    refs=EAL.find_package_referencers_for_asset(p, False) or []
    ext=[r for r in refs if not any(r.startswith(d) for d in todel)]
    print("  %-58s refs=%d  EXTERNAL=%s"%(p.split('/')[-1], len(refs), ext if ext else "none"))
print("=== deleting ===")
for p in DELETE:
    if EAL.does_asset_exist(p):
        ok=EAL.delete_asset(p)
        print("  %s %s"%("DEL " if ok else "FAIL", p))
print("DONE delete_cruft")
