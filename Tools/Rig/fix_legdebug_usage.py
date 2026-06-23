"""
M_LegDebug (the per-leg debug-color material) is applied to SK_RogoBot but lacks the
'Used with Skeletal Mesh' usage flag -> engine warns + falls back to the default material and
recompiles the material every editor launch. Set the flag + resave once to clear it.
Run: python C:/Users/tesse/rcpy.py i:/Projects/Unreal/RogosMobile/Tools/Rig/fix_legdebug_usage.py
"""
import unreal
EAL=unreal.EditorAssetLibrary
PATH="/Game/RogoBot/Viz/M_LegDebug"
m=EAL.load_asset(PATH)
if m is None:
    print("M_LegDebug not found at", PATH); raise SystemExit
before=m.get_editor_property("used_with_skeletal_mesh")
m.set_editor_property("used_with_skeletal_mesh", True)
EAL.save_asset(PATH, only_if_is_dirty=False)
print("used_with_skeletal_mesh: %s -> %s (saved)"%(before, m.get_editor_property("used_with_skeletal_mesh")))
