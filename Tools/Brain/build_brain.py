"""
RogoBot brain — CODE-DEFINED Behavior Tree generator.

This is the editable "brain". You edit the declarative spec in build_brain()
below, then re-run this file against the live editor:

    python C:/Users/tesse/rcpy.py i:/Projects/Unreal/RogosMobile/Tools/Brain/build_brain.py

It (re)builds the runtime BehaviorTree asset BT_RogoBrain. The generated tree
RUNS in PIE / packaged builds (it is a real UBehaviorTree); it just isn't laid
out in the visual BT editor. Edit here, not there.

Node vocabulary:
    Selector(name, [children])  -> runs children L->R until one SUCCEEDS  (priority / fallback)
    Sequence(name, [children])  -> runs children L->R until one FAILS     (do-all-in-order)
    MoveTo(key, radius)         -> move the pawn to a Blackboard vector/actor key
    BPTask(class_path, name)    -> run a custom Blueprint BTTask (added in later phases)
    When(key, is_set=True)      -> Blackboard decorator gating a child (only run if key set/true)

Blackboard keys available (see BB_RogoBrain): SafeZoneLocation, NudgeTarget,
HasNudge, IsThreatened, HazardLocation, PerceivedHazard, SelfActor.
"""
import unreal

BT_PATH = "/Game/RogoBot/AI/BT_RogoBrain"

# ============================================================================
# ============================  EDIT YOUR BRAIN  =============================
# ============================================================================
def build_brain():
    return Selector("Root", [
        # FLEE: top priority — if a hazard is in sight, run to the flee point.
        Sequence("FLEE", [
            When("IsThreatened"),
            MoveTo(key="FleeLocation", radius=50.0),
        ]),
        # NUDGE: net influence from all Attract/Repel sources (boxes + dropped
        # lures) is fused in BP_RogoBot.SenseInfluence into HasNudge/NudgeTarget.
        Sequence("NUDGE", [
            When("HasNudge"),
            MoveTo(key="NudgeTarget", radius=60.0),
        ]),
        # SEEK-SAFE: default — head to the level's safe zone.
        Sequence("SEEK-SAFE", [
            MoveTo(key="SafeZoneLocation", radius=80.0),
        ]),
    ])
# ============================================================================
# ==========================  END EDIT (machinery below)  ====================
# ============================================================================


# ---- declarative descriptors (plain data) ----
class Selector:
    def __init__(self, name, children): self.name, self.children = name, children
class Sequence:
    def __init__(self, name, children): self.name, self.children = name, children
class MoveTo:
    def __init__(self, key, radius=50.0): self.key, self.radius = key, radius
class BPTask:
    def __init__(self, class_path, name=None): self.class_path, self.name = class_path, (name or class_path.split('.')[-1])
class When:
    """Blackboard decorator: gate a child on a key being set / true."""
    def __init__(self, key, is_set=True): self.key, self.is_set = key, is_set


# ---- compiler: descriptors -> runtime UBehaviorTree nodes ----
def _key_sel(name):
    ks = unreal.BlackboardKeySelector()
    ks.set_editor_property("selected_key_name", name)
    return ks

def _radius(value):
    r = unreal.ValueOrBBKey_Float()
    try: r.set_editor_property("default_value", float(value))
    except Exception: pass
    return r

def _compile(node, bt):
    """Return (kind, uobject, decorators) where kind is 'composite' or 'task'.
    `decorators` are When() gates that the PARENT attaches to this node's link."""
    if isinstance(node, (Selector, Sequence)):
        cls = unreal.BTComposite_Selector if isinstance(node, Selector) else unreal.BTComposite_Sequence
        comp = unreal.new_object(cls, bt)
        comp.set_editor_property("node_name", node.name)
        # leading/any When() entries decorate THIS composite; rest are children
        my_decos = [c for c in node.children if isinstance(c, When)]
        real_children = [c for c in node.children if not isinstance(c, When)]
        children = []
        for ch in real_children:
            kind, obj, child_decos = _compile(ch, bt)
            cc = unreal.BTCompositeChild()
            if kind == 'composite': cc.set_editor_property("child_composite", obj)
            else: cc.set_editor_property("child_task", obj)
            if child_decos:
                cc.set_editor_property("decorators", [_compile_deco(d, bt) for d in child_decos])
            children.append(cc)
        comp.set_editor_property("children", children)
        return ('composite', comp, my_decos)
    if isinstance(node, MoveTo):
        t = unreal.new_object(unreal.BTTask_MoveTo, bt)
        t.set_editor_property("node_name", "MoveTo " + node.key)
        t.set_editor_property("blackboard_key", _key_sel(node.key))
        try: t.set_editor_property("acceptable_radius", _radius(node.radius))
        except Exception as e: unreal.log_warning("radius set failed: %s" % e)
        return ('task', t, [])
    if isinstance(node, BPTask):
        cls = unreal.load_class(None, node.class_path)
        t = unreal.new_object(cls, bt)
        t.set_editor_property("node_name", node.name)
        return ('task', t, getattr(node, 'decos', []))
    raise Exception("unknown node: %r" % node)

def _compile_deco(deco, bt):
    if isinstance(deco, When):
        d = unreal.new_object(unreal.BTDecorator_Blackboard, bt)
        d.set_editor_property("blackboard_key", _key_sel(deco.key))
        # 0 = IsSet, 1 = IsNotSet  (UBTDecorator_Blackboard.key_query)
        d.set_editor_property("notify_observer", unreal.BTBlackboardRestart.RESULT_CHANGE)
        try:
            d.set_editor_property("key_query", unreal.BlackboardKeyOperation.SET if deco.is_set
                                  else unreal.BlackboardKeyOperation.NOT_SET)
        except Exception:
            pass
        d.set_editor_property("node_name", ("if " if deco.is_set else "if not ") + deco.key)
        return d
    raise Exception("unknown decorator: %r" % deco)

# helper so When(...) can wrap a child via When(key)(child) — see usage in later phases
class _Decorated:
    def __init__(self, deco, child): self.deco, self.child = deco, child
def _when_call(self, child): return _Decorated(self, child)
When.__call__ = _when_call


def main():
    EAL = unreal.EditorAssetLibrary
    bt = EAL.load_asset(BT_PATH)
    if bt is None:
        unreal.log_error("BT not found: " + BT_PATH); return
    root_spec = build_brain()
    kind, root, _ = _compile(root_spec, bt)
    bt.set_editor_property("root_node", root)
    EAL.save_loaded_asset(bt)
    # report
    def dump(n, depth=0):
        nm = n.get_editor_property("node_name")
        unreal.log("  " * depth + "- " + str(nm))
        if hasattr(n, 'get_editor_property'):
            try:
                for cc in n.get_editor_property("children"):
                    c = cc.get_editor_property("child_composite") or cc.get_editor_property("child_task")
                    dump(c, depth + 1)
            except Exception: pass
    unreal.log("BT rebuilt:")
    dump(root)
    unreal.log("DONE build_brain")

main()
