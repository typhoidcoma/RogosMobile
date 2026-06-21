import unreal
ws=unreal.EditorLevelLibrary.get_game_world()
def first(p):
    for a in unreal.GameplayStatics.get_all_actors_of_class(ws, unreal.load_class(None,p)): return a
bot=first("/Game/RogoBot/Character/BP_RogoBot.BP_RogoBot_C")
sz=first("/Game/RogoBot/Gameplay/BP_SafeZone.BP_SafeZone_C")
if bot and sz:
    b=bot.get_actor_location(); s=sz.get_actor_location(); v=bot.get_velocity()
    d=((b.x-s.x)**2+(b.y-s.y)**2)**0.5
    print("bot=(%d,%d,%d) spd=%d | dist-to-safe=%d"%(b.x,b.y,b.z,(v.x**2+v.y**2)**0.5,d))
