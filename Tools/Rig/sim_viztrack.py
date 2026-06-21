import unreal
ws=unreal.EditorLevelLibrary.get_game_world()
bot=next((a for a in unreal.GameplayStatics.get_all_actors_of_class(ws, unreal.load_class(None,"/Game/RogoBot/Character/BP_RogoBot.BP_RogoBot_C"))),None)
if not bot: print("NO PIE BOT"); raise SystemExit
m=bot.get_component_by_class(unreal.SkeletalMeshComponent)
bl=m.get_socket_location("body")
arrow=ring=None
for c in bot.get_components_by_class(unreal.StaticMeshComponent):
    n=c.get_name()
    if "FrontArrow" in n: arrow=c
    elif "SenseRing" in n: ring=c
aw=arrow.get_world_location(); rw=ring.get_world_location()
print("body(%.0f,%.0f,%.0f) | arrow(%.0f,%.0f,%.0f) dXYfromBody=(%.0f,%.0f,%.0f) | ring(%.0f,%.0f,%.0f) dXY=(%.0f,%.0f)"%(
  bl.x,bl.y,bl.z, aw.x,aw.y,aw.z, aw.x-bl.x,aw.y-bl.y,aw.z-bl.z, rw.x,rw.y,rw.z, rw.x-bl.x,rw.y-bl.y))
