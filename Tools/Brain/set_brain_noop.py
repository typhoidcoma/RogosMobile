"""
Neutralize BT_RogoBrain to a no-op (root = idle Wait) so it no longer issues
navmesh MoveTo. The bot now drives itself via sensing-based steering in
BP_RogoBot. The BT is kept (RunBehaviorTree still creates the blackboard that
SenseInfluence writes to) but does nothing.
Run: python C:/Users/tesse/rcpy.py i:/Projects/Unreal/RogosMobile/Tools/Brain/set_brain_noop.py
"""
import unreal
bt=unreal.EditorAssetLibrary.load_asset("/Game/RogoBot/AI/BT_RogoBrain")
root=unreal.new_object(unreal.BTComposite_Selector, bt); root.set_editor_property("node_name","Idle (steering is in BP_RogoBot)")
wait=unreal.new_object(unreal.BTTask_Wait, bt); wait.set_editor_property("node_name","Wait")
try: wait.set_editor_property("wait_time", 99999.0)
except Exception as e: print("wait_time set:", e)
cc=unreal.BTCompositeChild(); cc.set_editor_property("child_task", wait)
root.set_editor_property("children", [cc])
bt.set_editor_property("root_node", root)
unreal.EditorAssetLibrary.save_loaded_asset(bt)
print("BT set to no-op idle")
