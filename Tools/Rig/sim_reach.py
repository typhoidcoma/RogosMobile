import unreal
ws=unreal.EditorLevelLibrary.get_game_world()
def first(p):
    for a in unreal.GameplayStatics.get_all_actors_of_class(ws, unreal.load_class(None,p)): return a
bot=first("/Game/RogoBot/Character/BP_RogoBot.BP_RogoBot_C")
sz=first("/Game/RogoBot/Gameplay/BP_SafeZone.BP_SafeZone_C")
if bot and sz:
    b=bot.get_actor_location(); s=sz.get_actor_location()
    d=((b.x-s.x)**2+(b.y-s.y)**2)**0.5
    v=bot.get_velocity(); spd=(v.x**2+v.y**2)**0.5
    print("bot=(%.0f,%.0f,%.0f) spd=%.0f | dist-to-safezone=%.0f"%(b.x,b.y,b.z,spd,d))
else: print("bot=%s sz=%s"%(bool(bot),bool(sz)))
