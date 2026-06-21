"""Quickly set Locomotor orient-to-ground pins on the live CR (no full rebuild).
Usage: edit the 4 values below, run via rcpy."""
import unreal, sys
PELVIS_PITCH=0.3; PELVIS_ROLL=0.3; FOOT_PITCH=0.3; FOOT_ROLL=0.3
cr=unreal.EditorAssetLibrary.load_asset("/Game/RogoBot/Anim/CR_RogoBot")
ctrl=cr.get_controller_by_name("RigVMModel")
ln=None
for n in ctrl.get_graph().get_nodes():
    ss=n.get_script_struct() if hasattr(n,"get_script_struct") else None
    if ss and "Locomotor" in ss.get_name(): ln=n; break
NP=ln.get_node_path()
ctrl.set_pin_default_value("%s.Pelvis.OrientToGroundPitch"%NP, str(PELVIS_PITCH))
ctrl.set_pin_default_value("%s.Pelvis.OrientToGroundRoll"%NP, str(PELVIS_ROLL))
ctrl.set_pin_default_value("%s.Stepping.OrientFootToGroundPitch"%NP, str(FOOT_PITCH))
ctrl.set_pin_default_value("%s.Stepping.OrientFootToGroundRoll"%NP, str(FOOT_ROLL))
unreal.EditorAssetLibrary.save_loaded_asset(cr)
print("orient set: pelvis(p%.2f r%.2f) foot(p%.2f r%.2f)"%(PELVIS_PITCH,PELVIS_ROLL,FOOT_PITCH,FOOT_ROLL))
