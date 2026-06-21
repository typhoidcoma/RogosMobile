import unreal
ws=unreal.EditorLevelLibrary.get_game_world()
def first(p):
    for a in unreal.GameplayStatics.get_all_actors_of_class(ws, unreal.load_class(None,p)): return a
bot=first("/Game/RogoBot/Character/BP_RogoBot.BP_RogoBot_C")
pc=unreal.GameplayStatics.get_player_controller(ws,0)
cam=pc.get_controlled_pawn() if pc else None
if not bot or not cam:
    print("bot=%s cam=%s"%(bool(bot),bool(cam)))
else:
    b=bot.get_actor_location(); c=cam.get_actor_location()
    v=bot.get_velocity(); spd=(v.x**2+v.y**2+v.z**2)**0.5
    d=((b.x-c.x)**2+(b.y-c.y)**2+(b.z-c.z)**2)**0.5
    # what is the camera's FollowTarget?
    ft=cam.get_editor_property("FollowTarget")
    print("bot=(%d,%d,%d) spd=%d | cam=(%d,%d,%d) | cam-bot=%d | FollowTarget=%s"%(
        b.x,b.y,b.z,spd, c.x,c.y,c.z, d, ft.get_name() if ft else "NULL"))
