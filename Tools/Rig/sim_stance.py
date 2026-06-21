import unreal
ws=unreal.EditorLevelLibrary.get_game_world()
bot=next((a for a in unreal.GameplayStatics.get_all_actors_of_class(ws, unreal.load_class(None,"/Game/RogoBot/Character/BP_RogoBot.BP_RogoBot_C"))),None) if ws else None
if not bot: print("NO PIE BOT"); raise SystemExit
m=bot.get_component_by_class(unreal.SkeletalMeshComponent)
bt=m.get_socket_transform("body", unreal.RelativeTransformSpace.RTS_WORLD)
# clean unit-scale frame from body translation+rotation (skeleton bones carry scale=100)
clean=unreal.Transform(bt.translation, bt.rotation.rotator(), unreal.Vector(1,1,1))
def f(L):
    t=m.get_socket_transform("ankle_"+L, unreal.RelativeTransformSpace.RTS_WORLD)
    p=clean.inverse_transform_location(t.translation)
    return "%s(%.0f,%.0f,%.0f)"%(L,p.x,p.y,p.z)
print("foot-in-body-frame:", f("FL"), f("FR"), f("BL"), f("BR"))
