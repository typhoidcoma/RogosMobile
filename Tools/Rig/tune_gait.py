"""Set ALL gait pins on the live CR_RogoBot Locomotor node (no full rebuild).
Edit the CONFIG below, run via rcpy, then restart PIE to test:
  python C:/Users/tesse/rcpy.py i:/Projects/Unreal/RogosMobile/Tools/Rig/tune_gait.py
Bake the final values into build_rig.py once they feel right.

LEG/FootSet index order (from build_rig.py): 0=FL 1=FR 2=BL 3=BR.
StaticLocalOffset is in the ANKLE BONE's local space (skewed by the imported
skeleton's -90 yaw + scale) -- derive the spread axis empirically: set one foot,
see which way it moves in PIE, then mirror to the others.
"""
import unreal

# ============================ CONFIG ============================
MOVEMENT = {
    "MinimumStepLength": 20.0,   # was 8 -> deliberate steps, not micro-shuffle
    "SpeedMax":          200.0,  # 160->200: headroom so the pelvis keeps up
    "Acceleration":      800.0,  # 100->800: gait speed ramps fast enough through wander turns
    "Deceleration":      400.0,
}
STEPPING = {
    "StepHeight":           14.0,   # was unset/6 -> clear foot lift (kills drag)
    "PercentOfStrideInAir": 0.45,   # was 0.35 -> longer clean swing
    "StepEaseIn":           0.5,
    "StepEaseOut":          0.1,    # crisp plant on landing (sticks -> no slide)
    "MaxCollisionHeight":   45.0,   # was 30 -> feet can reach onto steps/ramp lips
    "OrientFootToGroundPitch": 0.4,
    "OrientFootToGroundRoll":  0.3,
}
PELVIS = {
    "OrientToGroundPitch": 0.3,
    "OrientToGroundRoll":  0.3,
    # tighten the body to the capsule: 0.1 lagged the body ~tens of cm behind at
    # speed AND made the fall look floaty (body trailed the fast-falling capsule).
    "PositionDampingHalfLife": 0.035,   # was 0.1 -> body tracks the capsule snappily
    "LeadAmount":              0.5,     # was 2.0 -> less forward over-anticipation
    "BobOffset":              -10.0,    # was -8 -> a touch more step weight
}
# Per-foot. MaxHeelPeel Z restored (0 made the foot drag flat = slide).
# StaticLocalOffset starts at 0 -> tune for machine spread after slide is fixed.
MAXHEELPEEL = (0.0, 0.0, 40.0)
COLLISION_RADIUS = 28.0
#                  FL              FR              BL              BR
STATIC_OFFSET = {0:(0.0,0.0,0.0), 1:(0.0,0.0,0.0), 2:(0.0,0.0,0.0), 3:(0.0,0.0,0.0)}
# ===============================================================

cr=unreal.EditorAssetLibrary.load_asset("/Game/RogoBot/Anim/CR_RogoBot")
ctrl=cr.get_controller_by_name("RigVMModel")
ln=None
for n in ctrl.get_graph().get_nodes():
    ss=n.get_script_struct() if hasattr(n,"get_script_struct") else None
    if ss and "Locomotor" in ss.get_name(): ln=n; break
NP=ln.get_node_path()
def setp(path, val): ctrl.set_pin_default_value("%s.%s"%(NP,path), str(val))
def vec(t): return "(X=%f,Y=%f,Z=%f)"%(t[0],t[1],t[2])

for k,v in MOVEMENT.items(): setp("Movement.%s"%k, v)
for k,v in STEPPING.items(): setp("Stepping.%s"%k, v)
for k,v in PELVIS.items():   setp("Pelvis.%s"%k, v)
for i in range(4):
    setp("FootSets.%d.Feet.0.MaxHeelPeel"%i, vec(MAXHEELPEEL))
    setp("FootSets.%d.Feet.0.CollisionRadius"%i, COLLISION_RADIUS)
    setp("FootSets.%d.Feet.0.StaticLocalOffset"%i, vec(STATIC_OFFSET[i]))

unreal.EditorAssetLibrary.save_loaded_asset(cr)
print("GAIT TUNED: StepH=%.0f MinStep=%.0f HeelPeelZ=%.0f air=%.2f easeOut=%.2f offsets=%s"%(
    STEPPING["StepHeight"], MOVEMENT["MinimumStepLength"], MAXHEELPEEL[2],
    STEPPING["PercentOfStrideInAir"], STEPPING["StepEaseOut"],
    {k:v for k,v in STATIC_OFFSET.items() if v!=(0.0,0.0,0.0)} or "0"))
