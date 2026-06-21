"""
Gives RogoBot per-part collision: auto-generates a PhysicsAsset (one body per
bone: body, hip/knee/ankle x4) for SK_RogoBot and makes the SkeletalMeshComponent
physically present so the limbs/body push movable props + register hits.

The capsule STILL drives locomotion (unchanged) -- these per-bone bodies are
KINEMATIC (follow the animated pose); they do not move the character.

Run: python C:/Users/tesse/rcpy.py i:/Projects/Unreal/RogosMobile/Tools/Rig/make_phys_asset.py
"""
import unreal
EAL=unreal.EditorAssetLibrary
s=unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
SK="/Game/RogoBot/Anim/SK_RogoBot"
PA="/Game/RogoBot/Anim/SK_RogoBot_PhysicsAsset"
sk=EAL.load_asset(SK)

# 1) PhysicsAsset with auto-generated per-bone bodies ("as if FBX import"), assigned to the mesh.
if EAL.does_asset_exist(PA):
    pa=EAL.load_asset(PA); s.assign_physics_asset(sk, pa)
else:
    pa=s.create_physics_asset(sk, set_to_mesh=True)
EAL.save_loaded_asset(sk)
EAL.save_loaded_asset(pa)
print("PHYS asset:", pa.get_path_name())

# 2) Make the mesh's per-bone bodies physically interact with the world.
#    PhysicsActor profile = QueryAndPhysics + block: kinematic limbs push simulating
#    props and are hittable by traces/overlaps. The capsule (Pawn) still owns movement;
#    CharacterMovement ignores owned components, so this does not fight locomotion.
bp=EAL.load_asset("/Game/RogoBot/Character/BP_RogoBot")
cdo=unreal.get_default_object(bp.generated_class())
mesh=cdo.get_editor_property("mesh")
mesh.set_collision_profile_name("PhysicsActor")
mesh.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
print("MESH collision:", mesh.get_collision_enabled(), mesh.get_collision_profile_name())
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
EAL.save_asset("/Game/RogoBot/Character/BP_RogoBot", only_if_is_dirty=False)
print("DONE make_phys_asset")
