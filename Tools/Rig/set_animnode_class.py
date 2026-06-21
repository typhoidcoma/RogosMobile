import unreal
NODE = "/Game/RogoBot/Anim/ABP_RogoBot.ABP_RogoBot:AnimGraph.AnimGraphNode_ControlRig_1"
CR_CLASS = "/Script/ControlRig.ControlRigBlueprintGeneratedClass'/Game/RogoBot/Anim/CR_RogoBot.CR_RogoBot_C'"

node = unreal.load_object(None, NODE)
anim = node.get_editor_property("node")

ref = unreal.ControlRigAssetStrongReference()
ref.import_text('(BlueprintRigClass=%s)' % CR_CLASS)
print("ref ->", ref.export_text())

anim.set_editor_property("control_rig_asset_reference", ref)
node.set_editor_property("node", anim)

# also flag to draw ref pose from skeleton so rig has a base pose
anim2 = node.get_editor_property("node")
print("node ref now:", anim2.get_editor_property("control_rig_asset_reference").export_text())
unreal.EditorAssetLibrary.save_asset("/Game/RogoBot/Anim/ABP_RogoBot", only_if_is_dirty=False)
print("DONE set class")
