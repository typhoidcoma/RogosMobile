"""
Make RogoBot collide at its real (wide quadruped) size and steer around things.

  - Capsule radius 34 -> 45 so the spherical body (radius ~45) stops clipping
    through obstacles. Half-height stays 88 so the tuned mesh offset / gait
    grounding are unchanged.
  - Enable RVO avoidance so the bot locally steers around obstacles/other agents
    on top of the navmesh path ("find its own way however possible").

Pathfinding itself already works (the bot follows a navmesh path via the BT
MoveTo tasks). NOTE on clearance: the RecastNavMesh in the level is built for a
35-radius agent. The bot is now 45 wide, so in very tight (<90cm) gaps it can
brush a wall. If that matters, raise RecastNavMesh-Default 'Agent Radius' to 45
in the level and rebuild paths (Build > Build Paths). We left it at 35 here
because widening the agent fragments the navmesh around this level's closely
-spaced ramp/cube obstacles (a level-layout cleanup, not a character setting).

Run: python C:/Users/tesse/rcpy.py i:/Projects/Unreal/RogosMobile/Tools/Rig/fix_collision_nav.py
"""
import unreal

bp = unreal.EditorAssetLibrary.load_asset("/Game/RogoBot/Character/BP_RogoBot")
cdo = unreal.get_default_object(bp.generated_class())
cap = next(iter(cdo.get_components_by_class(unreal.CapsuleComponent)))
cap.set_editor_property("capsule_radius", 45.0)
cm = next(iter(cdo.get_components_by_class(unreal.CharacterMovementComponent)))
cm.set_editor_property("use_rvo_avoidance", True)
cm.set_editor_property("avoidance_consideration_radius", 400.0)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_asset("/Game/RogoBot/Character/BP_RogoBot", only_if_is_dirty=False)
print("capsule radius ->", cap.get_editor_property("capsule_radius"),
      "| RVO ->", cm.get_editor_property("use_rvo_avoidance"))
