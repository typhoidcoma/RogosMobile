import unreal
ws=unreal.EditorLevelLibrary.get_game_world()
gm=unreal.GameplayStatics.get_game_mode(ws)
pc=unreal.GameplayStatics.get_player_controller(ws,0)
pawn=pc.get_controlled_pawn() if pc else None
bot=None
for a in unreal.GameplayStatics.get_all_actors_of_class(ws, unreal.load_class(None,"/Game/RogoBot/Character/BP_RogoBot.BP_RogoBot_C")): bot=a;break
print("GameMode:", gm.get_class().get_name() if gm else None)
print("Controller:", pc.get_class().get_name() if pc else None)
print("Possessed pawn:", pawn.get_class().get_name() if pawn else None)
if pawn and bot:
    p=pawn.get_actor_location(); b=bot.get_actor_location()
    d=((p.x-b.x)**2+(p.y-b.y)**2+(p.z-b.z)**2)**0.5
    print("cam=(%.0f,%.0f,%.0f) bot=(%.0f,%.0f,%.0f) | cam-bot dist=%.0f"%(p.x,p.y,p.z,b.x,b.y,b.z,d))
